from django.http import HttpResponse
from django.shortcuts import render
from .models import DireccionEnCobertura, Ciudad
from django.views import generic

# Create your views here.
def index(request):

    num_municipios = DireccionEnCobertura.objects.values_list('municipio').distinct().count()
    #municipios = Ciudad.objects.all()
    municipios = DireccionEnCobertura.objects.order_by().values('municipio').distinct()
    #return HttpResponse("Index de Cobertura Total.")
    if 'poblacion' in request.GET:
        query=True
        poblacion = request.GET['poblacion']
        direcciones = DireccionEnCobertura.objects.filter(municipio__iexact=poblacion)
        if 'via' in request.GET:
            via = request.GET['via']
            direcciones = direcciones.filter(nombre_via__icontains=via)
            num_direcciones = direcciones.count()
        return render(request, 'index.html',
                      {'direcciones': direcciones, 'num_direcciones':num_direcciones, 'municipios':municipios, 'query':query })
    else:
        query=False
    return (render (request, 'index.html', context={'num_municipios':num_municipios, 'municipios':municipios, 'query':query}))


class ListaCoberturaView(generic.ListView):
    model =  DireccionEnCobertura
    context_object_name = 'direcciones_list'   # your own name for the list as a template variable
