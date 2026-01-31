from django import template
import math

register = template.Library()

@register.filter(name='safeval')
def safeval(value):
    """
    Template filter: display '-' instead of NaN/None/empty.
    Keeps other values as-is for readability.
    """
    try:
        if value is None:
            return '-'
        # Handle floats NaN
        if isinstance(value, float) and math.isnan(value):
            return '-'
        # Handle pandas NA string representation and empty strings
        sval = str(value).strip()
        if sval.lower() in ('nan', 'none', '') or sval.lower() == '<na>':
            return '-'
        return value
    except Exception:
        return '-'

@register.filter(name='safeint')
def safeint(value):
    """
    Template filter: render stock values as integers.
    Returns '-' for NaN/None/empty/non-numeric values.
    """
    try:
        if value is None:
            return '-'
        if isinstance(value, float) and math.isnan(value):
            return '-'
        sval = str(value).strip()
        if sval.lower() in ('nan', 'none', '') or sval.lower() == '<na>':
            return '-'
        num = float(sval)
        return int(round(num))
    except Exception:
        return '-'
