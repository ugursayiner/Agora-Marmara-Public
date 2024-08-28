from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

from authentications.models import CustomUser
from community.models import CommunityPage

class Exam(models.Model):
    exam_title = models.CharField(max_length=100)
    exam_creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam_community = models.ForeignKey(CommunityPage, on_delete=models.CASCADE)
    exam_start_date = models.DateTimeField()
    exam_end_date = models.DateTimeField()
    question1 = models.TextField()
    question2 = models.TextField()
    question3 = models.TextField()
    question4 = models.TextField()
    question5 = models.TextField()

    slug = models.SlugField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.exam_title)
        super().save(*args, **kwargs)

class ExamSubmission(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    answer1 = models.TextField()
    answer2 = models.TextField()
    answer3 = models.TextField()
    answer4 = models.TextField()
    answer5 = models.TextField()
    exam_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

