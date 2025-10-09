from .models import Alert

def alert_count(request):
    """
    Mostra nella navbar il numero di alert attivi:
    - solo 'scaduti' o 'in_scadenza'
    - esclude i silenziati e i 'normali'
    """
    if not request.user.is_authenticated:
        return {}

    alert_attivi = Alert.objects.filter(silenziato=False)

    scaduti = sum(1 for a in alert_attivi if a.priorita == "scaduto")
    in_scadenza = sum(1 for a in alert_attivi if a.priorita == "in_scadenza")

    return {
        "alert_scaduti": scaduti,
        "alert_in_scadenza": in_scadenza,
        "alert_count": scaduti + in_scadenza,
    }
