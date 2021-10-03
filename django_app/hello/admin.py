from django.contrib import admin
from .models import Friend
from .models import Message

admin.site.register(Friend)
admin.site.register(Message)
