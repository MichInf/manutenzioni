import os
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    RUOLI_CHOICES = [
        ('Administrator', 'Administrator'),
        ('Controlroom', 'Controlroom'),
        ('Operatore', 'Operatore'),
    ]
    ruolo = models.CharField(max_length=20, choices=RUOLI_CHOICES, default='Operatore')

    def is_administrator(self):
        return self.is_superuser or self.ruolo == 'Administrator'

    def is_controlroom(self):
        return self.ruolo == 'Controlroom'

    def is_operatore(self):
        return self.ruolo == 'Operatore'

class TipoComponente(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    descrizione = models.TextField(blank=True, verbose_name="Descrizione")
    intervallo_manutenzione_giorni = models.IntegerField(default=365, verbose_name="Intervallo Manutenzione (giorni)")
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Tipo Componente"
        verbose_name_plural = "Tipi Componente"

class Cliente(models.Model):
    # Informazioni Base
    nome_azienda = models.CharField(max_length=200, verbose_name="Nome Azienda")
    responsabile = models.CharField(max_length=100, verbose_name="Responsabile")
    telefono_responsabile = models.CharField(max_length=20, verbose_name="Tel. Responsabile")
    email = models.EmailField(verbose_name="Email")
    email2 = models.EmailField(blank=True, verbose_name="Email 2")
    
    # Informazioni Aggiuntive
    note = models.TextField(blank=True, verbose_name="Note")
    attivo = models.BooleanField(default=True, verbose_name="Attivo")
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_modifica = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nome_azienda
    
    def numero_cabine(self):
        """Conta il numero di cabine del cliente"""
        return self.cabine.filter(attiva=True).count()
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clienti"
        ordering = ['nome_azienda']

class Cabina(models.Model):
    # Informazioni Base
    nome = models.CharField(max_length=200, verbose_name="Nome/Denominazione")
    matricola = models.CharField(max_length=50, unique=True, verbose_name="Matricola")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='cabine', verbose_name="Cliente")
    fonte = models.CharField(max_length=50,blank=True,verbose_name="Fonte energetica")
    # Informazioni Specifiche
    guardiania = models.CharField(max_length=100, blank=True, verbose_name="Guardiania")
    chiave = models.CharField(max_length=50, blank=True, verbose_name="N° Chiave")
    pod = models.CharField(max_length=50, blank=True, verbose_name="POD")
    telefono_guardiania = models.CharField(max_length=20, blank=True, verbose_name="Tel. Guardiania")
    societa_proprietaria = models.CharField(max_length=100, blank=True, verbose_name="Società proprietaria")
    # Coordinate (opzionali)
    latitudine = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, verbose_name="Latitudine")
    longitudine = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name="Longitudine")
    
    # Stato
    attiva = models.BooleanField(default=True, verbose_name="Attiva")
    note = models.TextField(blank=True, verbose_name="Note")
    
    template_report = models.ForeignKey(
        'ReportTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cabine_assegnate',
        verbose_name="Template report"
    )
 

    def __str__(self):
        return f"{self.matricola} - {self.nome}"
    
    def ultima_manutenzione_ordinaria(self):
        """Restituisce l'ultima manutenzione ordinaria completata"""
        ultima = self.manutenzioni.filter(
            stato='completata',
            tipo__in=['semestrale', 'annuale']
        ).order_by('-data_completamento').first()
        return ultima.data_completamento if ultima else None

    def prossima_manutenzione_ordinaria(self):
        """Restituisce la prossima manutenzione programmata"""
        prossima = self.manutenzioni.filter(
            stato='programmata',
            tipo__in=['semestrale', 'annuale']
        ).order_by('data_programmata').first()
        return prossima.data_programmata if prossima else None

    def giorni_alla_manutenzione_ordinaria(self):
        """Calcola i giorni alla prossima manutenzione programmata"""
        prossima = self.prossima_manutenzione_ordinaria()
        if prossima:
            delta = prossima - timezone.now().date()
            return delta.days
        return None

    def stato_manutenzione_ordinaria(self):
        """Determina lo stato della manutenzione ordinaria"""
        giorni = self.giorni_alla_manutenzione_ordinaria()
        if giorni is None:
            return 'nessuna_programmata'
        elif giorni < 0:
            return 'scaduta'
        elif giorni <= 30:
            return 'in_scadenza'
        else:
            return 'ok'

    def servizi_attivi(self):
        return self.servizi_assoc.filter(scadenza__gte=timezone.now().date())
        
    class Meta:
        verbose_name = "Cabina"
        verbose_name_plural = "Cabine"
        ordering = ['matricola']


class PianoManutenzione(models.Model):
    class Tipo(models.TextChoices):
        SEMESTRALE_ANNUALE = 'semestrale_annuale', 'Semestrale + Annuale'
        ANNUALE_ONLY = 'annuale_only', 'Solo Annuale'
        SPOT = 'spot', 'Spot'
        MENSILE_LITE_ANNUALE = 'mensile_lite_annuale', 'Mensile Lite + Annuale'

    cabina = models.OneToOneField(
        'Cabina',
        on_delete=models.CASCADE,
        related_name='piano_manutenzione',
    )
    tipo = models.CharField(max_length=50, choices=Tipo.choices)
    durata_contrattuale_mesi = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Durata contrattuale (mesi)",
    )

    def __str__(self):
        return f"{self.cabina} - {self.get_tipo_display()}"

class Componente(models.Model):
    cabina = models.ForeignKey(Cabina, on_delete=models.CASCADE, related_name='componenti')
    tipo = models.ForeignKey(TipoComponente, on_delete=models.CASCADE)
    data_installazione = models.DateField(null=True, blank=True, verbose_name="Data Installazione")
    data_ultima_manutenzione = models.DateField(null=True, blank=True, verbose_name="Ultima Manutenzione")
    attivo = models.BooleanField(default=True, verbose_name="Attivo")
    note = models.TextField(blank=True, verbose_name="Note")
    
    def __str__(self):
        return f"{self.cabina.matricola} - {self.tipo.nome}"
    
    def prossima_manutenzione(self):
        """Calcola la prossima scadenza del componente"""
        if self.data_ultima_manutenzione:
            return self.data_ultima_manutenzione + timedelta(days=self.tipo.intervallo_manutenzione_giorni)
        elif self.data_installazione:
            return self.data_installazione + timedelta(days=self.tipo.intervallo_manutenzione_giorni)
        return None
    
    def giorni_alla_manutenzione(self):
        """Calcola i giorni alla prossima manutenzione"""
        prossima = self.prossima_manutenzione()
        if prossima:
            delta = prossima - timezone.now().date()
            return delta.days
        return None
    
    def stato_manutenzione(self):
        """Determina lo stato della manutenzione"""
        giorni = self.giorni_alla_manutenzione()
        if giorni is None:
            return 'mai_effettuata'
        elif giorni < 0:
            return 'scaduta'
        elif giorni <= 30:
            return 'in_scadenza'
        else:
            return 'ok'
    
    class Meta:
        verbose_name = "Componente"
        verbose_name_plural = "Componenti"

class ManutenzioneProgrammata(models.Model):
    TIPO_CHOICES = [
        ('semestrale', 'Ordinaria Semestrale'),
        ('annuale', 'Ordinaria Annuale'),
        ('mensile', 'Mensile Lite'),
        ('spot', 'Spot / Extra'),
    ]
    
    STATO_CHOICES = [
        ('programmata', 'Programmata'),
        ('completata', 'Completata'),
        ('inviata', 'Inviata'),
        ('fatturata', 'Fatturata')
    ]

    cabina = models.ForeignKey(Cabina, on_delete=models.CASCADE, related_name='manutenzioni')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='semestrale')
    data_programmata = models.DateField()
    data_completamento = models.DateField(null=True, blank=True)
    stato = models.CharField(max_length=20, choices=STATO_CHOICES, default='programmata')
    operatore = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)
    creata_da = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='manutenzioni_create')
    data_creazione = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['data_completamento']
        verbose_name = 'Manutenzione Programmata'
        verbose_name_plural = 'Manutenzioni Programmate'
    
    def __str__(self):
        return f"{self.cabina.matricola} - {self.get_tipo_display()} - {self.data_programmata}"
    
    @property
    def giorni_alla_scadenza(self):
        from datetime import date
        if self.stato == 'completata':
            return None
        delta = self.data_programmata - date.today()
        return delta.days
    
    @property
    def stato_scadenza(self):
        giorni = self.giorni_alla_scadenza
        if giorni is None:
            return 'completata'
        elif giorni < 0:
            return 'scaduta'
        elif giorni <= 7:
            return 'urgente'
        elif giorni <= 30:
            return 'in_scadenza'
        else:
            return 'ok'

class Servizio(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome servizio")
    descrizione = models.TextField(blank=True, verbose_name="Descrizione")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Servizio"
        verbose_name_plural = "Servizi"
        ordering = ['nome']

class CabinaServizio(models.Model):
    cabina = models.ForeignKey('Cabina', on_delete=models.CASCADE, related_name='servizi_assoc')
    servizio = models.ForeignKey('Servizio', on_delete=models.CASCADE)
    scadenza = models.DateField(verbose_name="Data scadenza")

    def __str__(self):
        return f"{self.servizio.nome} - {self.cabina.matricola} (fino al {self.scadenza})"

    class Meta:
        verbose_name = "Servizio assegnato"
        verbose_name_plural = "Servizi assegnati alle cabine"
        unique_together = ('cabina', 'servizio')  # ogni servizio una sola volta per cabina

def report_image_upload_to(instance, filename):
    """
    Path: reports/<cabina>/<report_id>/<field_name>/<filename>
    """
    cab = getattr(instance.report.cabina, "matricola", instance.report.cabina_id)
    return os.path.join("reports", str(cab), str(instance.report_id), instance.field_name, filename)


class ReportTemplate(models.Model):
    nome = models.CharField(max_length=200)
    descrizione = models.TextField(blank=True)
    frequenza = models.CharField(max_length=20, blank=True)
    versione = models.PositiveIntegerField(default=1)
    attivo = models.BooleanField(default=True)

    # Struttura dinamica del form
    schema = models.JSONField(default=dict)

    creato_da = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="report_template_creati"
    )
    creato_il = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} v{self.versione}"


class ReportCompilato(models.Model):
    manutenzione = models.OneToOneField(
        "ManutenzioneProgrammata", on_delete=models.CASCADE, related_name="report"
    )
    cabina = models.ForeignKey("Cabina", on_delete=models.PROTECT)
    template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT)

    # Copia del template al momento della creazione (versioning)
    schema_snapshot = models.JSONField()
    # Valori compilati (inclusi riferimenti a immagini)
    dati = models.JSONField(default=dict)

    STATO_CHOICES = (("bozza", "Bozza"), ("inviato", "Inviato"))
    stato = models.CharField(max_length=20, choices=STATO_CHOICES, default="bozza")

    compilato_da = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="report_compilati"
    )
    compilato_il = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.pk} - Cabina {self.cabina} - {self.stato}"


class ReportAttachment(models.Model):
    """
    Allegati immagine collegati ai campi di tipo 'image' del report.
    Richiede Pillow: pip install Pillow
    """
    report = models.ForeignKey(ReportCompilato, on_delete=models.CASCADE, related_name="attachments")
    field_name = models.CharField(max_length=100)  # nome 'name' definito nello schema JSON
    file = models.ImageField(
        upload_to=report_image_upload_to,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.field_name} ({self.file.name})"