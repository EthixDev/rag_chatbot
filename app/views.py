from django.shortcuts import render, get_object_or_404
from RAG.embedding_gen import embed_text
from RAG.read_chunking import chunk_text
from app.models import Document, Conversation, TextChunk, Topic
from pgvector.django import CosineDistance
from dotenv import load_dotenv
import google.generativeai as genai
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.serializers import TopicSerializer, ConversationSerializer, DocumentSerializer
from rest_framework.parsers import MultiPartParser, FormParser


load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY is not set. Please set the environment variable."
    )

genai.configure(api_key=api_key)

def generate_response_with_gemini(user_question, relevant_text_chunks, conversations):
    prompt = (
        f"AI Assistant: Based on the provided information and previous conversations:\n"
        f"User Question: {user_question}\n"
        f"Relevant Text Chunks: {relevant_text_chunks}\n"
        f"Conversation History: {conversations}\n"
        f"Please provide a short, concise, and fact-based answer to the user's question.\n"
        f"Answer: "
    )

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)

        return response.text
    except Exception as e:
        raise ValueError(f"Error generating response with Gemini: {e}")
    
def render_ui(request):
    return render(request, 'app/UI.html')

class TopicListCreateView(APIView):
    def get(self, request):
        topics = Topic.objects.all()
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopicDeleteView(APIView):
    def delete(self, request, topic_id):
        try:
            topic = get_object_or_404(Topic, id=topic_id)
            topic.delete()
            return Response({"message": "Topic deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)


class ConversationListView(APIView):
    def get(self, request, topic_id):
        conversations = Conversation.objects.filter(topic_id=topic_id)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

class GenerateResponseView(APIView):
    def post(self, request, id=None):
        topic = get_object_or_404(Topic, id=id) if id else None
        user_question = request.data.get("input_text")

        # Fetch the associated document
        if topic:
            selected_document_path = topic.document.file.name if topic.document and topic.document.file else None
        else:
            selected_document_path = request.data.get("document")

        selected_document = None
        if selected_document_path:
            try:
                selected_document = Document.objects.get(file=selected_document_path)
            except Document.DoesNotExist:
                return Response({"error": "Selected document is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate the embedded question
        embedded_question = embed_text([user_question])[0]

        # Find the most relevant text chunks
        similar_chunks = (
            TextChunk.objects.filter(document=selected_document)
            if selected_document
            else TextChunk.objects.all()
        ).annotate(
            similarity=CosineDistance("embedding", embedded_question)
        ).order_by("similarity")[:3]

        relevant_text_chunks = " ".join([chunk.chunk for chunk in similar_chunks])

        # Fetch conversation history
        history = []
        if topic:
            conversations = Conversation.objects.filter(topic=topic)
            for conv in conversations:
                formatted_question = f"Question: {conv.question}"
                formatted_answer = f"Answer: {conv.answer}"
                history.append(f"{formatted_question}, {formatted_answer}")
        else:
            history = None

        # Generate response using Gemini
        response = generate_response_with_gemini(
            user_question, relevant_text_chunks, conversations=history
        )

        # Save the conversation and topic
        if not topic:
            topic = Topic.objects.create(title=user_question, document=selected_document)

        # Create a new Conversation regardless of topic existence
        Conversation.objects.create(
            topic=topic, question=user_question, answer=response
        )

        return Response({"answer": response, "topic_id": topic.id})

class DocumentUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve all available documents.
        """
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(file=request.FILES["file"])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FetchDocumentsView(APIView):
    def get(self, request):
        """
        API to fetch all available documents for selection.
        """
        documents = Document.objects.all()
        data = [{"file": doc.file.name, "title": doc.title} for doc in documents]
        return Response(data, status=status.HTTP_200_OK)


def similarity_search(request):
    context = {}
    if request.method == "POST":
        input_text = request.POST.get("input_text")
        if input_text:
            try:
                text_chunks = chunk_text(input_text)
                embeddings = [embed_text(chunk) for chunk in text_chunks]

                # Find the most similar chunk for the first embedding
                similar_chunk = None
                corresponding_document = None
                if embeddings:
                    embedding = embeddings[0]
                    similar_chunk = TextChunk.objects.order_by(
                        CosineDistance('embedding', embedding)).first()
                    
                    if similar_chunk:
                        corresponding_document = similar_chunk.document
                
                context = {
                    'input_text': input_text,
                    'text_chunks': text_chunks,
                    'most_similar': similar_chunk.chunk if similar_chunk else "No similar chunk found.",
                    'corresponding_document': corresponding_document.file.name if corresponding_document else "No corresponding document found.",
                }
            except Exception as e:
                context = {'error': str(e)}

    return render(request, 'app/index.html', context)