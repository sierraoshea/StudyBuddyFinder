from django import template

register = template.Library()

@register.filter(name='all_but_user')
def all_but_user(value, arg):
    return value.exclude(id = arg.id)