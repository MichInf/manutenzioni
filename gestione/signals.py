from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Cabina, Componente, Alert

@receiver(post_save, sender=Cabina)
def genera_alert_cabina(sender, instance, **kwargs):
    stato = instance.stato_manutenzione_ordinaria()
    priorita = "normale"
    if stato == "in_scadenza":
        priorita = "alta"
    elif stato == "scaduta":
        priorita = "critica"
    elif stato == "completata":
        Alert.objects.filter(cabina=instance, componente=None).delete()
        return

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

@receiver(post_save, sender=Componente)
def genera_alert_componente(sender, instance, **kwargs):
    stato = instance.stato_manutenzione()
    priorita = "normale"
    if stato == "in_scadenza":
        priorita = "alta"
    elif stato == "scaduta":
        priorita = "critica"
    elif stato == "completata":
        Alert.objects.filter(componente=instance).delete()
        return

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
