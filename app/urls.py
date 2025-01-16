from django.urls import path
from app.views import (
    TopicListCreateView,
    TopicDeleteView,
    ConversationListView,
    GenerateResponseView,
    DocumentUploadView,
    render_ui,
    FetchDocumentsView,
)


urlpatterns = [
    path('chat/', render_ui, name='render_ui'),
    path('api/topics/', TopicListCreateView.as_view(), name='api_topics'),  # List/Create topics
    path('api/topics/<int:topic_id>/', TopicDeleteView.as_view(), name='api_delete_topic'),  # Delete a topic
    path('api/conversations/<int:topic_id>/', ConversationListView.as_view(), name='api_conversations'),  # Fetch conversations for a topic
    path('api/generate-response/', GenerateResponseView.as_view(), name='api_generate_response'),
    path('api/generate-response/<int:id>/', GenerateResponseView.as_view(), name='api_generate_response_with_id'),
    path('api/upload-document/', DocumentUploadView.as_view(), name='api_upload_document'),
    path('api/fetch-documents/', FetchDocumentsView.as_view(), name='api_fetch_documents'),

]
