#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from collections import namedtuple
from lib.service_instance import connect

VMLogin = namedtuple('info',['host','user','pwd','port'])

def vm_info():
    info={
        "host":"192.168.10.111",
        "user":"xxxxxx",
        "pwd":"xxxx",
        "port":"443"
    }
    vm_i = VMLogin(**info)
    return vm_i

v = vm_info()
si = connect(v.host,v.user,v.pwd,v.port)


