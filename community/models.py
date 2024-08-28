from django.db import models

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

from authentications.models import CustomUser

# Create your models here.

# Topluluk sayfası ile ilgili model -> CommunityPage
class CommunityPage(models.Model):
    """
    Topluluk sayfasını belirten modeldir.
    """

    community_title = models.CharField(max_length=100)
    id_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, null=True, blank=True)
    community_access_code = models.CharField(max_length=100, null=True, blank=True)
    info = models.TextField(max_length=500)
    terms = models.TextField(max_length=1000)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_communities')
    admins = models.ManyToManyField(CustomUser, related_name='administered_communities')
    subscribers = models.ManyToManyField(CustomUser, related_name='subscribed_communities')
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    profilephoto = models.ImageField(upload_to='images/' , default="images/default_community_pp.png" , blank=True)
    backgroundphoto = models.ImageField(upload_to='images/' , default="images/default_community_background.png" , blank=True)
   
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.id_name)
        super().save(*args, **kwargs)

    def get_subscriber_count(self):
        return self.subscribers.count()
    
    def get_post_count(self):
        # Bu topluluğa bağlı postları sayar
        return CommunityPost.objects.filter(post_community=self).count()
    
class CommunityPost(models.Model):
    """
    Postları belirten modeldir.
    """

    post_creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_creators' , null=True)
    post_created = models.DateTimeField(default=timezone.now)
    post_content = models.TextField(max_length=1000)
    post_community = models.ForeignKey(CommunityPage, on_delete=models.CASCADE, default=7)  # Varsayılan topluluk -> Announcements

    """ Diğer özelliklere sahip postlar eklenir. """
    post_link = models.CharField(max_length=300, null=True, blank=True)

    post_type = models.CharField(max_length=50 , null=True , blank=True )

    likes = models.ManyToManyField(CustomUser, through='PostLike', related_name='liked_posts', blank=True)
    comments = models.ManyToManyField(CustomUser, through='PostComment', related_name='commented_posts', blank=True)

    def get_like_count(self):
        return self.likes.count()
    
    def get_comment_count(self):
        return self.comments.count()

class AssignmentPost(CommunityPost):

    """ Assignment Post Özellikleri """

    assignment_header = models.CharField(max_length=200)    # Ödevin Başlığı
    assignment_duedate = models.DateTimeField()   # Ödev Teslim Tarihi
    assignment_file = models.FileField(upload_to='assignments/')    # Ödevde Paylaşılan Dosya
    slug = models.SlugField(unique=True, blank=True, null=True)  # Eklenen alan: Slug

    def __str__(self):
        return f"{self.post_creator} (Due: {self.assignment_duedate})"

class StudentAssignment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assignment = models.ForeignKey(AssignmentPost, on_delete=models.CASCADE)
    submitted_file = models.FileField(upload_to='submitted_assignments/')
    submission_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student} - {self.assignment.assignment_header}"
    
class PostLike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='post_likes', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class PostComment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='post_comments', null=True, blank=True)
    content = models.TextField(max_length=1000, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

@receiver(pre_delete, sender=CommunityPage)
def delete_community_images(sender, instance, **kwargs):
    if instance.profilephoto and instance.profilephoto.name != "images/default_community_pp.png":
        instance.profilephoto.delete(save=False)
    if instance.backgroundphoto and instance.backgroundphoto.name != "images/default_community_background.png":
        instance.backgroundphoto.delete(save=False)

@receiver(pre_delete, sender=AssignmentPost)
def delete_assignment_file(sender, instance, **kwargs):
    if instance.assignment_file:
        instance.assignment_file.delete(save=False)

@receiver(pre_delete, sender=StudentAssignment)
def delete_submitted_file(sender, instance, **kwargs):
    if instance.submitted_file:
        instance.submitted_file.delete(save=False)