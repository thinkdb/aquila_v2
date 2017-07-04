from django import template
import socket, struct
register = template.Library()


@register.simple_tag
def udf_strip(ret, arg):
    return ret.strip(arg)
