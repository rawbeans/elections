from django import template

register = template.Library()

@register.filter
def percentage(decimal):
    return '%.2f%%' % (decimal * 100)