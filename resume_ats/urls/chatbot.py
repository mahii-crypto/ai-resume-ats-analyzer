from django.urls import path
from ..views.chatbot import chat

urlpatterns = [
    path('', chat),  # POST /api/chat/
]
