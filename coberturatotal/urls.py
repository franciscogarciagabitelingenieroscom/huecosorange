from django.urls import path
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #path('accounts/login/', auth_views.LoginView.as_view()),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^direcciones/$', views.ListaCoberturaView.as_view(), name='direcciones'),

]
