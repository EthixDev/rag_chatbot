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
from django.shortcuts import get_object_or_404
from app.models import Topic, Conversation, Document, TextChunk
from app.serializers import TopicSerializer, ConversationSerializer, DocumentSerializer
from RAG.embedding_gen import embed_text
from pgvector.django import CosineDistance
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
def render_main_page(request):
  
    return render(request, 'app/generate_response.html')
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
    
    def post(self, request,id=None):
        topic = get_object_or_404(Topic, id=id) if id else None
        conversations = (
            Conversation.objects.filter(topic=topic) if topic else None
        )
        user_question = request.data.get("input_text")
        if topic:
            selected_document_path=topic.document.file.name
        else:            
            selected_document_path = request.data.get("document")
        
       

        selected_document = None
        if selected_document_path:
            try:
                selected_document = Document.objects.get(file=selected_document_path)
            except Document.DoesNotExist:
                return Response({"error": "Selected document is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        embeded_question = embed_text([user_question])[0]
        similar_chunks = (
            TextChunk.objects.filter(document=selected_document)
            if selected_document
            else TextChunk.objects.all()
        ).annotate(
            similarity=CosineDistance("embedding", embeded_question)
        ).order_by("similarity")[:3]

        relevant_text_chunks = " ".join([chunk.chunk for chunk in similar_chunks])
        history = []
        if conversations:
            for conv in conversations:
                formatted_question = f"Question: {conv.question}"
                formatted_answer = f"Answer: {conv.answer}"
                history.append(f"{formatted_question}, {formatted_answer}")
        else:
            history = None

        response = generate_response_with_gemini(
            user_question, relevant_text_chunks, conversations=history
        )
        if not topic:
            topic = Topic.objects.create(title=user_question,document=selected_document)
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
