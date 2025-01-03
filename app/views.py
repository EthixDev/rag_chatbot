from django.shortcuts import render, redirect, get_object_or_404
from RAG.embedding_gen import embed_text
from RAG.embedding_gen import chunk_text
from app.models import Document, Conversation, TextChunk, Topic
from pgvector.django import CosineDistance
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
import google.generativeai as genai
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DocumentSerializer
import json 
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

def process_question(request, id=None):
    # Fetch topic and conversation history if available
    topic = get_object_or_404(Topic, id=id) if id else None
    conversations = (
        Conversation.objects.filter(topic=topic) if topic else None
    )

    topics = Topic.objects.all()
    documents = Document.objects.all()  # Fetch all documents

    selected_document = None

    if request.method == "POST":
        user_question = request.POST.get("input_text")
        selected_document_path = request.POST.get("document")  # Get file path from the form

        if selected_document_path:
            try:
                # Fetch the document using the file path
                selected_document = Document.objects.get(file=selected_document_path)
            except Document.DoesNotExist:
                return render(
                    request,
                    "app/generate_response.html",
                    {
                        "conversations": conversations,
                        "topics": topics,
                        "documents": documents,
                        "error": "Selected document is invalid.",
                    },
                )

        if user_question:
            # Generate embedding for the user question
            embeded_question = embed_text([user_question])[0]

            # Query top 3 similar text chunks, optionally filter by selected document
            if selected_document:
                similar_chunks = TextChunk.objects.filter(
                    document=selected_document
                ).annotate(
                    similarity=CosineDistance("embedding", embeded_question)
                ).order_by("similarity")[:3]
            else:
                similar_chunks = TextChunk.objects.annotate(
                    similarity=CosineDistance("embedding", embeded_question)
                ).order_by("similarity")[:3]

            # Combine the text of the top 3 similar chunks
            relevant_text_chunks = " ".join([chunk.chunk for chunk in similar_chunks])

            # Prepare conversation history
            history = []
            if conversations:
                for conv in conversations:
                    formatted_question = f"Question: {conv.question}"
                    formatted_answer = f"Answer: {conv.answer}"
                    history.append(f"{formatted_question}, {formatted_answer}")
            else:
                history = None

            # Generate a response using Gemini
            try:
                response = generate_response_with_gemini(
                    user_question, relevant_text_chunks, conversations=history
                )
            except ValueError as e:
                response = str(e)

            if not topic:
                topic = Topic.objects.create(title=user_question)
            Conversation.objects.create(
                topic=topic, question=user_question, answer=response
            )

            return redirect("topic_view", topic.id if topic else None)

    return render(
        request,
        "app/generate_response.html",
        {
            "conversations": conversations,
            "topics": topics,
            "documents": documents,
            "selected_document": selected_document.file.name if selected_document else None,
        },
    )

def generate_response(request):
    return process_question(request)


def topic_view(request, id):
    return process_question(request, id)

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

class DocumentUpload(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = DocumentSerializer(data=request.data)

        # Ensure the file is present in request.FILES
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'errors': {'file': ['No file was uploaded.']}
            }, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save(file=request.FILES['file'])  # Save the document instance with the file
            return Response({
                'success': True,
                'message': 'Document uploaded successfully!',
                'document': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def delete_topic(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic_id = data.get('id')
            topic = get_object_or_404(Topic, id=topic_id)
            topic.delete()
            return JsonResponse({'message': 'Topic deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
