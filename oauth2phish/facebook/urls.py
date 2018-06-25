from django.urls import path
from . import views


app_name = 'facebook'
urlpatterns = [
  path('home/', views.home, name='home'),
  path('link/', views.link, name='link'),
  path('gettoken/', views.gettoken, name='gettoken'),
  #path('mail/', views.mail, name='mail'),
  #path('events/', views.events, name='events'),
]