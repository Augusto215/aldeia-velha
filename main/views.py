from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import F
from django.contrib import messages
from django.db.models import Count
import datetime
from django.urls import reverse

import mercadopago
from django.core.paginator import Paginator
from .models import *
from usuarios.models import *
import stripe

# Create your views here.
def home(request):
    print("Sessão:", request.session.session_key)
    print("Usuário autenticado:", request.user.is_authenticated)
    print(type(request.user))

    eventos = Evento.objects.all()
    context = {
        'eventos': eventos,
    }
    return render(request, 'core/index.html', context)

stripe.api_key = "sk_test_51OOOZrJOrrpeut8BiijyzvYXXB358oG2k8WFwl5ngzFSKZt0Y8cP3uqS1IrPrU4KwP5mmYnygsgqJ9JxyMackUF000llB2wukg"

def get_horarios(request):
    dia_id = request.GET.get('dia_id')
    horarios = HorarioEvento.objects.filter(dia_evento_id=dia_id).annotate(
        reservas_count=Count('reservas')
    ).filter(limite_reservas__gt=F('reservas_count'))
    data = [{'id': horario.id, 'hora_inicio': horario.hora_inicio.strftime('%H:%M')} for horario in horarios]
    return JsonResponse({'horarios': data})


def iniciar_pagamento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    sdk = mercadopago.SDK("APP_USR-205363937963095-011100-7c72c449b7df93fee6326030ab7b71fb-1627783278")

    if request.method == 'POST':
        if hasattr(request.user, 'cliente'):
            cliente = request.user.cliente
        elif isinstance(request.user, Cliente):
            cliente = request.user
        else:
            return redirect('login')

        qtd_adultos = int(request.POST.get('qtd_adultos'))
        qtd_criancas_6_a_10 = int(request.POST.get('qtd_criancas_6_a_10'))
        qtd_criancas_0_a_5 = int(request.POST.get('qtd_criancas_0_a_5'))

        # Calcular o valor total
        valor_total = (qtd_adultos * evento.valor_por_adulto) + \
                      (qtd_criancas_6_a_10 * evento.valor_por_crianca_6_a_10) + \
                      (qtd_criancas_0_a_5 * evento.valor_por_crianca_0_a_5)

        # Criar a reserva
        dia_evento_str = request.POST.get('dia')
        dia_evento = datetime.datetime.strptime(dia_evento_str, '%Y-%m-%d').date()




        request.session['reserva_info'] = {
            'evento_id': evento_id,
            'qtd_adultos': qtd_adultos,
            'qtd_criancas_6_a_10': qtd_criancas_6_a_10,
            'qtd_criancas_0_a_5': qtd_criancas_0_a_5,
            'dia_evento_str': dia_evento_str,
            'valor_total': float(valor_total)
        }

        preference_data = {
        "items": [
            {
                "title": evento.nome,
                "quantity": 1,
                "unit_price": float(valor_total)
            }
        ],
        "back_urls": {
            "success": request.build_absolute_uri(reverse('confirmar_pagamento')),  # Use o nome da URL mapeada para a função de confirmação
            "failure": request.build_absolute_uri(reverse('falha_pagamento')),  # Você deve criar uma função de visualização para falhas
            "pending": request.build_absolute_uri(reverse('pagamento_pendente'))  # E uma para pagamentos pendentes, se desejar
        },
        "auto_return": "approved",  # Opcional: retornar automaticamente para o site quando o pagamento estiver aprovado
        }
        preference_response = sdk.preference().create(preference_data)
        preference_id = preference_response['response']['id']

        # Armazenar o ID da preferência na sessão também pode ser uma boa ideia
        request.session['preference_id'] = preference_id

        # Redirecionar o usuário para a página de pagamento do Mercado Pago
        return redirect(preference_response['response']['init_point'])
    context = {
            'evento': evento,
            'evento_id': evento_id,
        }
    print("Evento ID:", evento_id)  # Adicione esta linha para depuração

    return render(request, 'core/checkout2.html', context)

def verificar_pagamento(sdk, payment_id):
    payment_info = sdk.payment().get(payment_id)
    if payment_info["status"] == 200:
        payment_status = payment_info["response"]["status"]
        return payment_status
    else:
        return None  # ou você pode retornar um status específico ou lançar uma exceção


def confirmar_pagamento(request):
    sdk = mercadopago.SDK("APP_USR-4033645478438119-021215-91a73d62a2df0ea1fec137f5317b7238-2266415170")
    payment_id = request.GET.get('payment_id')  # ou a chave correta enviada pelo Mercado Pago
    payment_status = verificar_pagamento(sdk, payment_id)

    if payment_status == 'approved' and 'reserva_info' in request.session:
        reserva_info = request.session['reserva_info']
        evento = get_object_or_404(Evento, id=reserva_info['evento_id'])
        dia_evento = datetime.datetime.strptime(reserva_info['dia_evento_str'], '%Y-%m-%d').date()

        # Criar a reserva
        reserva = Reserva.objects.create(
            evento=evento,
            cliente=request.user.cliente,
            dia_evento=dia_evento,
            qtd_adultos=reserva_info['qtd_adultos'],
            qtd_criancas_6_a_10=reserva_info['qtd_criancas_6_a_10'],
            qtd_criancas_0_a_5=reserva_info['qtd_criancas_0_a_5'],
            valor_final=Decimal(reserva_info['valor_total'])
        )

        # Limpar a sessão após a reserva ser criada
        del request.session['reserva_info']
        
        messages.success(request, f'Reserva para o evento {evento.nome} realizada com sucesso!')
        return redirect('home')

    # Se o pagamento não foi aprovado ou não há informações na sessão
    messages.error(request, 'Reserva cancelada.')
    return redirect('home')


def localizacao(request):
    return render(request, 'core/localizacao.html')

def historia(request):
    return render(request, 'core/historia.html')

def pataxo(request):
    return render(request, 'core/pataxo.html')

def turismo(request):
    return render(request, 'core/turismo.html')

def historico(request):
    return render(request, 'core/historico.html')

def minhas_reservas(request):
    if hasattr(request.user, 'cliente'):
            cliente = request.user.cliente
    elif isinstance(request.user, Cliente):
        cliente = request.user
    else:
        return redirect('login')

    reservas = Reserva.objects.filter(cliente=cliente)

    context = {
        'reservas':reservas
    }
    
    return render(request, 'core/minhas_reservas.html', context)


def checkout_success(request, evento_id):
    # Opcional: buscar informações do evento, se necessário
    evento = get_object_or_404(Evento, id=evento_id)

    messages.success(request, f'Reserva para o evento {evento.nome} realizada com sucesso!')
    return redirect('home')

def checkout_cancel(request):
    messages.error(request, 'Reserva cancelada.')
    return redirect('home')

def pendent(request):
    messages.error(request, 'Pagamento Pendente.')
    return redirect('home')




def galeria(request):
    fotos_list = Foto.objects.all()
    paginator = Paginator(fotos_list, 6) # Mostra 10 fotos por página

    page_number = request.GET.get('page')
    fotos = paginator.get_page(page_number)

    context = {
        'fotos': fotos
    }
    return render(request, 'core/galeria.html', context)


def projetos(request):

    return render(request, 'core/projetos.html')



def iniciar_doacao(request):
    sdk = mercadopago.SDK("APP_USR-205363937963095-011100-7c72c449b7df93fee6326030ab7b71fb-1627783278")

    if request.method == 'POST':
        valor_doacao_str = request.POST.get('valor_doacao')
        valor_doacao_str = valor_doacao_str.replace('R$', '').replace('.', '').replace(',', '.')

        try:
            valor_doacao = float(valor_doacao_str)
        except ValueError:
            # Tratar o caso em que a conversão não é possível
            # Por exemplo, redirecionar para a página de erro ou mostrar uma mensagem de erro
            # Aqui você pode retornar uma mensagem de erro
            return render(request, 'core/doar.html', {'error': 'Valor inválido. Por favor, insira um número válido.'})

        preference_data = {
            "items": [
                {
                    "title": "Doação",
                    "quantity": 1,
                    "unit_price": valor_doacao
                }
            ],
            "back_urls": {
                "success": request.build_absolute_uri(reverse('confirmar_pagamento')),  # URL de retorno após o pagamento
                "failure": request.build_absolute_uri(reverse('falha_pagamento')),  # URL para caso de falha
                "pending": request.build_absolute_uri(reverse('pagamento_pendente'))  # URL para pagamento pendente
            },
            "auto_return": "approved",
        }

        preference_response = sdk.preference().create(preference_data)
        preference_id = preference_response['response']['id']

        return redirect(preference_response['response']['init_point'])

    return render(request, 'core/doar.html')

def confirmar_doacao(request):
    # Logica para confirmar o pagamento
    messages.success(request, 'Pagamento efetuado com sucesso!')
    return redirect('home')


def falha_doacao(request):
    # Logica para confirmar o pagamento
    messages.error(request, 'Erro na confirmação do pagamento.')
    return redirect('home')
