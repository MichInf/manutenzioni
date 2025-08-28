from .models import Cabina, Componente

def alert_count(request):
    """Context processor per contare gli alert attivi"""
    if not request.user.is_authenticated:
        return {'alert_count': 0}
    
    # Conta alert cabine
    alert_cabine = 0
    for cabina in Cabina.objects.filter(attiva=True):
        stato = cabina.stato_manutenzione_ordinaria()
        if stato in ['scaduta', 'in_scadenza']:
            alert_cabine += 1
    
    # Conta alert componenti
    alert_componenti = 0
    for componente in Componente.objects.filter(attivo=True):
        stato = componente.stato_manutenzione()
        if stato in ['scaduta', 'in_scadenza']:
            alert_componenti += 1
    
    total_alert = alert_cabine + alert_componenti
    
    return {
        'alert_count': total_alert,
        'alert_critici': alert_cabine,
        'alert_componenti': alert_componenti,
    }