#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from pyVmomi import vim 
from lib.login import si 
from lib import pchelper

def get_vm_networkspec(content,vm_name):
    vm_host_info = pchelper.get_obj(content,[vim.VirtualMachine],vm_name)
    print(vm_host_info.network[0].summary)

# def update_vm_networkspec(vm_ip=None,vm_subnet=None,vm_gateway=None,vm_dns=None,vm_dnsDomain=None,vm_hostname=None):
#     pass

if __name__ == "__main__":
    content = si.RetrieveContent()
    vm_name = "wwu-clone1"
    get_vm_networkspec(content,vm_name)