from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import *

class ClienteRegistrationForm(UserCreationForm):
    cep = forms.CharField(max_length=9, required=True)
    image = forms.ImageField(required=False)
    

    class Meta:
        model = Cliente
        fields = ['email', 'password1', 'password2', 'cep', 'nome', 'username', 'telefone']


class LoginForm(AuthenticationForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Email ou CPF'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Senha'}))

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        """ Retorna um conjunto de usuários correspondentes para redefinição de senha. """
        # Busca usuários pelo e-mail, independente do estado 'is_active'
        active_users = User._default_manager.filter(email__iexact=email)
        return (u for u in active_users if u.has_usable_password())


