from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from datetime import datetime
import logging
from decimal import Decimal

from django.utils import timezone
from django.utils.timezone import timedelta
from django.utils.translation import gettext_lazy as _
import uuid
from django import forms
from PIL import Image
import requests
import datetime  # Importando o módulo datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator

from django.contrib.contenttypes.models import ContentType




class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('O campo email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)




class CustomUser(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(_('nome'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('CPF ou CNPJ'), max_length=30, unique=True)
    telefone = models.CharField(_('telefone'), max_length=20, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    is_staff = models.BooleanField(_('staff status'), default=False)


    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_user_permissions",
        related_query_name="customuser",
    )

    def __str__(self):
        return self.nome

class Evento(models.Model):
    nome = models.CharField(_('nome'), max_length=100)
    foto = models.ImageField(upload_to='images/', blank=True, null=True, default="/images/unknown.png")
    descricao = models.TextField(_('descrição'), blank=True)
    #data_hora_inicio = models.DateTimeField(_('data e hora de início'))
    #data_hora_fim = models.DateTimeField(_('data e hora de fim'))
    #limite_reservas = models.PositiveIntegerField(_('limite de reservas'), default=100)

    valor_por_adulto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    valor_por_crianca_6_a_10 = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    valor_por_crianca_0_a_5 = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Gratuito

    #qtd_max_adultos = models.PositiveIntegerField(default=2, validators=[MinValueValidator(1)])
    #qtd_max_criancas = models.PositiveIntegerField(default=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.nome


class Estado(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class Cidade(models.Model):
    estado = models.ForeignKey(Estado, related_name='cidades', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome



class Bairro(models.Model):
    nome = models.CharField(max_length=255)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class CEP(models.Model):
    codigo = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.codigo

class Endereco(models.Model):
    rua = models.CharField(max_length=255)
    numero = models.IntegerField(null=True, blank=True)
    complemento = models.CharField(max_length=50, null=True, blank=True)
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    cep = models.ForeignKey(CEP, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

class Cliente(CustomUser):
    #foto = models.ImageField(upload_to='images/', blank=True, null=True)
    cep = models.CharField(max_length=50, blank=True, null=True)


class DiaEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='dias', blank=True, null=True)
    data = models.DateField(_('data do evento'))

    def __str__(self):
        return f"{self.evento.nome} - {self.data.strftime('%Y-%m-%d')}"



class HorarioEvento(models.Model):
    dia_evento = models.ForeignKey(DiaEvento, on_delete=models.CASCADE, related_name='horarios')
    hora_inicio = models.TimeField(_('hora de início'))
    limite_reservas = models.PositiveIntegerField(_('limite de reservas'))

    def __str__(self):
        return f"{self.dia_evento} - {self.hora_inicio.strftime('%H:%M')}"

    def reservas_disponiveis(self):
        return self.limite_reservas > self.reservas.count()



class Reserva(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='reservas', blank=True, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='clientes', blank=True, null=True)
    dia_evento = models.DateField("Data do Evento", blank=True, null=True) 
    qtd_adultos = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    qtd_criancas_6_a_10 = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    qtd_criancas_0_a_5 = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    #horario = models.ForeignKey(HorarioEvento, on_delete=models.CASCADE, related_name='reservas', blank=True, null=True)
    #data_inicio = models.DateField(default=datetime.date.today)
    #data_final = models.DateField(default=datetime.date.today)
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.cliente.nome} - {self.dia_evento} - {self.valor_final}"
       

    def calcular_valor_total(self):
        valor_adultos = self.qtd_adultos * self.evento.valor_por_adulto
        valor_criancas_6_a_10 = self.qtd_criancas_6_a_10 * self.evento.valor_por_crianca_6_a_10
        valor_criancas_0_a_5 = self.qtd_criancas_0_a_5 * self.evento.valor_por_crianca_0_a_5  # Geralmente será 0
        return valor_adultos + valor_criancas_6_a_10 + valor_criancas_0_a_5



# Create your models here.
class Foto(models.Model):
    nome = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to='images/', blank=True, null=True)
    # Outros campos conforme necessário

    def __str__(self):
        return self.nome