import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


@api_view(['POST'])
def chat(request):
    """
    Proxy chat messages to Cohere's v1/chat endpoint.
    Mirrors: Controllers/ChatBot.js -> exports.chat
    """
    messages = request.data.get('messages')
    system = request.data.get('system')

    co_key = settings.CO_API_KEY
    print('CO KEY:', '✅ Found' if co_key else '❌ Missing')

    if not messages or not isinstance(messages, list):
        return Response({'error': 'messages array required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Build Cohere chat_history from all messages except the last
        chat_history = [
            {
                'role': 'USER' if msg['role'] == 'user' else 'CHATBOT',
                'message': msg['content'],
            }
            for msg in messages[:-1]
        ]

        last_message = messages[-1]['content']

        payload = {
            'model': 'command-r-plus-08-2024',
            'message': last_message,
            'chat_history': chat_history,
        }
        if system:
            payload['preamble'] = system

        response = requests.post(
            'https://api.cohere.com/v1/chat',
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {co_key}',
            },
            timeout=60,
        )

        data = response.json()

        if 'message' in data and 'text' not in data:
            print('Cohere error:', data['message'])
            return Response({'error': data['message']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        reply = data.get('text', 'Sorry, no response.')
        return Response({'content': [{'text': reply}]})

    except Exception as err:
        print('Chat error:', str(err))
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
