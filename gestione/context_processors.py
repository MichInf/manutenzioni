from .models import Alert

def alert_count(request):
    """Context processor per contare gli alert attivi (non silenziati)"""
    if not request.user.is_authenticated:
        return {"alert_count": 0}

    # Conta solo gli alert non silenziati
    total_alert = Alert.objects.filter(silenziato=False).count()
    critici = Alert.objects.filter(silenziato=False, priorita="critica").count()
    componenti = Alert.objects.filter(silenziato=False, tipo="Manutenzione Componente").count()

    return {
        "alert_count": total_alert,
        "alert_critici": critici,
        "alert_componenti": componenti,
    }
