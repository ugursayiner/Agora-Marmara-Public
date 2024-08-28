from django.contrib.auth.models import AbstractUser
from django.db import models

from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Create your models here.

class CustomUser(AbstractUser):
    # Ek özellikler burada tanımlanacak
    usertype = models.CharField(max_length=10, default='', null=True, blank=True)
    userprofilephoto = models.ImageField(upload_to='images/' , default="images/default_user_pp.png" , blank=True)
    userbackgroundphoto = models.ImageField(upload_to='images/' , default="images/default_user_background.jpg" , blank=True)
    userabout = models.TextField(default='', null=True, blank=True)

    def return_usertype(self):
        return self.usertype

@receiver(pre_delete, sender=CustomUser)
def delete_user_photos(sender, instance, **kwargs):
    if instance.userprofilephoto and instance.userprofilephoto.name != "images/default_user_pp.png":
        instance.userprofilephoto.delete(save=False)
    if instance.userbackgroundphoto and instance.userbackgroundphoto.name != "images/default_user_background.jpg":
        instance.userbackgroundphoto.delete(save=False)