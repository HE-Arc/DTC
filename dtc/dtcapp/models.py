from django.db import models

# Create your models here.


class LikedClip(models.Model):
    clipURL = models.CharField(max_length=250)

    def __str__(self):
        return self.clipURL


class Streamer(models.Model):
    name = models.CharField(max_length=50)
    image = models.CharField(max_length=250)

    def __str__(self):
        return self.name + " " + str(self.image)


class User(models.Model):
    username = models.CharField(max_length=100)
    # voir ici pour mdp plus tard : https://stackoverflow.com/questions/17523263/how-to-create-password-field-in-model-django
    password = models.CharField(max_length=50)
    Likes = models.ManyToManyField(LikedClip)
    Follows = models.ManyToManyField(Streamer)
    Subscriptions = models.ManyToManyField('self')

    def __str__(self):
        return self.username
