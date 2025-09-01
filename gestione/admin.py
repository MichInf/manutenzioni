from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import TipoComponente, Cliente, Cabina, Componente, Servizio, CabinaServizio, ManutenzioneProgrammata, ReportTemplate, ReportCompilato, ReportAttachment
from django import forms
class CabinaAdminForm(forms.ModelForm):
    FONTE_SCELTE = [
        ('eolico', 'Eolico'),
        ('fotovoltaico', 'Fotovoltaico'),
        ('idroelettrico', 'Idroelettrico'),
        ('passivo', 'Passivo'),
    ]
    fonte = forms.ChoiceField(choices=FONTE_SCELTE, required=False)

    class Meta:
        model = Cabina
        fields = '__all__'
@admin.register(TipoComponente)
class TipoComponenteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descrizione', 'intervallo_manutenzione_giorni')
    search_fields = ('nome',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_azienda', 'responsabile', 'telefono_responsabile', 'email', 'numero_cabine', 'attivo')
    list_filter = ('attivo',)
    search_fields = ('nome_azienda', 'responsabile', 'email')

@admin.register(Cabina)
class CabinaAdmin(admin.ModelAdmin):
    form = CabinaAdminForm
    list_display = ('matricola', 'nome', 'cliente', 'guardiania', 'attiva','template_report')
    list_filter = ('attiva', 'cliente')
    search_fields = ('matricola', 'nome', 'cliente__nome_azienda', 'pod')

@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'cabina', 'data_installazione', 'attivo')
    list_filter = ('tipo', 'attivo', 'cabina')
    search_fields = ('cabina__matricola', 'tipo__nome')

@admin.register(Servizio)
class ServizioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descrizione')
    search_fields = ('nome',)

@admin.register(CabinaServizio)
class CabinaServizioAdmin(admin.ModelAdmin):
    list_display = ('cabina', 'servizio', 'scadenza')
    list_filter = ('servizio', 'scadenza')
    search_fields = ('cabina__matricola', 'servizio__nome')
@admin.register(ManutenzioneProgrammata)
class ManutenzioneProgrammataAdmin(admin.ModelAdmin):
    list_display = ("cabina", "tipo", "data_programmata", "data_completamento", "stato")
    list_filter = ("stato", "tipo", "data_programmata", "data_completamento", "cabina")
    search_fields = ("cabina__matricola", "cabina__nome", "tipo", "stato")
    date_hierarchy = "data_programmata"

SCHEMA_SKELETON = {
    "sections": [
        {
            "title": "Nuova sezione",
            "frequency": "",
            "items": [
                {"name": "esempio_bool", "label": "Esempio Bool", "type": "bool", "required": False}
            ]
        }
    ]
}

def validate_schema(schema: dict):
    """Validazione minima della struttura dello schema."""
    if not isinstance(schema, dict):
        raise ValidationError("Lo schema deve essere un oggetto JSON (dict).")
    sections = schema.get("sections")
    if not isinstance(sections, list) or not sections:
        raise ValidationError("schema.sections deve essere una lista non vuota.")
    for sec in sections:
        if "title" not in sec or "items" not in sec:
            raise ValidationError("Ogni sezione deve avere 'title' e 'items'.")
        if not isinstance(sec["items"], list):
            raise ValidationError("section.items deve essere una lista.")
        for it in sec["items"]:
            for key in ("name", "label", "type"):
                if key not in it:
                    raise ValidationError(f"Ogni item richiede '{key}'.")
            if it["type"] == "select" and "options" not in it:
                raise ValidationError(f"Il campo select '{it['name']}' richiede 'options'.")
            if it["type"] == "image" and "multiple" in it and not isinstance(it["multiple"], bool):
                raise ValidationError(f"Il campo image '{it['name']}' ha 'multiple' non booleano.")

class ReportTemplateForm(forms.ModelForm):
    class Meta:
        model = ReportTemplate
        fields = "__all__"
        help_texts = {
            "schema": (
                "Struttura: { sections: [ { title, frequency, items: [ { name, label, type, ... } ] } ] }.\n"
                "Tipi supportati: bool, text, textarea, number(min/max), date, select(options), image(multiple?)."
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Precompila lo schema quando crei un nuovo template
        if not self.instance.pk and not self.initial.get("schema"):
            self.initial["schema"] = SCHEMA_SKELETON

    def clean_schema(self):
        s = self.cleaned_data.get("schema")
        validate_schema(s)
        return s


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    form = ReportTemplateForm
    list_display = ("nome", "frequenza", "versione", "attivo", "creato_il")
    list_filter = ("attivo", "frequenza", "versione", "creato_il")
    search_fields = ("nome", "descrizione")

    actions = ["duplica_template"]

    def duplica_template(self, request, queryset):
        """Crea una copia dei template selezionati (non attiva) incrementando la versione."""
        created = 0
        for t in queryset:
            clone = ReportTemplate(
                nome=f"{t.nome} (copia)",
                descrizione=t.descrizione,
                frequenza=t.frequenza,
                versione=t.versione + 1,
                attivo=False,
                schema=t.schema,
                creato_da=request.user,  # l'admin che duplica diventa creatore della copia
            )
            try:
                validate_schema(clone.schema)
                clone.full_clean()
                clone.save()
                created += 1
            except ValidationError as e:
                self.message_user(request, f"Errore duplicazione '{t}': {e}", level="error")
        self.message_user(request, f"Duplicati {created} template. Modificali e attivali quando pronti.")
    duplica_template.short_description = "Duplica template selezionati"


class ReportAttachmentInline(admin.TabularInline):
    model = ReportAttachment
    extra = 0
    readonly_fields = ("uploaded_by", "uploaded_at")
    fields = ("field_name", "file", "uploaded_by", "uploaded_at")


@admin.register(ReportCompilato)
class ReportCompilatoAdmin(admin.ModelAdmin):
    list_display = ("id", "cabina", "template", "stato", "compilato_da", "compilato_il")
    list_filter = ("stato", "compilato_il", "template")
    search_fields = ("cabina__matricola", "template__nome")
    readonly_fields = ("manutenzione", "cabina", "template", "schema_snapshot", "compilato_da", "compilato_il")
    inlines = [ReportAttachmentInline]


@admin.register(ReportAttachment)
class ReportAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "report", "field_name", "uploaded_by", "uploaded_at")
    search_fields = ("field_name", "report__cabina__matricola")
    list_filter = ("uploaded_at",)