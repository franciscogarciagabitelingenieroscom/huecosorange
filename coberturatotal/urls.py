from django.urls import path
from django.conf.urls import url


from . import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^direcciones/$', views.ListaCoberturaView.as_view(), name='direcciones'),

]
