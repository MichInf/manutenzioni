from django import template

register = template.Library()

@register.filter
def get_unique_cabine(alert_list):
    """Restituisce il numero di cabine uniche negli alert"""
    cabine_set = set()
    for alert in alert_list:
        cabine_set.add(alert['cabina'].matricola)
    return list(cabine_set)

@register.filter
def get_item(d, key):
    try:
        return d.get(key)
    except Exception:
        return None
