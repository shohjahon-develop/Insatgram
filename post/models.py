from django.db import models
from django.contrib.auth import get_user_model
from shared.models import BaseModel
from django.core.validators import FileExtensionValidator,MaxLengthValidator
from django.db.models import UniqueConstraint
User = get_user_model()
# Create your models here.

class Post(BaseModel):
    auther = models.ForeignKey(User,on_delete=models.CASCADE,related_name='post')
    image = models.ImageField(upload_to='post_images',validators=[
        FileExtensionValidator(allowed_extensions=['jpeg','jpg','png'])
    ])
    caption = models.TextField(validators=[MaxLengthValidator(2000)])

    class Meta:
        db_table = 'posts'
        verbose_name = 'post'
        verbose_name_plural = "posts"

    def __str__(self):
        return f"{self.auther} post about {self.caption}"

class PostComment(BaseModel):
    auther = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comment')
    comment = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='child',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.auther} tomonidan komment yozildi"

class PostLike(BaseModel):
    auther = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['auther','post'],
                name='posLikeUnique'
            )
        ]

class CommentLike(BaseModel):
    auther = models.ForeignKey(User,on_delete=models.CASCADE)
    comment = models.ForeignKey(PostComment,on_delete=models.CASCADE,related_name='likes')


    class Meta:
        constraints =[
            UniqueConstraint(
                fields=['auther','comment'],
                name='CommentLikeUnique'
            )
        ]
















































































