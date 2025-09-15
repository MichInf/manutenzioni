from django import forms
from django.conf import settings
from .models import (
    Cabina,
    Componente,
    TipoComponente,
    Cliente,
    ManutenzioneProgrammata,
    CabinaServizio,
    PianoManutenzione,
)
from django.forms import BaseFormSet, modelformset_factory
from django.contrib.auth import get_user_model
User = get_user_model()
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome_azienda', 'responsabile', 'telefono_responsabile', 'email', 'email2', 'note', 'attivo']
        widgets = {
            'nome_azienda': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': 'Nome dell\'azienda'
            }),
            'responsabile': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': 'Nome del responsabile'
            }),
            'telefono_responsabile': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': '+39 123 456 7890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': 'email@azienda.com'
            }),
            'email2': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': 'email2@azienda.com (opzionale)'
            }),
            'note': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500 resize-none',
                'rows': 4,
                'placeholder': 'Note aggiuntive sul cliente...'
            }),
            'attivo': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500'
            }),
        }

class CabinaForm(forms.ModelForm):
    FONTE_CHOICES = [
        ('eolico', 'Eolico'),
        ('fotovoltaico', 'Fotovoltaico'),
        ('idroelettrico', 'Idroelettrico'),
        ('passivo', 'Passivo'),
    ]

    fonte = forms.ChoiceField(
        choices=FONTE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
        })
    )
    piano_manutenzione_tipo = forms.ChoiceField(
        choices=PianoManutenzione.Tipo.choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
        }),
        label='Piano manutenzione',
    )
    durata_contrattuale_mesi = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900',
            'min': '1'
        }),
        label='Durata contrattuale (mesi)',
    )
    class Meta:
        model = Cabina
        fields = ['nome', 'matricola', 'cliente', 'fonte', 'guardiania', 'chiave', 'pod', 'telefono_guardiania', 'latitudine', 'longitudine', 'attiva', 'note', 'template_report']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': 'Nome della cabina'
            }),
            'matricola': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': 'Matricola univoca'
            }),
            'cliente': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
            }),
            
            'guardiania': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': 'Nome della guardiania'
            }),
            'chiave': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': 'Codice chiave'
            }),
            'pod': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': 'Codice POD'
            }),
            'telefono_guardiania': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'placeholder': '+39 123 456 7890'
            }),
            'latitudine': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'step': 'any',
                'placeholder': '45.123456'
            }),
            'longitudine': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500',
                'step': 'any',
                'placeholder': '9.123456'
            }),
            'note': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500 resize-none',
                'rows': 4,
                'placeholder': 'Note aggiuntive sulla cabina...'
            }),
            'attiva': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500'
            }),
            'template_report': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
            })
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and hasattr(self.instance, 'piano_manutenzione'):
            piano = self.instance.piano_manutenzione
            self.fields['piano_manutenzione_tipo'].initial = piano.tipo
            self.fields['durata_contrattuale_mesi'].initial = piano.durata_contrattuale_mesi

    def save(self, commit=True):
        cabina = super().save(commit)
        tipo = self.cleaned_data.get('piano_manutenzione_tipo')
        durata = self.cleaned_data.get('durata_contrattuale_mesi')
        if tipo or durata:
            PianoManutenzione.objects.update_or_create(
                cabina=cabina,
                defaults={
                    'tipo': tipo,
                    'durata_contrattuale_mesi': durata,
                },
            )
        return cabina
class ComponenteForm(forms.ModelForm):
    class Meta:
        model = Componente
        fields = ['cabina', 'tipo', 'data_installazione', 'data_ultima_manutenzione', 'attivo', 'note']
        widgets = {
            'data_installazione': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_ultima_manutenzione': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cabina': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class ManutenzioneProgrammataForm(forms.ModelForm):
    class Meta:
        model = ManutenzioneProgrammata
        fields = ['tipo', 'data_programmata', 'operatore', 'note']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
            }),
            'data_programmata': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900',
                'type': 'date'
            }),
            'operatore': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
            }),
            'note': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500 resize-none',
                'rows': 3,
                'placeholder': 'Note sulla manutenzione...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tutti gli utenti come operatori per ora
        self.fields['operatore'].queryset = User.objects.all()
        self.fields['operatore'].empty_label = "Seleziona operatore"



class TipoComponenteForm(forms.ModelForm):
    class Meta:
        model = TipoComponente
        fields = ['nome', 'descrizione', 'intervallo_manutenzione_giorni']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'es. Interruttore'
            }),
            'descrizione': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 3,
                'placeholder': 'Descrizione del tipo di componente'
            }),
            'intervallo_manutenzione_giorni': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'min': '1',
                'placeholder': 'es. 180 (giorni)'
            }),
        }
        labels = {
            'nome': 'Nome Tipo Componente',
            'descrizione': 'Descrizione',
            'intervallo_manutenzione_giorni': 'Intervallo manutenzione (giorni)',
        }

class ManutenzioneCompletataForm(forms.ModelForm):
    class Meta:
        model = ManutenzioneProgrammata
        fields = ['tipo', 'data_completamento', 'operatore', 'note']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
            }),
            
            'data_completamento': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900',
                'type': 'date'
            }),
            'operatore': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
            }),
            'note': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500 resize-none',
                'rows': 3,
                'placeholder': 'Note sulla manutenzione completata...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operatore'].queryset = User.objects.all()
        self.fields['operatore'].empty_label = "Seleziona operatore"
class ModificaManutenzioneProgrammataForm(forms.ModelForm):
    class Meta:
        model = ManutenzioneProgrammata
        fields = ['tipo', 'data_programmata', 'operatore', 'stato', 'note']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
            }),
            'data_programmata': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900',
                'type': 'date'
            }),
            'operatore': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
            }),
            'stato': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900'
            }),
            'note': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none bg-white text-gray-900 placeholder-gray-500 resize-none',
                'rows': 3,
                'placeholder': 'Note sulla manutenzione...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['operatore'].queryset = User.objects.all()
        self.fields['operatore'].empty_label = "Seleziona operatore"

class CabinaServizioForm(forms.ModelForm):
    class Meta:
        model = CabinaServizio
        fields = ['servizio', 'scadenza']
        widgets = {
            'servizio': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500'
            }),
            'scadenza': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500',
                'type': 'date'
            }),
        }

CabinaServizioFormSet = modelformset_factory(
    CabinaServizio,
    form=CabinaServizioForm,
    extra=0,
    can_delete=True
)
def _style_field(field, kind, *, multiple=False):
    base = "mt-1 block w-full rounded-md border border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500 text-sm"
    if kind == "bool":
        field.widget.attrs.update({
            "class": "h-5 w-5 rounded border-gray-300 text-orange-600 focus:ring-orange-500"
        })
    elif kind == "textarea":
        field.widget.attrs.update({"class": base, "rows": "3"})
    elif kind == "image":
        attrs = {"class": base + " min-h-11 py-2.5", "accept": "image/*", "capture": "environment"}
        # il widget per multipli lo hai già creato con ClearableFileInput(multiple=True)
        field.widget.attrs.update(attrs)
    else:
        field.widget.attrs.update({"class": base + " min-h-11 py-2.5"})

def _media_urlize(v: str) -> str:
    """Rende assoluto l'URL dell'immagine rispetto a MEDIA_URL."""
    if not v:
        return v
    if v.startswith("http://") or v.startswith("https://"):
        return v
    # se è già /media/...
    if v.startswith(settings.MEDIA_URL):
        return v
    # se inizia con /reports/... → aggiungi /media
    if v.startswith("/"):
        return settings.MEDIA_URL.rstrip("/") + v
    # se è relativo (es. "reports/...") → prefix con /media/
    return settings.MEDIA_URL.rstrip("/") + "/" + v.lstrip("/")

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultiImageField(forms.Field):
    """Campo per upload multiplo di immagini (accetta lista di file)."""
    widget = MultiFileInput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, data):
        files = data
        if not files:
            files = []
        elif not isinstance(files, (list, tuple)):
            files = [files]
        if self.required and len(files) == 0:
            from django.core.exceptions import ValidationError
            raise ValidationError("Carica almeno una immagine.")
        return files

def build_report_form(schema: dict, *, data=None, files=None, initial=None, relax_file_required: bool = False) -> forms.Form:
    """
    Costruisce un Form dinamico a partire da schema JSON.
    - In GET:  usa initial=report.dati
    - In POST: usa data=request.POST, files=request.FILES
    La form restituita espone:
      - form.sections = [(title, [field_names]), ...]
      - form.bound_sections = [{title, frequency, items:[{item, field, value, note_field}]}]
    """

    fields = {}
    sections_meta = []

    for section in schema.get("sections", []):
        title = section.get("title", "")
        items = section.get("items", [])
        names_in_section = []

        for it in items:
            name = it["name"]
            label = it.get("label", name)
            required = bool(it.get("required", False))
            ftype = it.get("type", "text")
            help_text = it.get("help", "")

            # Campo booleano
            if ftype == "bool":
                field = forms.BooleanField(required=required, label=label, help_text=help_text)
                _style_field(field, "bool")

                # eventuale campo nota
                allow_note = it.get("note") or it.get("note_type") or it.get("note_label") or it.get("note_help")
                if allow_note:
                    note_name = f"{name}__note"
                    note_label = it.get("note_label", "Note")
                    note_help = it.get("note_help", "")
                    note_type = (it.get("note_type") or "textarea").lower()

                    if note_type == "text":
                        note_field = forms.CharField(required=False, label=note_label, help_text=note_help)
                        _style_field(note_field, "text")
                    else:
                        note_field = forms.CharField(
                            required=False,
                            label=note_label,
                            help_text=note_help,
                            widget=forms.Textarea()
                        )
                        _style_field(note_field, "textarea")

                    fields[note_name] = note_field
                    names_in_section.append(note_name)

            elif ftype == "text":
                field = forms.CharField(required=required, label=label, help_text=help_text)
                _style_field(field, "text")

            elif ftype == "textarea":
                field = forms.CharField(
                    required=required,
                    label=label,
                    help_text=help_text,
                    widget=forms.Textarea()
                )
                _style_field(field, "textarea")

            elif ftype == "number":
                field = forms.FloatField(
                    required=required,
                    label=label,
                    help_text=help_text,
                    min_value=it.get("min"),
                    max_value=it.get("max")
                )
                _style_field(field, "number")

            elif ftype == "date":
                field = forms.DateField(
                    required=required,
                    label=label,
                    help_text=help_text,
                    input_formats=["%Y-%m-%d"],
                    widget=forms.DateInput(attrs={"type": "date"})
                )
                _style_field(field, "date")

            elif ftype == "select":
                options = it.get("options", [])
                choices = [(o, o) for o in options]
                if not required:
                    choices = [("", "—")] + choices
                field = forms.ChoiceField(
                    required=required,
                    label=label,
                    help_text=help_text,
                    choices=choices
                )
                _style_field(field, "select")

            elif ftype == "image":
                required_eff = required and not relax_file_required
                if it.get("multiple"):
                    field = MultiImageField(
                        required=required_eff,
                        label=label,
                        help_text=help_text,
                        widget=MultiFileInput(),
                    )
                else:
                    field = forms.ImageField(
                        required=required_eff,
                        label=label,
                        help_text=help_text,
                    )
                field.widget.attrs.update({
                    "class": "mt-1 block w-full rounded-md border border-gray-300 shadow-sm "
                             "focus:border-orange-500 focus:ring-orange-500 text-sm min-h-11 py-2.5",
                    "accept": "image/*",
                })

            else:
                # fallback
                field = forms.CharField(required=required, label=label, help_text=help_text)
                _style_field(field, "text")

            fields[name] = field
            names_in_section.append(name)

        sections_meta.append((title, names_in_section))

    # Costruzione form dinamica
    ReportDynamicForm = type("ReportDynamicForm", (forms.Form,), fields)
    form = ReportDynamicForm(data=data or None, files=files or None, initial=initial)
    form.sections = sections_meta

    # Costruzione bound_sections per il template
    bound_sections = []
    existing = initial or {}

    for sec in schema.get("sections", []):
        bound_items = []
        for it in sec.get("items", []):
            name = it["name"]
            val = existing.get(name)

            # normalizza immagini
            if it.get("type") == "image":
                if val is None:
                    val = []
                elif isinstance(val, (list, tuple)):
                    val = [_media_urlize(x) for x in val]
                else:
                    val = [_media_urlize(val)]

            # eventuale campo nota
            note_field = None
            note_name = f"{name}__note"
            if note_name in form.fields:
                note_field = form[note_name]

            # campo principale
            bound_items.append({
                "item": it,
                "field": form[name],
                "value": val,
                "note_field": note_field,  # collegate al checkbox
            })

        bound_sections.append({
            "title": sec.get("title", ""),
            "frequency": sec.get("frequency", ""),
            "items": bound_items,
        })

    form.bound_sections = bound_sections
    return form
    """
    Costruisce un Form dinamico a partire da schema JSON.
    - In GET:  usa initial=report.dati
    - In POST: usa data=request.POST, files=request.FILES
    La form restituita espone:
      - form.sections = [(title, [field_names]), ...]
      - form.bound_sections = [{title, frequency, items:[{item, field, value}]}]
    """

    fields = {}
    sections_meta = []

    for section in schema.get("sections", []):
        title = section.get("title", "")
        items = section.get("items", [])
        names_in_section = []

        for it in items:
            name = it["name"]
            label = it.get("label", name)
            required = bool(it.get("required", False))
            ftype = it.get("type", "text")
            help_text = it.get("help", "")

            # Campo booleano
            if ftype == "bool":
                field = forms.BooleanField(required=required, label=label, help_text=help_text)
                _style_field(field, "bool")

                # eventuale campo Nota
                allow_note = it.get("note") or it.get("note_type") or it.get("note_label") or it.get("note_help")
                if allow_note:
                    note_name = f"{name}__note"
                    note_label = it.get("note_label", "Note")
                    note_help = it.get("note_help", "")
                    note_type = (it.get("note_type") or "textarea").lower()

                    if note_type == "text":
                        note_field = forms.CharField(required=False, label=note_label, help_text=note_help)
                        _style_field(note_field, "text")
                    else:
                        note_field = forms.CharField(
                            required=False,
                            label=note_label,
                            help_text=note_help,
                            widget=forms.Textarea()
                        )
                        _style_field(note_field, "textarea")

                    fields[note_name] = note_field
                    names_in_section.append(note_name)

            elif ftype == "text":
                field = forms.CharField(required=required, label=label, help_text=help_text)
                _style_field(field, "text")

            elif ftype == "textarea":
                field = forms.CharField(
                    required=required,
                    label=label,
                    help_text=help_text,
                    widget=forms.Textarea()
                )
                _style_field(field, "textarea")

            elif ftype == "number":
                field = forms.FloatField(
                    required=required,
                    label=label,
                    help_text=help_text,
                    min_value=it.get("min"),
                    max_value=it.get("max")
                )
                _style_field(field, "number")

            elif ftype == "date":
                field = forms.DateField(
                    required=required,
                    label=label,
                    help_text=help_text,
                    input_formats=["%Y-%m-%d"],
                    widget=forms.DateInput(attrs={"type": "date"})
                )
                _style_field(field, "date")

            elif ftype == "select":
                options = it.get("options", [])
                choices = [(o, o) for o in options]
                if not required:
                    choices = [("", "—")] + choices
                field = forms.ChoiceField(
                    required=required,
                    label=label,
                    help_text=help_text,
                    choices=choices
                )
                _style_field(field, "select")

            elif ftype == "image":
                required_eff = required and not relax_file_required
                if it.get("multiple"):
                    field = MultiImageField(
                        required=required_eff,
                        label=label,
                        help_text=help_text,
                        widget=MultiFileInput(),
                    )
                else:
                    field = forms.ImageField(
                        required=required_eff,
                        label=label,
                        help_text=help_text,
                    )
                field.widget.attrs.update({
                    "class": "mt-1 block w-full rounded-md border border-gray-300 shadow-sm "
                             "focus:border-orange-500 focus:ring-orange-500 text-sm min-h-11 py-2.5",
                    "accept": "image/*",
                })

            else:
                # fallback
                field = forms.CharField(required=required, label=label, help_text=help_text)
                _style_field(field, "text")

            fields[name] = field
            names_in_section.append(name)

        sections_meta.append((title, names_in_section))

    # Costruzione form dinamica
    ReportDynamicForm = type("ReportDynamicForm", (forms.Form,), fields)
    form = ReportDynamicForm(data=data or None, files=files or None, initial=initial)
    form.sections = sections_meta

    # Costruzione bound_sections per il template
    bound_sections = []
    existing = initial or {}

    for sec in schema.get("sections", []):
        bound_items = []
        for it in sec.get("items", []):
            name = it["name"]
            val = existing.get(name)

            # normalizza immagini
            if it.get("type") == "image":
                if val is None:
                    val = []
                elif isinstance(val, (list, tuple)):
                    val = [_media_urlize(x) for x in val]
                else:
                    val = [_media_urlize(val)]

            # campo principale
            bound_items.append({
                "item": it,
                "field": form[name],
                "value": val,
                "note_field": None,
            })

            # eventuale campo nota
            note_name = f"{name}__note"
            if note_name in form.fields:
                bound_items.append({
                    "item": {
                        "name": note_name,
                        "label": it.get("note_label", "Note"),
                        "type": it.get("note_type", "textarea"),
                        "help": it.get("note_help", "")
                    },
                    "field": form[note_name],
                    "value": existing.get(note_name),
                    "note_field": None
                })

        bound_sections.append({
            "title": sec.get("title", ""),
            "frequency": sec.get("frequency", ""),
            "items": bound_items,
        })

    form.bound_sections = bound_sections
    return form
    fields = {}
    sections_meta = []

    for section in schema.get("sections", []):
        title = section.get("title", "")
        items = section.get("items", [])
        names_in_section = []

        for it in items:
            name = it["name"]
            label = it.get("label", name)
            required = bool(it.get("required", False))
            ftype = it.get("type", "text")
            help_text = it.get("help", "")

            if ftype == "bool":
                field = forms.BooleanField(required=required, label=label, help_text=help_text)
                _style_field(field, "bool")
                allow_note = it.get("note") or it.get("note_type") or it.get("note_label") or it.get("note_help")
                if allow_note:
                    note_name = f"{name}__note"
                    note_label = it.get("note_label", "Note")
                    note_help = it.get("note_help", "")
                    note_type = (it.get("note_type") or "textarea").lower()

                    if note_type == "text":
                        note_field = forms.CharField(required=False, label=note_label, help_text=note_help)
                        _style_field(note_field, "text")
                    else:
                        note_field = forms.CharField(
                            required=False,
                            label=note_label,
                            help_text=note_help,
                            widget=forms.Textarea()
                        )
                        _style_field(note_field, "textarea")

                    fields[note_name] = note_field
                    names_in_section.append(note_name)

            elif ftype == "text":
                field = forms.CharField(required=required, label=label, help_text=help_text)
                _style_field(field, "text")

            elif ftype == "textarea":
                field = forms.CharField(required=required, label=label, help_text=help_text,
                                        widget=forms.Textarea())
                _style_field(field, "textarea")

            elif ftype == "number":
                field = forms.FloatField(required=required, label=label, help_text=help_text,
                                         min_value=it.get("min"), max_value=it.get("max"))
                _style_field(field, "number")

            elif ftype == "date":
                field = forms.DateField(required=required, label=label, help_text=help_text,
                                        input_formats=["%Y-%m-%d"],
                                        widget=forms.DateInput(attrs={"type": "date"}))
                _style_field(field, "date")

            elif ftype == "select":
                options = it.get("options", [])
                choices = [(o, o) for o in options]
                if not required:
                    choices = [("", "—")] + choices
                field = forms.ChoiceField(required=required, label=label, help_text=help_text, choices=choices)
                _style_field(field, "select")

            elif ftype == "image":
                required_eff = required and not relax_file_required
                if it.get("multiple"):
                    # widget che supporta multiple upload
                    field = MultiImageField(
                        required=required_eff,
                        label=label,
                        help_text=help_text,
                        widget=MultiFileInput(),
                    )
                else:
                    # singola immagine (ClearableFileInput va bene di default)
                    field = forms.ImageField(
                        required=required_eff,
                        label=label,
                        help_text=help_text,
                    )
                # stile + hint mobile (valido per entrambi i casi)
                field.widget.attrs.update({
                    "class": "mt-1 block w-full rounded-md border border-gray-300 shadow-sm "
                            "focus:border-orange-500 focus:ring-orange-500 text-sm min-h-11 py-2.5",
                    "accept": "image/*",
                })

            else:
                # fallback per tipi non riconosciuti
                field = forms.CharField(required=required, label=label, help_text=help_text)
                _style_field(field, "text")

            fields[name] = field
            names_in_section.append(name)

        sections_meta.append((title, names_in_section))

    ReportDynamicForm = type("ReportDynamicForm", (forms.Form,), fields)
    form = ReportDynamicForm(data=data or None, files=files or None, initial=initial)
    form.sections = sections_meta

    bound_sections = []
    existing = initial or {}

    for sec in schema.get("sections", []):
        bound_items = []
        for it in sec.get("items", []):
            name = it["name"]
            val = existing.get(name)

            # normalizza le immagini: sempre LISTA di URL assoluti verso MEDIA_URL
            if it.get("type") == "image":
                if val is None:
                    val = []
                elif isinstance(val, (list, tuple)):
                    val = [_media_urlize(x) for x in val]
                else:
                    val = [_media_urlize(val)]
            note_field = None
        note_name = f"{name}__note"
        if note_name in form.fields:
            note_field = form[note_name]

        bound_items.append({
            "item": it,
            "field": form[name],
            "value": val,
            "note_field": None   # solo il campo principale
        })

        # Se esiste un campo note, aggiungilo come item separato
        note_name = f"{name}__note"
        if note_name in form.fields:
            bound_items.append({
                "item": {
                    "name": note_name,
                    "label": it.get("note_label", "Note"),
                    "type": it.get("note_type", "textarea"),
                    "help": it.get("note_help", "")
                },
                "field": form[note_name],
                "value": existing.get(note_name),
                "note_field": None
            })
        bound_sections.append({
            "title": sec.get("title", ""),
            "frequency": sec.get("frequency", ""),
            "items": bound_items,
        })
    form.bound_sections = bound_sections
    return form
    """
    Costruisce un Form dinamico a partire da schema JSON.
    - In GET:  usa initial=report.dati
    - In POST: usa data=request.POST, files=request.FILES
    La form restituita espone `form.sections` = [(title, [field_names]), ...]
    per rendere le intestazioni di sezione nel template.
    """
    fields = {}
    sections_meta = []

    for section in schema.get("sections", []):
        title = section.get("title", "")
        items = section.get("items", [])
        names_in_section = []

        for it in items:
            name = it["name"]
            label = it.get("label", name)
            required = bool(it.get("required", False))
            ftype = it.get("type", "text")
            help_text = it.get("help", "")

            if ftype == "bool":
                # Nota: required=True per checkbox significa "deve essere spuntato"
                field = forms.BooleanField(required=required, label=label, help_text=help_text)

            elif ftype == "text":
                field = forms.CharField(required=required, label=label, help_text=help_text)

            elif ftype == "textarea":
                field = forms.CharField(
                    required=required, label=label, help_text=help_text,
                    widget=forms.Textarea(attrs={"rows": 3})
                )

            elif ftype == "number":
                min_v = it.get("min", None)
                max_v = it.get("max", None)
                field = forms.FloatField(
                    required=required, label=label, help_text=help_text,
                    min_value=min_v, max_value=max_v
                )

            elif ftype == "date":
                field = forms.DateField(
                    required=required, label=label, help_text=help_text,
                    input_formats=["%Y-%m-%d"],
                    widget=forms.DateInput(attrs={"type": "date"})
                )

            elif ftype == "select":
                options = it.get("options", [])
                choices = [(o, o) for o in options]
                if not required:
                    choices = [("", "—")] + choices
                field = forms.ChoiceField(required=required, label=label, help_text=help_text, choices=choices)

            elif ftype == "image":
                if it.get("multiple"):
                    field = forms.FileField(
                        required=required, label=label, help_text=help_text,
                        widget=forms.ClearableFileInput(attrs={"multiple": True, "accept": "image/*"})
                    )
                else:
                    field = forms.ImageField(required=required, label=label, help_text=help_text)
                    # hint browser
                    field.widget.attrs.update({"accept": "image/*"})

            else:
                # fallback a text
                field = forms.CharField(required=required, label=label, help_text=help_text)

            fields[name] = field
            names_in_section.append(name)

        sections_meta.append((title, names_in_section))

    # Creiamo una Form dinamica con i campi definiti sopra.
    ReportDynamicForm = type("ReportDynamicForm", (forms.Form,), fields)
    form = ReportDynamicForm(
        data=data if data is not None else None,
        files=files if files is not None else None,
        initial=initial
    )
    # Metadati per il template (render delle sezioni)
    form.sections = sections_meta
    bound_sections = []
    existing = initial or {}  # usa i dati già salvati nel report per le anteprime

    for sec in schema.get("sections", []):
        bound_items = []
        for it in sec.get("items", []):
            name = it["name"]
            val = existing.get(name)
            # Normalizza: salva sempre una LISTA per le immagini
            if it.get("type") == "image":
                if val is None:
                    val = []
                elif not isinstance(val, (list, tuple)):
                    val = [val]
            bound_items.append({
                "item": it,           # definizione campo (label, type, etc.)
                "field": form[name],  # BoundField
                "value": val,         # valore già pronto per il template
            })
        bound_sections.append({
            "title": sec.get("title", ""),
            "frequency": sec.get("frequency", ""),
            "items": bound_items,
        })

    form.bound_sections = bound_sections
    return form