from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.db.models import Case, When, Value, IntegerField,Q
from .models import Cabina, Componente, TipoComponente, Cliente, ManutenzioneProgrammata, CabinaServizio, Servizio ,ReportTemplate, ReportCompilato, ReportAttachment, Alert
from .forms import (CabinaForm, ComponenteForm, TipoComponenteForm, ClienteForm, ManutenzioneProgrammataForm, ManutenzioneCompletataForm, ModificaManutenzioneProgrammataForm, CabinaServizioFormSet, build_report_form)
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.core.files.storage import default_storage
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from .models import ManutenzioneProgrammata

@login_required
def calendario_manutenzioni(request):
    manutenzioni = ManutenzioneProgrammata.objects.filter(stato='programmata')
    events = []

    for m in manutenzioni:
        events.append({
            "title": f"{m.get_tipo_display()} - {m.cabina.matricola}",
            "start": m.data_programmata.strftime("%Y-%m-%d"),
            "url": reverse('dettaglio_cabina', kwargs={'matricola': m.cabina.matricola}) + '#tab-manutenzioni'
        })

    return JsonResponse(events, safe=False)

@csrf_exempt
@login_required
def crea_servizio_ajax(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descrizione = request.POST.get('descrizione', '')

        if nome:
            servizio, created = Servizio.objects.get_or_create(nome=nome, defaults={'descrizione': descrizione})
            return JsonResponse({'success': True, 'id': servizio.id, 'nome': servizio.nome})
        else:
            return JsonResponse({'success': False, 'error': 'Nome mancante'})

    return JsonResponse({'success': False, 'error': 'Metodo non valido'})


@login_required
def dashboard(request):
    user = request.user
    
    # Statistiche generali
    total_cabine = Cabina.objects.filter(attiva=True).count()
    total_componenti = Componente.objects.filter(attivo=True).count()
    
    # Alert per scadenze
    cabine_scadute = []
    cabine_in_scadenza = []
    componenti_scaduti = []
    componenti_in_scadenza = []
    
    for cabina in Cabina.objects.filter(attiva=True):
        stato = cabina.stato_manutenzione_ordinaria()
        if stato == 'scaduta':
            cabine_scadute.append(cabina)
        elif stato == 'in_scadenza':
            cabine_in_scadenza.append(cabina)
    
    for componente in Componente.objects.filter(attivo=True):
        stato = componente.stato_manutenzione()
        if stato == 'scaduta':
            componenti_scaduti.append(componente)
        elif stato == 'in_scadenza':
            componenti_in_scadenza.append(componente)
    
    context = {
        'total_cabine': total_cabine,
        'total_componenti': total_componenti,
        'cabine_scadute': len(cabine_scadute),
        'cabine_in_scadenza': len(cabine_in_scadenza),
        'componenti_scaduti': len(componenti_scaduti),
        'componenti_in_scadenza': len(componenti_in_scadenza),
        'alert_totali': len(cabine_scadute) + len(cabine_in_scadenza) + len(componenti_scaduti) + len(componenti_in_scadenza),
    }
    
    if user.is_administrator():
        return render(request, 'dashboard_admin.html', context)
    elif user.is_controlroom():
        return render(request, 'dashboard_controlroom.html', context)
    elif user.is_operatore():
        return render(request, 'dashboard_operatore.html', context)
    else:
        return redirect('login')

@login_required
def lista_cabine(request):
    sort = request.GET.get('sort', 'matricola')
    direction = request.GET.get('direction', 'asc')
    search = request.GET.get('q', '')  # <- nuova barra ricerca

    qs = Cabina.objects.filter(attiva=True)

    # 🔍 Filtra se presente testo di ricerca
    if search:
        qs = qs.filter(
            Q(matricola__icontains=search) |
            Q(nome__icontains=search)
        )

    # Ordinamento DB solo per matricola o nome
    if sort in {'matricola', 'nome'}:
        order_by = sort if direction == 'asc' else f'-{sort}'
        qs = qs.order_by(order_by)
    else:
        qs = qs.order_by('matricola')

    # Materializza e calcola attributi derivati
    cabine = list(qs)
    for cabina in cabine:
        cabina.stato_ordinaria = cabina.stato_manutenzione_ordinaria()
        cabina.giorni_ordinaria = cabina.giorni_alla_manutenzione_ordinaria()
        cabina.componenti_ok = cabina.componenti_scadenza = cabina.componenti_scaduti = 0
        for comp in cabina.componenti.filter(attivo=True):
            stato = comp.stato_manutenzione()
            if stato == 'ok': cabina.componenti_ok += 1
            elif stato == 'in_scadenza': cabina.componenti_scadenza += 1
            elif stato == 'scaduta': cabina.componenti_scaduti += 1

    if sort == 'stato_ordinaria':
        order = {'ok': 1, 'in_scadenza': 2, 'scaduta': 3}
        cabine.sort(
            key=lambda c: order.get(c.stato_ordinaria, 99),
            reverse=(direction == 'desc')
        )

    headers = [
        ('matricola', 'Matricola'),
        ('nome', 'Nome'),
        ('stato_ordinaria', 'Manutenzione Ordinaria'),
    ]

    return render(request, 'cabine/lista.html', {
        'cabine': cabine,
        'sort': sort,
        'direction': direction,
        'headers': headers,
        'search': search,  # <- passo anche nel context
    })


from django.db.models import BooleanField, Case, When, Value

@login_required
def dettaglio_cabina(request, matricola):
    cabina = get_object_or_404(Cabina, matricola=matricola, attiva=True)
    componenti = cabina.componenti.filter(attivo=True)
    today = timezone.localdate()

    for componente in componenti:
        componente.stato = componente.stato_manutenzione()
        componente.giorni = componente.giorni_alla_manutenzione()
        componente.prossima = componente.prossima_manutenzione()

    manutenzioni = (
        cabina.manutenzioni
        .annotate(
            is_aperta=Case(
                When(stato__in=['programmata', 'in_corso'], then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        .order_by('-is_aperta', '-data_completamento')  # aperte sopra, poi completate per data
    )

    context = {
        'cabina': cabina,
        'componenti': componenti,
        'manutenzioni': manutenzioni,
        'stato_ordinaria': cabina.stato_manutenzione_ordinaria(),
        'giorni_ordinaria': cabina.giorni_alla_manutenzione_ordinaria(),
        'prossima_ordinaria': cabina.prossima_manutenzione_ordinaria(),
        'today': today
    }
    return render(request, 'cabine/dettaglio.html', context)

@login_required
def lista_alert(request):
    # Query sul modello Alert
    alert_qs = Alert.objects.filter(silenziato=False)

    # Se l'alert è stato posticipato, usa quella data al posto della scadenza
    today = timezone.localdate()
    alert_qs = alert_qs.annotate(
        giorni=Case(
            When(posticipato_a__isnull=False,
                 then=F('posticipato_a') - Value(today)),
            default=F('scadenza') - Value(today),
            output_field=IntegerField()
        )
    )

    # Ordina: prima i critici, poi per scadenza crescente
    alert_qs = alert_qs.order_by(
        Case(
            When(priorita="critica", then=0),
            When(priorita="alta", then=1),
            default=2,
            output_field=IntegerField()
        ),
        'scadenza'
    )

    return render(request, 'alert/lista.html', {'alert': alert_qs})

@login_required
def silenzia_alert(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    alert.silenziato = True
    alert.save()
    messages.success(request, "Alert silenziato con successo 🔕")
    return redirect("lista_alert")


@login_required
def posticipa_alert(request, pk):
    alert = get_object_or_404(Alert, pk=pk)
    if request.method == "POST":
        nuova_data = request.POST.get("nuova_scadenza")
        if nuova_data:
            alert.posticipato_a = nuova_data
            alert.save()
            messages.success(request, f"Alert posticipato al {nuova_data} ⏰")
            return redirect("lista_alert")
    return render(request, "alert/posticipa_form.html", {"alert": alert})



def _parse_servizi_from_post(request):
    """
    Ritorna (pairs, errors) dove:
      - pairs = [(servizio_id:int, scadenza:date), ...]
      - errors = [str, ...]
    Supporta sia i nuovi campi (servizio[]/scadenza[]) sia i vecchi (form-TEMPID-...).
    """
    ids = request.POST.getlist('servizio[]') or request.POST.getlist('form-TEMPID-servizio')
    dates = request.POST.getlist('scadenza[]') or request.POST.getlist('form-TEMPID-scadenza')

    pairs, errors = [], []
    for idx, (sid, sdate) in enumerate(zip(ids, dates), start=1):
        if not sid and not sdate:
            continue
        if not sid or not sdate:
            errors.append(f"Riga {idx}: seleziona sia il servizio che la scadenza.")
            continue
        try:
            sid_int = int(sid)
        except ValueError:
            errors.append(f"Riga {idx}: servizio non valido.")
            continue
        try:
            date_obj = datetime.strptime(sdate, "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"Riga {idx}: data scadenza non valida.")
            continue

        # (opzionale) vieta date nel passato
        if date_obj < timezone.now().date():
            errors.append(f"Riga {idx}: la scadenza non può essere nel passato.")
            continue

        pairs.append((sid_int, date_obj))

    # dedup per servizio: tiene l'ultima occorrenza nel form
    dedup = {}
    for sid, d in pairs:
        dedup[sid] = d
    pairs = [(sid, dedup[sid]) for sid in dedup.keys()]
    return pairs, errors

@login_required
def crea_cabina(request):
    if not (request.user.is_administrator() or request.user.is_controlroom()):
        messages.error(request, "Non hai i permessi per creare cabine.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CabinaForm(request.POST)
        pairs, servizi_errors = _parse_servizi_from_post(request)

        if form.is_valid() and not servizi_errors:
            with transaction.atomic():
                cabina = form.save()

                # crea i legami CabinaServizio
                objs = [
                    CabinaServizio(cabina=cabina, servizio_id=sid, scadenza=dt)
                    for sid, dt in pairs
                ]
                try:
                    CabinaServizio.objects.bulk_create(objs)
                except IntegrityError:
                    # fallback (ad es. unique_together violata per post duplicati)
                    for o in objs:
                        CabinaServizio.objects.update_or_create(
                            cabina=o.cabina, servizio_id=o.servizio_id,
                            defaults={'scadenza': o.scadenza}
                        )

            messages.success(request, f"Cabina {cabina.matricola} creata con successo!")
            return redirect('dettaglio_cabina', matricola=cabina.matricola)

        # errori: mostra messaggi e ricadi sul render
        if servizi_errors:
            for e in servizi_errors:
                messages.error(request, e)
    else:
        form = CabinaForm()

    context = {
        'form': form,
        'today': timezone.now().date(),
        'servizi_options': Servizio.objects.all().order_by('nome'),
        'servizi_initial': [],  # nessun prefill in "Crea"
    }
    # alias per compatibilità con template che usano "servizi"
    context['servizi'] = context['servizi_options']
    return render(request, 'cabine/crea.html', context)

@login_required
def modifica_cabina(request, matricola):
    if not (request.user.is_administrator() or request.user.is_controlroom()):
        messages.error(request, "Non hai i permessi per modificare cabine.")
        return redirect('dashboard')

    cabina = get_object_or_404(Cabina, matricola=matricola)

    if request.method == 'POST':
        form = CabinaForm(request.POST, instance=cabina)
        pairs, servizi_errors = _parse_servizi_from_post(request)

        if form.is_valid() and not servizi_errors:
            with transaction.atomic():
                cabina = form.save()

                # strategia semplice: rimpiazzo completo delle righe servizi
                CabinaServizio.objects.filter(cabina=cabina).delete()
                objs = [
                    CabinaServizio(cabina=cabina, servizio_id=sid, scadenza=dt)
                    for sid, dt in pairs
                ]
                try:
                    CabinaServizio.objects.bulk_create(objs)
                except IntegrityError:
                    for o in objs:
                        CabinaServizio.objects.update_or_create(
                            cabina=o.cabina, servizio_id=o.servizio_id,
                            defaults={'scadenza': o.scadenza}
                        )

            messages.success(request, f"Cabina {cabina.matricola} modificata con successo!")
            return redirect('dettaglio_cabina', matricola=cabina.matricola)

        # errori: segnala
        if servizi_errors:
            for e in servizi_errors:
                messages.error(request, e)

        # se il form non è valido o ci sono errori servizi, ripopola dal POST
        servizi_initial = [
            {"servizio": sid, "scadenza": dt.strftime("%Y-%m-%d")}
            for sid, dt in pairs
        ]
    else:
        form = CabinaForm(instance=cabina)
        servizi_initial = [
            {"servizio": cs.servizio_id, "scadenza": cs.scadenza.strftime("%Y-%m-%d")}
            for cs in cabina.servizi_assoc.all()
        ]

    context = {
        'form': form,
        'cabina': cabina,
        'today': timezone.now().date(),
        'servizi_options': Servizio.objects.all().order_by('nome'),
        'servizi_initial': servizi_initial,
    }
    # alias per compatibilità con template che usano "servizi"
    context['servizi'] = context['servizi_options']
    return render(request, 'cabine/modifica.html', context)

@login_required
def aggiungi_componente(request, matricola):
    # Solo Administrator e Controlroom possono aggiungere componenti
    if not (request.user.is_administrator() or request.user.is_controlroom()):
        messages.error(request, "Non hai i permessi per aggiungere componenti.")
        return redirect('dashboard')
    
    cabina = get_object_or_404(Cabina, matricola=matricola)
    
    if request.method == 'POST':
        form = ComponenteForm(request.POST)
        if form.is_valid():
            componente = form.save(commit=False)
            componente.cabina = cabina
            componente.save()
            messages.success(request, f"Componente {componente.tipo.nome} aggiunto alla cabina {cabina.matricola}!")
            return redirect('dettaglio_cabina', matricola=cabina.matricola)
    else:
        form = ComponenteForm()
    
    return render(request, 'componenti/aggiungi.html', {'form': form, 'cabina': cabina})

@login_required
def modifica_componente(request, componente_id):
    # Solo Administrator e Controlroom possono modificare componenti
    if not (request.user.is_administrator() or request.user.is_controlroom()):
        messages.error(request, "Non hai i permessi per modificare componenti.")
        return redirect('dashboard')
    
    componente = get_object_or_404(Componente, id=componente_id)
    
    if request.method == 'POST':
        form = ComponenteForm(request.POST, instance=componente)
        if form.is_valid():
            componente = form.save()
            messages.success(request, f"Componente modificato con successo!")
            return redirect('dettaglio_cabina', matricola=componente.cabina.matricola)
    else:
        form = ComponenteForm(instance=componente)
    
    return render(request, 'componenti/modifica.html', {'form': form, 'componente': componente})

@login_required
def elimina_componente(request, componente_id):
    # Solo Administrator e Controlroom possono eliminare componenti
    if not (request.user.is_administrator() or request.user.is_controlroom()):
        messages.error(request, "Non hai i permessi per eliminare componenti.")
        return redirect('dashboard')
    
    componente = get_object_or_404(Componente, id=componente_id)
    cabina_matricola = componente.cabina.matricola
    
    if request.method == 'POST':
        componente.delete()
        messages.success(request, "Componente eliminato con successo!")
        return redirect('dettaglio_cabina', matricola=cabina_matricola)
    
    return render(request, 'componenti/elimina.html', {'componente': componente})

@login_required
def lista_clienti(request):
    clienti = Cliente.objects.filter(attivo=True).order_by('nome_azienda')
    return render(request, 'clienti/lista.html', {'clienti': clienti})

@login_required
def dettaglio_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    cabine = cliente.cabine.filter(attiva=True)
    return render(request, 'clienti/dettaglio.html', {'cliente': cliente, 'cabine': cabine})

@login_required
def crea_cliente(request):
    if not (request.user.is_administrator() or request.user.is_controlroom()):
        messages.error(request, "Non hai i permessi.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f"Cliente {cliente.nome_azienda} creato!")
            return redirect('dettaglio_cliente', cliente_id=cliente.id)
    else:
        form = ClienteForm()
    
    return render(request, 'clienti/crea.html', {'form': form})

@login_required
def modifica_cliente(request, cliente_id):
    if not (request.user.is_administrator() or request.user.is_controlroom()):
        messages.error(request, "Non hai i permessi.")
        return redirect('dashboard')

    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f"Cliente {cliente.nome_azienda} modificato!")
            return redirect('dettaglio_cliente', cliente_id=cliente.id)
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clienti/modifica.html', {'form': form, 'cliente': cliente})

@login_required
def programma_manutenzione(request, matricola):
    if not (request.user.is_administrator() or request.user.is_controlroom()):
        messages.error(request, "Non hai i permessi.")
        return redirect('dashboard')
    
    cabina = get_object_or_404(Cabina, matricola=matricola)
    
    if request.method == 'POST':
        form = ManutenzioneProgrammataForm(request.POST)
        if form.is_valid():
            manutenzione = form.save(commit=False)
            manutenzione.cabina = cabina
            manutenzione.creata_da = request.user
            manutenzione.save()
            messages.success(request, f"Manutenzione {manutenzione.get_tipo_display()} programmata per {manutenzione.data_programmata}!")
            return redirect(reverse('dettaglio_cabina', kwargs={'matricola': cabina.matricola}) + '#tab-manutenzioni')
    else:
        form = ManutenzioneProgrammataForm()
    
    return render(request, 'manutenzioni/programma.html', {'form': form, 'cabina': cabina})

@login_required
def completa_manutenzione(request, pk):
    if request.method != "POST":
        messages.error(request, "Richiesta non valida.")
        return redirect('dashboard')

    manut = get_object_or_404(ManutenzioneProgrammata, pk=pk)
    url = reverse('dettaglio_cabina', kwargs={'matricola': manut.cabina.matricola})

    if manut.stato == "completata":
        messages.info(request, "Questa manutenzione risulta già completata.")
        return redirect(f"{url}#tab-manutenzioni")

    # data completamento
    date_str = request.POST.get("data_completamento")
    if date_str:
        try:
            data_compl = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Formato data non valido (YYYY-MM-DD).")
            return redirect(f"{url}#tab-manutenzioni")
    else:
        data_compl = timezone.localdate()

    # salva chiusura
    manut.stato = "completata"
    manut.data_completamento = data_compl
    manut.operatore = request.user
    manut.save()

    # ======= NUOVA LOGICA =======
    piano = getattr(manut.cabina, "piano_manutenzione", None)

    if piano:
        if piano.tipo == "semestrale_annuale":
            # alterna
            next_tipo = "annuale" if manut.tipo == "semestrale" else "semestrale"
            giorni = 182 
            ManutenzioneProgrammata.objects.create(
                cabina=manut.cabina,
                creata_da=request.user,
                tipo=next_tipo,
                data_programmata=data_compl + timedelta(days=giorni),
            )

        elif piano.tipo == "annuale_only":
            # sempre annuale
            ManutenzioneProgrammata.objects.create(
                cabina=manut.cabina,
                creata_da=request.user,
                tipo="annuale",
                data_programmata=data_compl + timedelta(days=365),
            )

        elif piano.tipo == "mensile_lite_annuale":
            if manut.tipo == "annuale":
                # dopo un’annuale: 11 mensili + 1 annuale
                for i in range(1, 12):
                    ManutenzioneProgrammata.objects.create(
                        cabina=manut.cabina,
                        creata_da=request.user,
                        tipo="mensile",
                        data_programmata=data_compl + relativedelta(months=i),
                    )
                ManutenzioneProgrammata.objects.create(
                    cabina=manut.cabina,
                    creata_da=request.user,
                    tipo="annuale",
                    data_programmata=data_compl + relativedelta(years=1),
                )
            # se sto completando un mensile, non genero nulla

        elif piano.tipo == "spot":
            # nessuna nuova manutenzione
            pass

    messages.success(request, "Manutenzione segnata come completata.")
    return redirect(f"{url}#tab-manutenzioni")

@login_required
def registra_manutenzione_completata(request, matricola):
    if not (request.user.is_administrator() or request.user.is_controlroom()):
        messages.error(request, "Non hai i permessi.")
        return redirect('dashboard')
    
    cabina = get_object_or_404(Cabina, matricola=matricola)
    
    if request.method == 'POST':
        form = ManutenzioneCompletataForm(request.POST)
        if form.is_valid():
            manutenzione = form.save(commit=False)
            manutenzione.cabina = cabina
            manutenzione.creata_da = request.user
            manutenzione.data_programmata = manutenzione.data_completamento
            manutenzione.stato = 'completata'
            manutenzione.save()
            messages.success(request, f"Manutenzione {manutenzione.get_tipo_display()} registrata come completata!")
            return redirect(reverse('dettaglio_cabina', kwargs={'matricola': cabina.matricola}) + '#tab-manutenzioni')
        else:
            print(form.errors)
    else:
        form = ManutenzioneCompletataForm()
    
    return render(request, 'manutenzioni/registra_completata.html', {'form': form, 'cabina': cabina})
@login_required
def modifica_manutenzione(request, manutenzione_id):
    if not (request.user.is_administrator() or request.user.is_controlroom()):
        messages.error(request, "Non hai i permessi.")
        return redirect('dashboard')
    
    manutenzione = get_object_or_404(ManutenzioneProgrammata, id=manutenzione_id)
    
    if request.method == 'POST':
        form = ModificaManutenzioneProgrammataForm(request.POST, instance=manutenzione)
        if form.is_valid():
            form.save()
            messages.success(request, f"Manutenzione {manutenzione.get_tipo_display()} modificata!")
            return redirect(reverse('dettaglio_cabina', kwargs={'matricola': manutenzione.cabina.matricola}) + '#tab-manutenzioni')
    else:
        form = ModificaManutenzioneProgrammataForm(instance=manutenzione)
    
    return render(request, 'manutenzioni/modifica_manutenzione.html', {
        'form': form, 
        'manutenzione': manutenzione,
        'cabina': manutenzione.cabina
    })
@login_required
def rinnova_servizio(request, servizio_id):
    cs = get_object_or_404(CabinaServizio, pk=servizio_id)

    if request.method != "POST":
        messages.error(request, "Richiesta non valida.")
        return redirect("dettaglio_cabina", matricola=cs.cabina.matricola)

    new_date_str = request.POST.get("new_date", "").strip()
    try:
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        messages.error(request, "Data non valida.")
        return redirect("dettaglio_cabina", matricola=cs.cabina.matricola)

    if new_date < timezone.localdate():
        messages.error(request, "La nuova scadenza non può essere nel passato.")
        return redirect("dettaglio_cabina", matricola=cs.cabina.matricola)

    cs.scadenza = new_date
    cs.save()
    messages.success(request, f"Nuova scadenza impostata al {cs.scadenza:%d/%m/%Y}.")
    return redirect("dettaglio_cabina", matricola=cs.cabina.matricola)


# Helpers di permesso (adatta ai tuoi metodi/ruoli)
def _can_fill_reports(user):
    return getattr(user, "is_administrator", lambda: False)() or getattr(user, "is_controlroom", lambda: False)()

# Selezione template con priorità: cabina+frequenza → cabina → frequenza → generico
def seleziona_template(cabina, frequenza: str | None):
    return getattr(cabina, "template_report", None)


@login_required
@transaction.atomic
def report_compila(request, pk):
    """
    Crea/edita il ReportCompilato per una ManutenzioneProgrammata (pk).
    - GET:   mostra la form (initial = report.dati) con anteprime
    - POST:  salva dati non-file e immagini (URL in lista)
    """
    from .models import ManutenzioneProgrammata  # importa dal modulo corretto
    manut = get_object_or_404(ManutenzioneProgrammata, pk=pk)

    # permessi
    if not _can_fill_reports(request.user):  # implementato da te
        messages.error(request, "Non hai i permessi per compilare report.")
        return redirect('dettaglio_cabina', matricola=manut.cabina.matricola)

    frequenza = getattr(manut, "tipo", "")  # "semestrale"/"annuale"/...

    # template assegnato
    template = seleziona_template(manut.cabina, frequenza)  # implementato da te
    if not template:
        messages.error(
        request,
        "Nessun template assegnato alla cabina. Assegna un template report dalla scheda cabina oppure contatta l’amministratore."
        )
        return redirect('dettaglio_cabina', matricola=manut.cabina.matricola)

    # crea/recupera report
    report, created = ReportCompilato.objects.get_or_create(
        manutenzione=manut,
        defaults={
            "cabina": manut.cabina,
            "template": template,
            "schema_snapshot": template.schema,  # snapshot per versioning
            "compilato_da": request.user,
        }
    )
    # RAMO POST
    if request.method == "POST":
        is_bozza = ("salva" in request.POST) and ("invia" not in request.POST)
        # evita POST "vuote": salviamo solo se viene premuto Salva/Invia
        if "salva" not in request.POST and "invia" not in request.POST:
            return redirect("report_compila", pk=pk)

        # PASSA SEMPRE initial=report.dati per mostrare anteprime anche in caso di errori
        form = build_report_form(
            report.schema_snapshot,
            data=request.POST,
            files=request.FILES,
            initial=report.dati,
            relax_file_required=is_bozza
        )
        if not form.is_valid():
            return render(request, "report/compila.html", {
                "report": report, "form": form, "schema": report.schema_snapshot
            })

        # 1) salva i campi non-file
        cleaned = form.cleaned_data.copy()
        non_file_values = {}
        for k, v in cleaned.items():
            # file/multipli li gestiamo separatamente
            if hasattr(v, "read") or isinstance(v, (list, tuple)):
                continue
            non_file_values[k] = v

        report.dati = {**(report.dati or {}), **non_file_values}
        report.compilato_da = request.user
        report.stato = "inviato" if "invia" in request.POST else "bozza"
        report.save()  # garantisce PK per upload_to

        # 2) salva immagini (sempre lista di URL in report.dati[fname])
        for section in report.schema_snapshot.get("sections", []):
            for item in section.get("items", []):
                if item.get("type") != "image":
                    continue

                fname = item["name"]
                if item.get("multiple"):
                    files = request.FILES.getlist(fname)
                    if files:
                        report.attachments.filter(field_name=fname).delete()
                        names = []
                        for f in files:
                            att = ReportAttachment.objects.create(
                                report=report, field_name=fname, file=f, uploaded_by=request.user
                            )
                            names.append(att.file.name)  # <— salva NAME, non URL
                        report.dati[fname] = names
                        report.save()
                else:
                    f = request.FILES.get(fname)
                    if f:
                        report.attachments.filter(field_name=fname).delete()
                        att = ReportAttachment.objects.create(
                            report=report, field_name=fname, file=f, uploaded_by=request.user
                        )
                        report.dati[fname] = [att.file.name]  # lista con 1 name
                        report.save()


        messages.success(request, "Report inviato." if report.stato == "inviato" else "Report salvato come bozza.")
        return redirect('dettaglio_cabina', matricola=manut.cabina.matricola)

    # --- GET ---
    form = build_report_form(report.schema_snapshot, initial=report.dati)
    return render(request, "report/compila.html", {"report": report, "form": form, "schema": report.schema_snapshot})

@login_required
def report_download(request, pk):
    from .models import ManutenzioneProgrammata, ReportCompilato
    manut = get_object_or_404(ManutenzioneProgrammata, pk=pk)

    try:
        report = manut.report
    except ReportCompilato.DoesNotExist:
        messages.error(request, "Nessun report compilato per questa manutenzione.")
        return redirect('dettaglio_cabina', matricola=manut.cabina.matricola)

    if report.stato != "inviato":
        messages.error(request, "Il report non è ancora inviato, non è possibile scaricarlo.")
        return redirect('report_compila', pk=pk)

    # Mappa attachments: field -> [URL]
    attachments_map = {}
    for att in report.attachments.all():
        attachments_map.setdefault(att.field_name, []).append(att.file.url)

    # fallback: se in dati hai nomi file, prova a risolverli in URL
    dati = report.dati or {}
    for fname, names in list(dati.items()):
        if isinstance(names, list) and fname not in attachments_map:
            urls = []
            for name in names:
                try:
                    urls.append(default_storage.url(name))
                except Exception:
                    pass
            if urls:
                attachments_map[fname] = urls

    context = {
        "report": report,
        "cabina": report.cabina,
        "manutenzione": manut,
        "schema": report.schema_snapshot,
        "dati": dati,
        "attachments": attachments_map,
        "base_url": request.build_absolute_uri("/"),
    }

    html = render_to_string("report/print.html", context=context, request=request)

    data_rif = manut.data_completamento or manut.data_programmata
    filename = f"Report_{report.cabina.matricola}_{data_rif:%Y%m%d}.pdf"

    try:
        from weasyprint import HTML, CSS
    except Exception:
        messages.error(
            request,
            "WeasyPrint non è installato/configurato. Esegui: pip install weasyprint"
        )
        return redirect('report_compila', pk=pk)

    pdf = HTML(string=html, base_url=context["base_url"]).write_pdf(
    )
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


@login_required
def calendario_manutenzioni(request):
    manutenzioni = ManutenzioneProgrammata.objects.filter(stato='programmata')
    events = []

    for m in manutenzioni:
        events.append({
            
            "title": f"{m.cabina.cliente.nome_azienda} - {m.cabina.nome}",
            "start": m.data_programmata.strftime("%Y-%m-%d"),
            "url": reverse('dettaglio_cabina', kwargs={'matricola': m.cabina.matricola}) + '#tab-manutenzioni',
            "extendedProps": {"tipo": m.tipo}
        })

    return JsonResponse(events, safe=False)



def logout_view(request):
    logout(request)
    return redirect('login')