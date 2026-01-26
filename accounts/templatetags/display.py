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
