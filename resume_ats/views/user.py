from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import User
from ..serializers import UserSerializer


@api_view(['POST'])
def register(request):
    """
    Register or retrieve a Firebase-authenticated user.
    Mirrors: Controllers/user.js -> exports.register
    """
    name = request.data.get('name')
    email = request.data.get('email')
    photo_url = request.data.get('photoUrl')  # camelCase from frontend

    if not name or not email:
        return Response(
            {'error': 'Bad request', 'message': 'Name and email are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'name': name, 'photo_url': photo_url}
        )

        serializer = UserSerializer(user)

        if created:
            return Response(
                {'message': 'User Registered Successfully 👍', 'user': serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {'message': 'Welcome Back', 'user': serializer.data},
            status=status.HTTP_200_OK
        )

    except Exception as err:
        print(f'User registration failed: {err}')
        return Response(
            {'error': 'Server-error', 'message': str(err)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
