from django.contrib import admin
from .models import User, LikedClip, Streamer
# Register your models here.
# python .\manage.py migrate --run-syncdb
admin.site.register(User)
admin.site.register(LikedClip)
admin.site.register(Streamer)
