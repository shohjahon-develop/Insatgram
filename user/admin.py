from django.contrib import admin
from user.models import User, Post, BaseModel

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
# admin.site.register(BaseModel)