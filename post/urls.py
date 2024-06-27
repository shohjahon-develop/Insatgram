from django.urls import path

from post.views import (PostListApiView,PostCommentCreateView,PostCommentListView
                        ,PostLikeApiView,PostCreateView,PostLikeListView,CommentRetrieveView,
                        PostRetrieveUpdateDestoryView,CommentListCreateApiView,CommentLikeAPIView,
                        CommentLikeListView)

urlpatterns=[
    path('list/',PostListApiView.as_view()),
    path('create/',PostCreateView.as_view()),
    path('<uuid:pk>/',PostRetrieveUpdateDestoryView.as_view()),
    path('<uuid:pk>/likes/',PostLikeListView.as_view()),
    path('<uuid:pk>/comments/',PostCommentListView.as_view()),
    path('<uuid:pk>/comments/create/',PostCommentCreateView.as_view()),
    path('comments/',CommentListCreateApiView.as_view()),
    path('comments/<uuid:pk>/',CommentRetrieveView.as_view()),
    path('comments/<uuid:pk>/likes/',CommentLikeListView.as_view()),
    path('<uuid:pk>/create-delete-like/',PostLikeApiView.as_view()),
    path('comments/<uuid:pk>/create-delete-like/',CommentLikeAPIView.as_view())
]






















































