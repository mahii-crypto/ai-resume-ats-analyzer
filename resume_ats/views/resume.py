import os
import re
import requests
import tempfile

import pdfplumber
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings

from ..models import Resume
from ..serializers import ResumeSerializer


def _call_cohere_chat(model: str, message: str, chat_history: list = None, preamble: str = None) -> dict:
    """Helper: call Cohere v1/chat endpoint."""
    payload = {
        'model': model,
        'message': message,
        'temperature': 0.7,
    }
    if chat_history:
        payload['chat_history'] = chat_history
    if preamble:
        payload['preamble'] = preamble

    response = requests.post(
        'https://api.cohere.com/v1/chat',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.CO_API_KEY}',
        },
        timeout=60,
    )
    return response.json()


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_resume(request):
    """
    Upload a PDF resume, analyze it against the job description via Cohere,
    save the result, and return the analysis.
    Mirrors: Controllers/resume.js -> exports.addResume
    """
    job_desc = request.data.get('job_desc')
    user = request.data.get('user', 'guest')
    resume_file = request.FILES.get('resume')

    if not resume_file:
        return Response({'message': 'Resume file not uploaded'}, status=status.HTTP_400_BAD_REQUEST)

    if not job_desc:
        return Response({'message': 'Job description required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Save uploaded file to a temp location, extract text with pdfplumber
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            for chunk in resume_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            with pdfplumber.open(tmp_path) as pdf:
                pdf_text = '\n'.join(
                    page.extract_text() or '' for page in pdf.pages
                )
        finally:
            os.unlink(tmp_path)

        print('PDF Extracted Successfully')

        prompt = f"""You are an ATS Resume Analyzer.

Compare the following resume with the job description.

Return only in this exact format:

Score: XX
Reason: Your explanation

Resume:
{pdf_text}

Job Description:
{job_desc}
"""

        data = _call_cohere_chat(model='command-a-03-2025', message=prompt)
        print('RAW RESPONSE:', data)

        if 'message' in data and 'text' not in data:
            return Response({'error': data['message']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        result = data.get('text', '')
        if not result:
            content = data.get('message', {}).get('content', [])
            result = content[0].get('text', '') if content else ''

        if not result:
            raise ValueError('No response from AI')

        print('AI RESULT:', result)

        score_match = re.search(r'Score:\s*(\d+)', result, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else 0

        reason_match = re.search(r'Reason:\s*([\s\S]*)', result, re.IGNORECASE)
        reason = reason_match.group(1).strip() if reason_match else 'No feedback available'

        new_resume = Resume.objects.create(
            user=user,
            resume_name=resume_file.name,
            job_desc=job_desc,
            score=str(score),
            feedback=reason,
        )

        serializer = ResumeSerializer(new_resume)
        return Response(
            {'message': 'Analysis completed successfully', 'data': serializer.data},
            status=status.HTTP_200_OK
        )

    except Exception as err:
        print('FULL ERROR:', err)
        return Response(
            {'error': 'Server Error', 'message': str(err)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_resume_for_user(request, user):
    """
    Return all resumes for a given user (ordered newest first).
    Mirrors: Controllers/resume.js -> exports.getAllResumeForUser
    """
    try:
        resumes = Resume.objects.filter(user=user).order_by('-created_at')
        serializer = ResumeSerializer(resumes, many=True)
        return Response({'message': 'Your Previous History', 'resume': serializer.data})
    except Exception as err:
        print('FULL ERROR:', err)
        return Response(
            {'error': 'Server Error', 'message': str(err)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_all_resumes_admin(request):
    """
    Return all resumes for admin view.
    Mirrors: Controllers/resume.js -> exports.getAllResumeForAdmin
    """
    try:
        resumes = Resume.objects.all().order_by('-created_at')
        serializer = ResumeSerializer(resumes, many=True)
        return Response({'message': 'Fetched All User History', 'resume': serializer.data})
    except Exception as err:
        print('FULL ERROR:', err)
        return Response(
            {'error': 'Server Error', 'message': str(err)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
