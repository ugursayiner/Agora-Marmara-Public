from django.urls import path
from . import views

urlpatterns = [
    path('' , views.open_frontpage , name='featuredpages_frontpage_name'),
    path('frontpage/' , views.open_frontpage)
]

