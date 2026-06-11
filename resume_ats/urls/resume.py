from django.urls import path
from ..views.resume import add_resume, get_resume_for_user, get_all_resumes_admin

urlpatterns = [
    path('addResume', add_resume),          # POST /api/resume/addResume
    path('admin/all', get_all_resumes_admin),  # GET  /api/resume/admin/all
    path('<str:user>', get_resume_for_user),   # GET  /api/resume/<user>
]
