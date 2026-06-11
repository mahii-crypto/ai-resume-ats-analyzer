from django.urls import path
from ..views.user import register

urlpatterns = [
    path('', register),  # POST /api/user/
]
