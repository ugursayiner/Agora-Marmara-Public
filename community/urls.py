from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('feed/' , views.open_feed , name='community_feed_name'),
    path('user/<str:username>/' , views.open_profile , name='community_profile_name'),
    path('community/', views.open_groups , name='community_groups_name'),
    path('community/<slug:slug>/', views.open_community , name='community_opencommunity_name'),
    path('community/<slug:slug>/members/', views.open_allmembers , name='community_openallmembers_name'),
    path('community/<slug:slug>/settings/', views.open_communitysettings , name='community_opencommunitysettings_name'),
    path('community/<slug:community_slug>/post/<slug:slug>/', views.open_postdetail , name='community_postdetail_name'),
    path('settings/', views.open_settings , name='community_settings_name'),
    path('create-a-community/', views.create_group , name="community_createcommunity_name"),
    path('search/', views.open_searchresults , name="community_searchresults_name"),
    path('download-submission/<int:submission_id>/', views.download_submission, name='download_submission'),
    path('download-assignment/<int:assignment_id>/', views.download_assignment, name='download_assignment'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('deletepost/<int:post_id>/', views.deletepost, name='deletepost'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)