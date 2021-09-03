#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from pyVmomi import vim 
from lib.login import si 
from lib import pchelper

def update_vm_customspec(vm_ip=None,vm_subnet=None,vm_gateway=None,vm_dns=None,vm_dnsDomain=None,vm_hostname=None):
    #网络配置修改
    adapter_list = []
    netinfo = vim.vm.customization.AdapterMapping()
    netinfo.adapter = vim.vm.customization.IPSettings()
    #FixedIP表示设置为一个固定的静态ip
    netinfo.adapter.ip = vim.vm.customization.FixedIp()
    netinfo.adapter.ip.ipAddress = vm_ip
    netinfo.adapter.subnetMask = vm_subnet
    netinfo.adapter.gateway = vm_gateway
    if vm_dnsDomain:
        netinfo.adapter.dnsDomain = vm_dnsDomain
    adapter_list.append(netinfo)

    #设置DNS，GlobalIPSettings这里要理解为dns的全球ip(比如：202.103.24.68)
    gloablip = vim.vm.customization.GlobalIPSettings()
    if vm_dns:
        gloablip.dnsServerList=[vm_dns]

    #设置主机名
    ident = vim.vm.customization.LinuxPrep()
    #设置主机ip对于的域名（/etc/hosts文件）
    if vm_dnsDomain:
        ident.domain = vm_dnsDomain
    #FixedName表示设置为一个固定的主机名
    ident.hostName = vim.vm.customization.FixedName()
    if vm_hostname:
        ident.hostName.name = vm_hostname

    #自定义配置
    customspec =  vim.vm.customization.Specification()
    customspec.nicSettingMap =  adapter_list
    customspec.globalIPSettings = gloablip
    customspec.identity = ident
    return customspec

if __name__ == "__main__":
    content = si.RetrieveContent()
    vm_name = "wwu-clone"
    host = pchelper.get_obj(content,[vim.VirtualMachine],vm_name)
    spec = update_vm_customspec(vm_ip="192.168.10.250",vm_subnet="255.255.255.0",
                                vm_gateway="192.168.10.254",
                                vm_dns="202.103.24.68",
                                vm_hostname="wwu-clone")
    task = host.Customize(spec)
    print(task.info)
    