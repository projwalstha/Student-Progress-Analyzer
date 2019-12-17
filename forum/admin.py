from django.contrib import admin
from forum.models import Forum, thread, Post,Comment
# Register your models here.
admin.site.register(Forum)
admin.site.register(thread)
admin.site.register(Post)
admin.site.register(Comment)
