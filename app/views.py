from django.shortcuts import render, redirect, get_object_or_404
from RAG.embedding_gen import embed_text
from RAG.similarity import cosine_similarity
from dotenv import load_dotenv
from app.models import Conversation, Document, TextChunk, Topic
import google.generativeai as genai
from django.contrib.auth.decorators import login_required
import os

# Load environment variables
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY is not set. Please set the environment variable."
    )

# Configure the API
genai.configure(api_key=api_key)


# Generate response using Gemini
def generate_response_with_gemini(user_question, relevant_text_chunk, conversations):
    prompt = (
        f"AI Assistant: Based on the provided information and previous conversations:\n"
        f"User Question: {user_question}\n"
        f"Relevant Text Chunk: {relevant_text_chunk}\n"
        f"Conversation History: {conversations}\n"
        f"Please provide a short, concise, and fact-based answer to the user's question.\n"
        f"Answer: "
    )

    try:
        # Use Gemini to generate a response
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)

        return response.text
    except Exception as e:
        raise ValueError(f"Error generating response with Gemini: {e}")


def process_question(request, id=None):
    if id:
        topic = get_object_or_404(Topic, id=id)
        conversations = Conversation.objects.filter(topic=topic)
    else:
        topic = None
        conversations = None

    documents = Document.objects.all()
    topics = Topic.objects.all()

    if request.method == "POST":
        user_question = request.POST.get("input_text")
        selected_document_name = request.POST.get("document", "")
        selected_document = Document.objects.filter(
            file__icontains=selected_document_name
        ).first()

        if selected_document:
            # Generate embedding for the user question using Gemini
            embeded_question = embed_text([user_question])[0]
            best_text_chunks = []
            chunks = TextChunk.objects.filter(document=selected_document)

            for text_chunk in chunks:
                # Calculate similarity between question embedding and text chunks
                similarity = cosine_similarity(embeded_question, text_chunk.embedding)

                if len(best_text_chunks) < 3:
                    best_text_chunks.append((similarity, text_chunk.chunk))
                else:
                    min_similarity_index = min(
                        range(3), key=lambda i: best_text_chunks[i][0]
                    )
                    if similarity > best_text_chunks[min_similarity_index][0]:
                        best_text_chunks[min_similarity_index] = (
                            similarity,
                            text_chunk.chunk,
                        )

            # Combine best matching text chunks
            best_text_chunks = [chunk for _, chunk in best_text_chunks]
            total_text = "".join(best_text_chunks)

            # Prepare conversation history
            history = []
            if conversations is not None:
                for conv in conversations:
                    formatted_question = f"Question: {conv.question}"
                    formatted_answer = f"Answer: {conv.answer}"
                    history.append(f"{formatted_question}, {formatted_answer}")
            else:
                history = None

            # Generate a response using Gemini
            try:
                response = generate_response_with_gemini(
                    user_question, total_text, conversations=history
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
            "documents": documents,
            "conversations": conversations,
            "topics": topics,
        },
    )


@login_required
def generate_response(request):
    return process_question(request)


def topic_view(request, id):
    return process_question(request, id)
