from django import template
import socket, struct
register = template.Library()


@register.simple_tag
def num2ip(arg, int_ip):
    """
    IP address and number conversion
    """
    if arg == 'ip':
        ip = socket.inet_ntoa(struct.pack('I', socket.htonl(int_ip)))
    else:
        ip = str(socket.ntohl(struct.unpack('I', socket.inet_aton(int_ip))[0]))
    return ip


@register.filter
def udf_split(ret):
    return ret.split('---')


@register.filter
def udf_split_2(ret):
    return ret.split(',')


@register.filter
def udf_split_3(ret):
    return ret.split('\r\n')


@register.filter
def udf_split_4(ret, args):
    return ret.split(args)

@register.filter
def udf_strip(ret, arg):
    return ret.strip(arg)
