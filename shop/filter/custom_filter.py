from django import template

register = template.Library()
@register.filter
def linebreaksbr(value):
    return value.replace('\n', '<br>')