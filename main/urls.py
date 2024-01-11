from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from main.views import *

urlpatterns = [
        path('', home, name='home'),
        path('checkout/<int:evento_id>/', processar_reserva, name='checkout'),
        #path('ajax/get_horarios/', get_horarios, name='ajax_get_horarios'),
        path('localizacao/', localizacao, name='localizacao'),
        path('historia/', historia, name='historia'),
        path('historico/', historico, name='historico'),
        path('pataxo/', pataxo, name='pataxo'),
        path('desfile/', desfile, name='desfile'),
        path('reservas/', minhas_reservas, name='reservas'),
        path('checkout/<int:evento_id>/success/', checkout_success, name='success'),
        path('cancel/', checkout_cancel, name='cancel'),
        path('galeria/', galeria, name='galeria'),





]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    