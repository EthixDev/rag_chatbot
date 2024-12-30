from django.urls import  path

from app.views import generate_response,topic_view, index
 
urlpatterns = [
    # path('', generate_prompt, name='generate'),
    path('chat', generate_response, name='generate_response'),
    path('<int:id>/', topic_view, name='topic_view'),
    path('chunk', index, name='index')

] 