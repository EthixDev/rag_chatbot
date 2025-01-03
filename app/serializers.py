from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file', 'title', 'created_at', 'updated_at']

    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError("No file uploaded.")
        return value
