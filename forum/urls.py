from . import views
from django.urls import re_path

app_name = "forum"
urlpatterns = [
    re_path(r'^$',views.index,name='index'),
    re_path(r'^thread/(?P<pk>\d+)/$', views.view_thread, name='thread'),
    re_path(r'^thread/(?P<pk>\d+)/add_post/$', views.add_post, name='add_post'),
    re_path(r'^create_forum/$', views.create_forum, name='create_forum'),
    re_path(r'^(?P<pk>\d+)/$', views.forum, name='forum'),
    re_path(r'^(?P<pk>\d+)/add_thread/$', views.add_thread, name='add_thread'),
    re_path(r'^thread/post/(?P<pk>\d+)/comment/$', views.comment, name="comment"),
    re_path(r'^(?P<pk>\d+)/edit/$', views.edit_forum, name="edit_forum"),

]
