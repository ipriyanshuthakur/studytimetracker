from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def format_timedelta(td):
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{int(hours)}h {int(minutes)}m"
    else:
        return f"{int(minutes)}m"

