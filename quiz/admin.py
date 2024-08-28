from django.contrib import admin

from .models import Exam, ExamSubmission

# Register your models here.
admin.site.register(Exam)
admin.site.register(ExamSubmission)