from django import template

register = template.Library()

@register.filter(name='all_but_user')
def all_but_user(value, arg):
    return value.exclude(id = arg.id)

@register.filter(name='index')
def index(value, arg):
    return value.index(arg)