from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from monitor.models import Image
from django.core import serializers
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.mail import send_mail
from rest_framework import viewsets
from monitor.serializers import ImageSerializer
from . import SnmpGet
from . import Grafica
from . import Thrend
import logging
import json
import os
import time
from . import forms
from . import ObtenerInformacion
from .models import *

from . import Invoker
invoker = Invoker.Invoker()
print (hex(id(invoker)))
invoker.startA()



# Create your views here.
def index(request):

    return render(request, 'adminlte/index.html')

def verAgentes(request):
    if request.method == 'GET':
        agents = Agent.objects.all()
        lista = []
        for agent in agents:
            oidINterfaces = '1.3.6.1.2.1.2.1.0'
            interfaces = SnmpGet.consultaSNMP(str(agent.grupo),str(agent.hostname),int(agent.puerto),int(agent.version),oidINterfaces)
            #print(interfaces)
            status = int(interfaces)
            if status>0:
                status="Up"
            else:
                status="Down"

            diccionario = {'nombre':str(agent.name),
                            'host':str(agent.hostname),
                        'version':str(agent.version),
                        'puerto':str(agent.puerto),
                        'status':str(status),
                        'interfaces':str(interfaces),
                        'grupo':str(agent.grupo)}

            lista.append(diccionario)
        retorno = {'lista':lista}

    elif request.method == 'POST':
        agentForm = forms.newAgentForm(request.POST)
        if agentForm.is_valid():
            name = agentForm.cleaned_data['name']
            hostname =  agentForm.cleaned_data['hostname']
            version = int(agentForm.cleaned_data['version'])
            puerto = int(agentForm.cleaned_data['puerto'])
            grupo = agentForm.cleaned_data['grupo']
            email = agentForm.cleaned_data['email']
            
        
        # Guardado en base de datos
        newAgent = Agent(name, hostname, version, puerto, grupo, email)
        newAgent.save()

        agents = Agent.objects.all()
        lista = []
        for agent in agents:
            oidINterfaces = '1.3.6.1.2.1.2.1.0'
            interfaces = SnmpGet.consultaSNMP(str(agent.grupo),str(agent.hostname),int(agent.puerto),int(agent.version),oidINterfaces)
            #print(interfaces)
            status = int(interfaces)
            if status>0:
                status="Up"
            else:
                status="Down"

            diccionario = {'nombre':str(agent.name),
                            'host':str(agent.hostname),
                        'version':str(agent.version),
                        'puerto':str(agent.puerto),
                        'status':str(status),
                        'interfaces':str(interfaces),
                        'grupo':str(agent.grupo)}

            lista.append(diccionario)
        retorno = {'lista':lista}
    
    return render(request, 'adminlte/agentes.html',context=retorno)

def agregarAgente(request):
    agentForm = forms.newAgentForm()
    context = {'agentForm': agentForm}
    return render(request, 'adminlte/agregarAgente.html', context)

def verAgente(request):
    return render(request, 'adminlte/verAgente.html')

def estadoAgente(request):
    return render(request, 'adminlte/verAgente.html')

def obtenerInfo(request, name):
    try:
        agent = Agent.objects.get(pk=name)
        if (Image.objects.filter(agent_id=name).count() > 0):
            # Get images Path
            images = Image.objects.filter(agent_id=name)[:5]
        else:
            # Save the images into the DB
            loc = "/static/" + name
            imgTraffic = Image(location=loc + "TraficoRed.png", agent_id=name)
            imgPingResponses = Image(location=loc + "RespuestasPING.png", agent_id=name)
            imgTCPSegments = Image(location=loc + "SegmentosTCP.png", agent_id=name)
            imgIPDatagrams = Image(location=loc + "DatagramasIP.png", agent_id=name)
            imgICMPStatistics = Image(location=loc + "EstadisticaICMP.png", agent_id=name)
            
            imgTraffic.save()
            imgPingResponses.save()
            imgTCPSegments.save()
            imgIPDatagrams.save()
            imgICMPStatistics.save()
            
            images = Image.objects.filter(agent_id=name)[:5]
        try:
            traffic = images[0]
            ping = images[1]
            TCP = images[2]
            IP = images[3]
            ICMP = images[4]
            
        except (IndexError) as e:
            print("Some pictures missing")
            
        finally:
            detallesAgente = ObtenerInformacion.obtenerInfo(agent.hostname, agent.puerto, agent.version, agent.grupo)

    except agent.DoesNotExist:
        raise Http404("Agente no encontrado!")
    
    context = {'detallesAgente':detallesAgente,
                'nombreHost': name,
                'imgTraffic': traffic,
                'imgPing': ping,
                'imgTCP': TCP,
                'imgIP': IP,
                'imgICMP': ICMP}

    return render(request,'adminlte/verAgente.html',context)


def verProyeccion(request):
    
    agents  = getAgentsAvailable()

    dic = { 'agentes':agents}
    return render(request,'adminlte/verProyeccion.html',context=dic)



def deleteAgent(request, name):
    # CHANGE TO HTTP DELETE METHOD
    if request.method == 'GET':
        try:
            agent = Agent.objects.get(pk=name)
            agent.delete()
            success = True
        except agent.DoesNotExist:
            success = False
            raise Http404("Agente no encontrado!")
        entry = False
    context = {'success': success, 'entry': entry}
    return render(request,'adminlte/index.html',context=context)


class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer






##Not used to HTTP ###



def sendEmail(email,subject,message):

    #subject = 'Evidencia 3 '
    #message = 'Equipo 10 Grupo 4CM3' 
    email_from = settings.EMAIL_HOST_USER
    recipient_list = []
    recipient_list.append(str(email))
    res = send_mail(subject,message,email_from,recipient_list,)
    if res:
        print("Correo Electronico enviado a "+email)
        logging.info("Correo Electronico enviado a "+email)
    else: 
        print("Ocurrió un error al enviar el correo elcronico a "+email)
        logging.info("Ocurrió un error al enviar el correo elcronico a "+email)
    
    return  


def getAgentsAvailable():

        agents = Agent.objects.all()
        li = []
        d = {}
        for agent in agents:
            d['name'] = agent.name
            d['hostname'] = agent.hostname
            d['version'] = agent.version
            d['puerto'] = agent.puerto
            d['grupo'] = agent.grupo
            d['email'] = agent.email
            li.append(d)
        
        return li



