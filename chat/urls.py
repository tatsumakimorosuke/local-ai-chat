
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("stream/", views.stream_chat, name="stream_chat"),
    path("new/", views.new_chat, name="new_chat"),
    path("open/<int:conversation_id>/", views.open_chat, name="open_chat"),
    path("delete/<int:conversation_id>/", views.delete_chat, name="delete_chat"),
    path("rename/<int:conversation_id>/", views.rename_chat, name="rename_chat"),
]
