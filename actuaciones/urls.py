from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    #path('', views.actuaciones_list, name='actuaciones_list'),

    url(r'^actuaciones/preparar/pendientes/$', views.act_pending_prep, name='act_pending_prep'),
    #url(r'^actuaciones/preparar/pendientes/(?P<poblacion>\w+?)/$', views.act_pending_prep, name='act_pending_prep2'),
    url(r'^actuaciones/preparar/fincas/(?P<actuacion_id>[\w{}.-]+)/$', views.act_pending_prep_fincas, name='act_pending_prep_fincas'),
    url(r'^actuaciones/preparar/finca/(?P<pk>[0-9]+)/$', views.act_prep_finca, name='act_prep_finca'),
    url(r'^actuaciones/preparar/cierre/(?P<actuacion_id>[\w{}.-]+)/$', views.act_close_prep, name='act_close_prep'),

    url(r'^actuaciones/replantear/pendientes/$', views.act_pending_replan, name='act_pending_replan'),
    url(r'^actuaciones/replantear/fincas/(?P<actuacion_id>[\w{}.-]+)/$', views.act_pending_replan_fincas, name='act_pending_replan_fincas'),
    url(r'^actuaciones/replantear/finca/(?P<pk>[0-9]+)/$', views.act_replan_finca, name='act_replan_finca'),
    url(r'^actuaciones/replantear/cierre/(?P<actuacion_id>[\w{}.-]+)/$', views.act_close_rep, name='act_close_rep'),

    url(r'^actuaciones/aaii/pendientes/$', views.act_pending_aaii, name='act_pending_aaii'),
    url(r'^actuaciones/aaii/fincas/(?P<actuacion_id>[\w{}.-]+)/$', views.act_pending_aaii_fincas, name='act_pending_aaii_fincas'),
    url(r'^actuaciones/aaii/finca/(?P<pk>[0-9]+)/$', views.act_aaii_finca, name='act_aaii_finca'),
    url(r'^actuaciones/aaii/cierre/(?P<actuacion_id>[\w{}.-]+)/$', views.act_close_aaii, name='act_close_aaii'),
]
