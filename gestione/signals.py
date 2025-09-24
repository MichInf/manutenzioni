from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Cabina, Componente, Alert

@receiver(post_save, sender=Cabina)
def genera_alert_cabina(sender, instance, **kwargs):
    stato = instance.stato_manutenzione_ordinaria()
    alert_qs = Alert.objects.filter(cabina=instance, componente=None, tipo="Manutenzione Ordinaria")

    # Se esiste ed è silenziato → non fare nulla
    if alert_qs.filter(silenziato=True).exists():
        return

    # Se esiste ed è posticipato → non toccarlo
    if alert_qs.exists() and alert_qs.first().posticipato_a:
        return

    if stato in ["scaduta", "in_scadenza"]:
        priorita = "critica" if stato == "scaduta" else "alta"
        Alert.objects.update_or_create(
            cabina=instance,
            componente=None,
            tipo="Manutenzione Ordinaria",
            defaults={
                "priorita": priorita,
                "scadenza": instance.prossima_manutenzione_ordinaria(),
                "silenziato": False,
            },
        )
    else:
        alert_qs.delete()


@receiver(post_save, sender=Componente)
def genera_alert_componente(sender, instance, **kwargs):
    stato = instance.stato_manutenzione()
    if stato in ["scaduta", "in_scadenza"]:
        priorita = "critica" if stato == "scaduta" else "alta"
        Alert.objects.update_or_create(
            cabina=instance.cabina,
            componente=instance,
            tipo="Manutenzione Componente",
            defaults={
                "priorita": priorita,
                "scadenza": instance.prossima_manutenzione(),
                "silenziato": False,
            },
        )
    else:
        Alert.objects.filter(componente=instance, tipo="Manutenzione Componente").delete()

from .models import Cabina, Componente, Alert

@receiver(post_delete, sender=Cabina)
def elimina_alert_cabina(sender, instance, **kwargs):
    """
    Quando elimino una cabina → elimino tutti gli alert collegati.
    """
    Alert.objects.filter(cabina=instance).delete()


@receiver(post_delete, sender=Componente)
def elimina_alert_componente(sender, instance, **kwargs):
    """
    Quando elimino un componente → elimino gli alert legati a quel componente.
    """
    Alert.objects.filter(componente=instance).delete()
