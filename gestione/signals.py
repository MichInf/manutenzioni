from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Alert, ManutenzioneProgrammata


@receiver(post_save, sender=ManutenzioneProgrammata)
def crea_o_aggiorna_alert_manutenzione(sender, instance, **kwargs):
    """
    Crea o aggiorna un alert per ogni manutenzione programmata.
    Se la manutenzione è completata → l'alert viene rimosso.
    """
    # Se la manutenzione è completata o fatturata → rimuoviamo eventuale alert
    if instance.stato in ['completata', 'fatturata']:
        Alert.objects.filter(
            tipo="Manutenzione Programmata",
            cabina=instance.cabina,
            componente=None
        ).delete()
        return

    # Solo per manutenzioni attive
    if instance.stato in ['programmata', 'inviata']:
        scadenza = instance.data_programmata

        Alert.objects.update_or_create(
            tipo="Manutenzione Programmata",
            cabina=instance.cabina,
            componente=None,
            defaults={
                'scadenza': scadenza,
                'silenziato': False,
            }
        )


@receiver(post_delete, sender=ManutenzioneProgrammata)
def elimina_alert_manutenzione(sender, instance, **kwargs):
    """
    Se una manutenzione viene eliminata, rimuove il relativo alert.
    """
    Alert.objects.filter(
        tipo="Manutenzione Programmata",
        cabina=instance.cabina,
        componente=None
    ).delete()
