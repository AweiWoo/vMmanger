from collections import namedtuple
from lib.service_instance import connect

VMLogin = namedtuple('info',['host','user','pwd','port'])

def vm_info():
    info={
        "host":"192.168.10.200",
        "user":"administrator@cbh.com",
        "pwd":"Cbh@211!",
        "port":"443"
    }
    vm_i = VMLogin(**info)
    return vm_i

v = vm_info()
si = connect(v.host,v.user,v.pwd,v.port)


