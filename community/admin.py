from django.contrib import admin
from .models import CommunityPage, CommunityPost, AssignmentPost, StudentAssignment, PostLike, PostComment

# Register your models here.

admin.site.register(CommunityPage)
admin.site.register(CommunityPost)
admin.site.register(AssignmentPost)
admin.site.register(StudentAssignment)
admin.site.register(PostLike)
admin.site.register(PostComment)