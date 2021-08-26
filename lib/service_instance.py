#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from pyVim.connect import SmartConnect, Disconnect
import atexit

def connect(host,username,password,port,ssl=True):
    service_instance = None
    try:
        service_instance = SmartConnect(host=host,user=username,pwd=password,port=port,disableSslCertValidation=ssl)
        atexit.register(Disconnect, service_instance)
    except IOError as e:
        print(e)

    if not service_instance:
        raise SystemExit("Unable to collect to host.")

    return service_instance