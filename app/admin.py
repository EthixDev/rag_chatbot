from django.contrib import admin

# Register your models here.

from django.contrib import admin


from .models import Document, TextChunk, Conversation, Topic

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('pdf_file', 'created_at', 'updated_at')
    search_fields = ('pdf_file',)
    readonly_fields = ('created_at', 'updated_at')

class TextChunkAdmin(admin.ModelAdmin):
    list_display = ('chunk', 'embed', 'updated_at')
  

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'created_at')


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')

admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(TextChunk, TextChunkAdmin)
admin.site.register(Topic, TopicAdmin)
