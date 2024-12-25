from django.urls import  path

from app.views import generate_response,topic_view
 
urlpatterns = [
    # path('', generate_prompt, name='generate'),
    path('', generate_response, name='generate_response'),
    path('<int:id>/', topic_view, name='topic_view'),

] 