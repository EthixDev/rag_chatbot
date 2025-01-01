from django.urls import path
from app.views import generate_response, topic_view, index, DocumentUpload, delete_topic

urlpatterns = [
    path('', generate_response, name='generate_response'),  # Root path for the app
    path('<int:id>/', topic_view, name='topic_view'),
    path('chunk', index, name='index'),
    path('api/upload_document/', DocumentUpload.as_view(), name='api_upload_document'),
    path('delete-topic/', delete_topic, name='delete_topic'),


]
