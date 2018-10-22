from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Count, Min, Sum
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from datetime import datetime

from .models import Actuacion, Finca, User
from .forms import FincaPreparaForm, FincaReplanteaForm, FincaAAIIForm
# Create your views here.

@login_required
def act_pending_prep(request):
    poblacion = ''
    num_actuaciones = 0
    actuaciones = None
    municipios = Actuacion.objects.order_by().values('municipio').distinct()

    if 'poblacion' in request.GET:
        poblacion = request.GET['poblacion']
        actuaciones = Actuacion.objects.order_by().filter(municipio__iexact=poblacion, is_preparado=False).values('actuacion', 'idzona', 'preparado_por').annotate(total_uuii  = Sum('finca__numero_uuii'), num_fincas = Count('finca'))
        num_actuaciones = actuaciones.count()

        page = request.GET.get('page',1)
        paginator = Paginator(actuaciones, 20)
        try:
            actuaciones = paginator.page(page)
        except PageNotAnInteger:
            actuaciones = paginator.page(1)
        except EmptyPage:
            actuaciones = paginator.page(paginator.num_pages)
    return render(request, 'act_pending_prep.html',
                  {'actuaciones': actuaciones, 'num_actuaciones':num_actuaciones, 'municipios':municipios, 'poblacion':poblacion})
@login_required
def act_pending_prep_fincas(request, actuacion_id):
    actuacion = get_object_or_404(Actuacion, actuacion = actuacion_id)
    if actuacion.preparado_por:
        pass
    else:

        actuacion.preparado_por = get_object_or_404(User,pk=request.user.pk)
        actuacion.save()
    fincas = actuacion.finca_set.all()
    fincas_preparadas = fincas.filter(resultado_preparacion__in=[Finca.PREPARADO, Finca.TRAMO3, Finca.NO_VIABLE, Finca.VIABLE]).count()
    return render(request, 'act_pending_prep_fincas.html',
                  {'fincas': fincas, 'actuacion':actuacion, 'fincas_preparadas':fincas_preparadas })
@login_required
def act_prep_finca(request, pk):
    finca = get_object_or_404(Finca, pk=pk)
    if request.method == "POST":
        form = FincaPreparaForm(data=request.POST,instance=finca)
        user = request.user.username
        if form.is_valid():
            finca = form.save(commit=False)
            #actuacion.replanteado_fecha = datetime.now()
            finca.save()
            return redirect('act_pending_prep_fincas', actuacion_id = finca.actuacion.actuacion)

    else:
        if not finca.numero_uuii_definitivo:
            finca.numero_uuii_definitivo = finca.numero_uuii
        #idzona = actuaciones.first().idzona
        form = FincaPreparaForm(instance=finca)
        return render(request, 'act_prep_finca.html',
                      {'finca': finca, 'actuacion_id':finca.actuacion.actuacion, 'form':form })

@login_required
def act_close_prep(request, actuacion_id):
    actuacion = get_object_or_404(Actuacion, actuacion=actuacion_id)
    actuacion.is_preparado = True
    actuacion.preparado_fecha = datetime.now()
    actuacion.save()
    return redirect('act_pending_prep',)# poblacion=actuacion.municipio)


#######################################################REPLANTEO################################################################################

@login_required
def act_pending_replan(request):
    poblacion = ''
    num_actuaciones = 0
    actuaciones = None
    municipios = Actuacion.objects.order_by().values('municipio').distinct()

    if 'poblacion' in request.GET:
        poblacion = request.GET['poblacion']
        actuaciones = Actuacion.objects.order_by().filter(municipio__iexact=poblacion, is_preparado=True).values('actuacion', 'idzona', 'preparado_por', 'replanteado_por').annotate(
                total_uuii  = Sum('finca__numero_uuii_definitivo'), num_fincas = Count('finca'))
        num_actuaciones = actuaciones.count()

        page = request.GET.get('page',1)
        paginator = Paginator(actuaciones, 20)
        try:
            actuaciones = paginator.page(page)
        except PageNotAnInteger:
            actuaciones = paginator.page(1)
        except EmptyPage:
            actuaciones = paginator.page(paginator.num_pages)
    return render(request, 'act_pending_replan.html',
                  {'actuaciones': actuaciones, 'num_actuaciones':num_actuaciones, 'municipios':municipios, 'poblacion':poblacion})

@login_required
def act_pending_replan_fincas(request, actuacion_id):
    actuacion = get_object_or_404(Actuacion, actuacion = actuacion_id)
    if actuacion.replanteado_por:
        pass
    else:

        actuacion.replanteado_por = get_object_or_404(User,pk=request.user.pk)
        actuacion.save()
    fincas = actuacion.finca_set.filter(resultado_preparacion=Finca.PREPARADO)
    fincas_preparadas = fincas.filter(resultado_replanteo__in=[Finca.VIABLE, Finca.NO_VIABLE, Finca.NO_PROCEDE, Finca.TRAMO3]).count()
    return render(request, 'act_pending_replan_fincas.html',
                  {'fincas': fincas, 'actuacion':actuacion, 'fincas_preparadas':fincas_preparadas, 'poblacion':actuacion.municipio })

@login_required
def act_replan_finca(request, pk):
    finca = get_object_or_404(Finca, pk=pk)
    if request.method == "POST":
        form = FincaReplanteaForm(request.POST,instance=finca)
        user = request.user.username
        if form.is_valid():
            finca = form.save(commit=False)
            finca.is_replanteado = True
            finca.save()
            return redirect('act_pending_replan_fincas', actuacion_id = finca.actuacion.actuacion)

    else:
        #if not finca.numero_uuii_definitivo:
        #    finca.numero_uuii_definitivo = finca.numero_uuii
        #idzona = actuaciones.first().idzona
        form = FincaReplanteaForm(instance=finca)
        return render(request, 'act_prep_finca.html',
                      {'finca': finca, 'actuacion_id':finca.actuacion.actuacion, 'form':form })



@login_required
def act_close_rep(request, actuacion_id):
    actuacion = get_object_or_404(Actuacion, actuacion=actuacion_id)
    actuacion.is_replanteado = True
    actuacion.replanteado_fecha = datetime.now()
    actuacion.save()
    return redirect('act_pending_replan')


#######################################################AAII################################################################################

@login_required
def act_pending_aaii(request):
    poblacion = ''
    num_actuaciones = 0
    actuaciones = None
    municipios = Actuacion.objects.order_by().values('municipio').distinct()

    if 'poblacion' in request.GET:
        poblacion = request.GET['poblacion']
        actuaciones = Actuacion.objects.order_by().filter(municipio__iexact=poblacion, is_replanteado=True, is_aaii_preparada=False, finca__resultado_replanteo= Finca.VIABLE).values('actuacion', 'idzona', 'preparado_por', 'replanteado_por').annotate(total_uuii  = Sum('finca__numero_uuii_definitivo'), num_fincas = Count('finca'))
        num_actuaciones = actuaciones.count()

        page = request.GET.get('page',1)
        paginator = Paginator(actuaciones, 20)
        try:
            actuaciones = paginator.page(page)
        except PageNotAnInteger:
            actuaciones = paginator.page(1)
        except EmptyPage:
            actuaciones = paginator.page(paginator.num_pages)
    return render(request, 'act_pending_aaii.html',
                  {'actuaciones': actuaciones, 'num_actuaciones':num_actuaciones, 'municipios':municipios, 'poblacion':poblacion})

@login_required
def act_pending_aaii_fincas(request, actuacion_id):
    actuacion = get_object_or_404(Actuacion, actuacion = actuacion_id)
    if actuacion.aaii_por:
        pass
    else:

        actuacion.aaii_por = get_object_or_404(User,pk=request.user.pk)
        actuacion.save()
    fincas = actuacion.finca_set.filter(resultado_replanteo=Finca.VIABLE)
    fincas_preparadas = fincas.filter(estado_aaii__in=[Finca.OK, Finca.NO_PROCEDE]).count()
    return render(request, 'act_pending_aaii_fincas.html',
                  {'fincas': fincas, 'actuacion':actuacion, 'fincas_preparadas':fincas_preparadas })

@login_required
def act_aaii_finca(request, pk):
    finca = get_object_or_404(Finca, pk=pk)
    if request.method == "POST":
        form = FincaAAIIForm(request.POST,instance=finca)
        user = request.user.username
        if form.is_valid():
            finca = form.save(commit=False)
            finca.save()
            return redirect('act_pending_aaii_fincas', actuacion_id = finca.actuacion.actuacion)

    else:
        #if not finca.numero_uuii_definitivo:
        #    finca.numero_uuii_definitivo = finca.numero_uuii
        #idzona = actuaciones.first().idzona
        form = FincaAAIIForm(instance=finca)
        return render(request, 'act_aaii_finca.html',
                      {'finca': finca, 'actuacion_id':finca.actuacion.actuacion, 'form':form })


@login_required
def act_close_aaii(request, actuacion_id):
    actuacion = get_object_or_404(Actuacion, actuacion=actuacion_id)
    actuacion.is_aaii_preparada = True
    actuacion.aaii_fecha = datetime.now()
    actuacion.save()
    return redirect('act_pending_aaii')
