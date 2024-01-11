from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from django.http import JsonResponse
from django.db.models import F
from django.contrib import messages
from django.db.models import Count
from datetime import datetime
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


from datetime import datetime

def processar_reserva(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        
        if evento.foto and hasattr(evento.foto, 'url'):
            imagem_url = request.build_absolute_uri(evento.foto.url)
        else:
            # URL de uma imagem padrão, caso o evento não tenha uma imagem
            imagem_url = request.build_absolute_uri('reservaApp\static\img\a72ef393-ee5d-4d76-acf5-42a4a54b4a36.jpg')

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
        dia_evento = datetime.strptime(dia_evento_str, '%Y-%m-%d').date()

        reserva = Reserva.objects.create(
            evento=evento,
            cliente=cliente,
            dia_evento=dia_evento,
            qtd_adultos=qtd_adultos,
            qtd_criancas_6_a_10=qtd_criancas_6_a_10,
            qtd_criancas_0_a_5=qtd_criancas_0_a_5,
            valor_final=Decimal(valor_total)
        )


        # Criar a sessão de checkout do Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'unit_amount': int(valor_total * 100),  # Stripe usa o menor valor da moeda, como centavos
                    'product_data': {
                        'name': evento.nome,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('success/'),
            cancel_url=request.build_absolute_uri('/cancel/'),
        )
          # Inclua as informações do evento no contexto
        
        return redirect(checkout_session.url, code=303)
    context = {
            'evento': evento,
            'evento_id': evento_id,
        }
    return render(request, 'core/checkout2.html', context)



def localizacao(request):
    return render(request, 'core/localizacao.html')

def historia(request):
    return render(request, 'core/historia.html')

def pataxo(request):
    return render(request, 'core/pataxo.html')

def desfile(request):
    return render(request, 'core/desfile.html')

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





def galeria(request):
    fotos_list = Foto.objects.all()
    paginator = Paginator(fotos_list, 6) # Mostra 10 fotos por página

    page_number = request.GET.get('page')
    fotos = paginator.get_page(page_number)

    context = {
        'fotos': fotos
    }
    return render(request, 'core/galeria.html', context)