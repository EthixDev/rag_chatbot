from django.urls import path
from app.views import (
    TopicListCreateView,
    TopicDeleteView,
    ConversationListView,
    GenerateResponseView,
    DocumentUploadView,
    render_main_page,
)

urlpatterns = [
    # API for managing topics
    path('', render_main_page, name='main_page'),  # Root URL for rendering the HTML page

    path('api/topics/', TopicListCreateView.as_view(), name='api_topics'),  # List/Create topics
    path('api/topics/<int:topic_id>/', TopicDeleteView.as_view(), name='api_delete_topic'),  # Delete a topic

    # API for fetching conversations
    path('api/conversations/<int:topic_id>/', ConversationListView.as_view(), name='api_conversations'),  # Fetch conversations for a topic

    # API for generating a chatbot response
    path('api/generate-response/', GenerateResponseView.as_view(), name='api_generate_response'),
    path('api/generate-response/<int:id>/', GenerateResponseView.as_view(), name='api_generate_response_with_id'),


    # API for uploading documents
    path('api/upload-document/', DocumentUploadView.as_view(), name='api_upload_document'),
]
