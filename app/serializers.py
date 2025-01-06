from rest_framework import serializers
from .models import Document,Topic, Conversation

class DocumentSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    class Meta:
        model = Document
        fields = ['id', 'file','file_name', 'title', 'created_at', 'updated_at']

    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError("No file uploaded.")
        return value
    def get_file_name(self, obj):
        return obj.file.name.split('/')[-2] +'/' + obj.file.name.split('/')[-1] if obj.file else None
    
class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'title', 'created_at', 'updated_at']


class ConversationSerializer(serializers.ModelSerializer):
    topic_title = serializers.CharField(source='topic.title', read_only=True)  # Optional: Include topic title in conversation details

    class Meta:
        model = Conversation
        fields = ['id', 'topic', 'topic_title', 'question', 'answer', 'created_at']