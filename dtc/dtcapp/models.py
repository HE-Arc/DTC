from django.db import models

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import UserManager

# Create your models here.
class LikedClip(models.Model):
    clipURL = models.CharField(max_length=250)
    id_clip = models.CharField(max_length=30)

    def __str__(self):
        return self.clipURL


class Streamer(models.Model):
    name = models.CharField(max_length=50)
    image = models.CharField(max_length=250)
    id_streamer = models.CharField(max_length=30)

    def __str__(self):
        return self.name + " " + str(self.image)


class User(AbstractBaseUser):
    username = models.CharField(max_length=100,unique=True)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=100)
    pictureURL = models.CharField(max_length=250)
    id_twitch = models.CharField(max_length=30)
    # voir ici pour mdp plus tard : https://stackoverflow.com/questions/17523263/how-to-create-password-field-in-model-django
    #password = models.CharField(max_length=50)
    Likes = models.ManyToManyField(LikedClip)
    Follows = models.ManyToManyField(Streamer,through='Following')
    Subscriptions = models.ManyToManyField('self')

    objects = UserManager()

    USERNAME_FIELD='username'
    REQUIRED_FIELDS=['password','email','pictureURL','id_twitch']

    def __str__(self):
        return self.username


class Following(models.Model):
    streamer = models.ForeignKey(Streamer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activated = models.BooleanField(default=True)