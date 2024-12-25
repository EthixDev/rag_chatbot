from django.shortcuts import render, redirect, get_object_or_404
from RAG.embed_text import embed_text
from RAG.similarity import cosine_similarity
from dotenv import load_dotenv
from app.models import Conversation, Document, TextChunk, Topic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from django.contrib.auth.decorators import login_required
import os


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY is not set. Please set the environment variable.")

chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.2, openai_api_key=api_key)


# chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.2)


def generate_response_with_gpt_turbo(user_question, relevant_text_chunk, conversations):
    prompt = (
        f"AI Language Model Assistant, based on the provided information and conversations:\n"
        f"User Question: '+ \n {conversations} \n {user_question}'\n"
        f"Relevant Text Chunk: '{relevant_text_chunk}'\n"
        f"Please provide a short, concise and fact-based answer to the user's question:\n"
        f"Answer: "
    )

    # Implement the GPT-3.5 Turbo API call to generate a response
    response = chat.invoke(
        [
            HumanMessage(content=prompt),
        ]
    )
    return response


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
            pdf_file__icontains=selected_document_name
        ).first()

        if selected_document:
            embeded_question = embed_text([user_question])[0]
            best_text_chunks = []
            chunks = TextChunk.objects.filter(document=selected_document)

            for text_chunk in chunks:
                similarity = cosine_similarity(embeded_question, text_chunk.embed)

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

            best_text_chunks = [chunk for _, chunk in best_text_chunks]
            total_text = "".join(best_text_chunks)

            history = []
            if conversations is not None:
                for conv in conversations:
                    answer = 'quetion: ' + conv.answer
                    question ='answer: ' + conv.question
                    add_two = answer + ', ' + question
                    history.append(add_two)
            else:
                None

            response = generate_response_with_gpt_turbo(
                user_question, total_text, conversations=history
            )

            if not topic:
                topic = Topic.objects.create(title=user_question)
            Conversation.objects.create(
                topic=topic, question=user_question, answer=response.content
            )   

            return redirect("topic_view", topic.id if topic else None)

    documents = Document.objects.all()
    topics = Topic.objects.all()
    conversations = Conversation.objects.filter(topic_id=id) if id else None

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
