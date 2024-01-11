from django.shortcuts import render
from usuarios.forms import *
from django.contrib.sessions.models import Session
from .models import *
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import login as auth_login
from .forms import LoginForm
from django.contrib.auth import authenticate
import logging
import googlemaps
from django.contrib import messages
def register(request):
    form = ClienteRegistrationForm()

    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
           
                user = Cliente.objects.create_user(
                    nome = form.cleaned_data['nome'],
                    username = form.cleaned_data['username'],
                    telefone = form.cleaned_data['telefone'],
                    email=form.cleaned_data['email'],
                    #foto = form.cleaned_data['foto'],
                    password=form.cleaned_data['password1'],
              
                 
                  
                )
                user.save()

             
               
               
                    
                messages.success(request, 'Cadastro Realizado com sucesso!')
                return redirect('login')
        else:
            print("Formulário inválido")
            messages.error(request, form.errors)
    
    return render(request, 'core/registro.html', {'form': form})


def obter_coordenadas(endereco_completo, google_maps_api_key):
    gmaps = googlemaps.Client(key=google_maps_api_key)
    geocode_result = gmaps.geocode(endereco_completo)
    
    if geocode_result:
        latitude = geocode_result[0]['geometry']['location']['lat']
        longitude = geocode_result[0]['geometry']['location']['lng']
        return latitude, longitude
    
    return None, None


from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Usuário logado com sucesso!")
            return redirect('home')
        else:
            messages.error(request, "Email ou senha inválidos.")
    else:
        form = LoginForm()
        
        
    return render(request, 'core/login.html')


    
from django.contrib.auth import logout

def custom_logout(request):
    logout(request)
    return redirect('home')
    