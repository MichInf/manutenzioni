from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cabine/', views.lista_cabine, name='lista_cabine'),
    path('cabine/crea/', views.crea_cabina, name='crea_cabina'),
    path('cabine/<str:matricola>/', views.dettaglio_cabina, name='dettaglio_cabina'),
    path('cabine/<str:matricola>/modifica/', views.modifica_cabina, name='modifica_cabina'),
    path('cabine/<str:matricola>/aggiungi-componente/', views.aggiungi_componente, name='aggiungi_componente'),
    path('componenti/<int:componente_id>/modifica/', views.modifica_componente, name='modifica_componente'),
    path('componenti/<int:componente_id>/elimina/', views.elimina_componente, name='elimina_componente'),
    path('alert/', views.lista_alert, name='lista_alert'),
    path('clienti/', views.lista_clienti, name='lista_clienti'),
    path('clienti/<int:cliente_id>/', views.dettaglio_cliente, name='dettaglio_cliente'),
    path('clienti/crea/', views.crea_cliente, name='crea_cliente'),
    path('clienti/<int:cliente_id>/modifica/', views.modifica_cliente, name='modifica_cliente'),
    path('cabine/<str:matricola>/programma-manutenzione/', views.programma_manutenzione, name='programma_manutenzione'),
    path('cabine/<str:matricola>/registra-manutenzione-completata/', views.registra_manutenzione_completata, name='registra_manutenzione_completata'),
    path('manutenzione/<int:manutenzione_id>/modifica/', views.modifica_manutenzione, name='modifica_manutenzione'),
    path("manutenzioni/<int:pk>/completa/", views.completa_manutenzione, name="completa_manutenzione"),
    path("manutenzioni/<int:pk>/report/", views.report_compila, name="report_compila"),
    path('ajax/crea-servizio/', views.crea_servizio_ajax, name='crea_servizio_ajax'),
    path('servizio/<int:servizio_id>/rinnova/', views.rinnova_servizio, name='rinnova_servizio'),
    path('logout/', views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)