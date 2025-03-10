from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import logging
import requests
import mercadopago
from .models import Produto, Pedido, ItemPedido
from .carrinho import Carrinho

logger = logging.getLogger(__name__)
mercado_pago_sdk = mercadopago.SDK("APP_USR-205363937963095-011100-7c72c449b7df93fee6326030ab7b71fb-1627783278")
BASE_URL = "https://seusite.com"


def loja(request):
    produtos = Produto.objects.all()
    return render(request, 'core/loja.html', {'produtos': produtos})


@login_required
def adicionar_ao_carrinho(request, produto_id):
    if request.method == "POST":
        carrinho = Carrinho(request)
        quantidade = int(request.POST.get(f"quantidade_{produto_id}", 1))
        
        if quantidade >= 1:
            carrinho.adicionar(produto_id, quantidade, atualizar=True)

    return redirect('ver_carrinho') 

@login_required
def ver_carrinho(request):
    carrinho = Carrinho(request)
    itens = []
    total = 0

    for produto_id, data in carrinho.listar_itens().items():
        produto = get_object_or_404(Produto, id=int(produto_id))
        quantidade = max(1, data['quantidade'])
        subtotal = produto.preco * quantidade
        total += subtotal

        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal
        })

    return render(request, 'core/carrinho.html', {'itens': itens, 'total': total})


@login_required
def remover_do_carrinho(request, produto_id):
    carrinho = Carrinho(request)
    carrinho.remover(produto_id)
    return redirect('ver_carrinho')


@login_required
def checkout(request):
    return redirect("confirmacao_checkout")

@login_required
def confirmacao_checkout(request):
    carrinho = Carrinho(request)
    itens = []
    total = 0

    for produto_id, data in carrinho.listar_itens().items():
        produto = get_object_or_404(Produto, id=int(produto_id))
        quantidade = max(1, data['quantidade'])
        subtotal = produto.preco * quantidade
        total += subtotal

        itens.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal
        })

    return render(request, 'core/confirmacao_checkout.html', {'itens': itens, 'total': total})

@login_required
def checkout_finalizar(request):
    try:
        carrinho = Carrinho(request)
        itens = []
        total = 0

        for produto_id, data in carrinho.listar_itens().items():
            produto = get_object_or_404(Produto, id=int(produto_id))
            quantidade = max(1, data['quantidade'])
            subtotal = produto.preco * quantidade
            total += subtotal

            itens.append({'produto': produto, 'quantidade': quantidade, 'subtotal': subtotal})

        # Criar o pedido no banco de dados com status "pendente"
        pedido = Pedido.objects.create(
            usuario=request.user,
            total=total,
            status="pendente"  # O pedido será confirmado apenas após o pagamento
        )

        for item in itens:
            ItemPedido.objects.create(
                pedido=pedido,
                produto=item['produto'],
                quantidade=item['quantidade']
            )

        # Criar a preferência de pagamento no Mercado Pago
        preference_data = {
            "items": [
                {
                    "title": item['produto'].nome,
                    "quantity": item['quantidade'],
                    "unit_price": float(Produto.objects.get(id=item['produto'].id).preco)
                } for item in itens
            ],
            "back_urls": {
                "success": f"{BASE_URL}/checkout/sucesso/{pedido.id}/",
                "failure": f"{BASE_URL}/checkout/erro/{pedido.id}/",
                "pending": f"{BASE_URL}/checkout/pendente/{pedido.id}/",
            },
            "auto_return": "approved",
        }

        preference_response = mercado_pago_sdk.preference().create(preference_data)

        # Limpar o carrinho após iniciar o pagamento
        carrinho.limpar()

        return redirect(preference_response['response']['init_point'])

    except Exception as e:
        logger.error(f"Erro no checkout: {str(e)}")
        return redirect("checkout_erro")



@login_required
def checkout_sucesso(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    pedido.status = "pago"  # Confirma o pedido no banco
    pedido.save()
    return render(request, 'loja/checkout_sucesso.html', {'pedido': pedido})

def checkout_erro(request):
    return render(request, 'loja/checkout_erro.html')


def checkout_pendente(request):
    return render(request, 'loja/checkout_pendente.html')

@login_required
def atualizar_carrinho(request):
    if request.method == "POST":
        carrinho = Carrinho(request)

        for key, quantidade in request.POST.items():
            if key.startswith("quantidade_"):
                produto_id = key.split("_")[1]
                try:
                    quantidade = int(quantidade)
                    if quantidade >= 1:
                        # Removendo o item antigo antes de adicionar o novo com a quantidade correta
                        carrinho.remover(produto_id)
                        carrinho.adicionar(produto_id, quantidade)
                except ValueError:
                    continue  # Ignora valores inválidos

    return redirect("ver_carrinho")

SUPERFRETE_API_URL = "https://sandbox.superfrete.com/api/v0/calculator"
SUPERFRETE_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NDE1NTYwMzcsInN1YiI6IkJhTEVXZjBOQnZPUUplMDhhajVid21Bb1BTNDMifQ.9I_Dx3929PLS2TmvWDLz5rD8w21D57BkkID_P4QshuE"
 
def calcular_frete():
    headers = {
        "Authorization": f"Bearer {SUPERFRETE_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "augusto.webdeveloping@gmail.com"
    }

    payload = {
    "from": {"postal_code": "01153000"},
    "to": {"postal_code": "20020050"},
    "services": "1,2,17",
    "options": {
        "own_hand": False,
        "receipt": False,
        "insurance_value": 0,
        "use_insurance_value": False
    },
    "package": {
        "height": 2,
        "width": 11,
        "length": 16,
        "weight": 0.3  # Agora está igual ao Postman
    }
}


    try:
        print(">>> Enviando requisição para SuperFrete...")
        print(">>> Headers:", headers)
        print(">>> Payload:", payload)

        response = requests.post(SUPERFRETE_API_URL, headers=headers, json=payload, timeout=10)

        print(f">>> Status Code: {response.status_code}")
        print(f">>> Resposta da API: {response.text}")

        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as e:
        print(">>> Erro HTTP:", e)
        return {"erro": f"Erro HTTP na API do SuperFrete: {e}"}
    except requests.exceptions.RequestException as e:
        print(">>> Erro de Conexão:", e)
        return {"erro": f"Erro na conexão com o SuperFrete: {e}"}
    except Exception as e:
        print(">>> Erro inesperado:", e)
        return {"erro": f"Erro inesperado: {e}"}


@login_required
def calcular_frete_view(request):
    """Endpoint Django que chama a API do SuperFrete."""
    fretes = calcular_frete()

    if "erro" in fretes:
        return JsonResponse(fretes, status=500)

    return JsonResponse(fretes)
