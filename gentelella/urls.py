"""gentella URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # app/ -> Genetelella UI and resources
    url(r'^app/', include('app.urls')),
    url(r'^', include('app.urls')),
    # login
    url(r'index/$', views.index, name='index'),
    url(r'login/$', views.login, name='login'),
    url(r'register/$', views.register, name='register'),
    url(r'logout/$', views.logout),   
    # groups
    url(r'group_list/$', views.group_list, name='group_list'),
    url(r'join_group/$', views.join_group, name='join_group'),
    url(r'quit_group/$', views.quit_group, name='quit_group'),
    url(r'create_group/$', views.create_group, name='create_group'),
    #group
    url(r'group_info/$', views.group_info, name='group_info'),
    #event
    url(r'event_info/$', views.event_info, name='event_info'),
    url(r'add_event/$', views.add_event, name='add_event'),   
    #voting
    url(r'voting/$', views.voting, name='voting'),
    url(r'vote/$', views.vote, name='vote'),
    #movie
    url(r'movie_info/$', views.movie_info, name='movie_info'),
    url(r'add_movie/$', views.add_movie, name='add_movie'),
    url(r'search_movie/$', views.search_movie, name='search_movie'),
    url(r'view_movie/$', views.view_movie, name='view_movie'),
    
]
