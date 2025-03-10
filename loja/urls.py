from django.urls import path
from . import views

urlpatterns = [
    path('loja/', views.loja, name='loja'),
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('remover/<int:produto_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/sucesso/', views.checkout_sucesso, name='checkout_sucesso'),
    path('checkout/erro/', views.checkout_erro, name='checkout_erro'),
    path('checkout/pendente/', views.checkout_pendente, name='checkout_pendente'),
path('carrinho/atualizar/', views.atualizar_carrinho, name='atualizar_carrinho'),
    path('checkout/pendente/', views.checkout_pendente, name='checkout_pendente'),
    path('checkout/confirmacao/', views.confirmacao_checkout, name='confirmacao_checkout'),
    path('checkout/finalizar/', views.checkout_finalizar, name='checkout_finalizar'),
    path('calcular_frete/', views.calcular_frete_view, name='calcular_frete'),



]
