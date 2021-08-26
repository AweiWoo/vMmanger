#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from pyVmomi import vim
from lib import pchelper
from lib.login import si
from collections import namedtuple

def wait_for_task(task):
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result
        if task.info.state == 'error':
            print("there was an error")
            print(task.info.error)
            task_done = True

def update_vm_customspec(vm_ip=None,vm_subnet=None,vm_gateway=None,vm_dns=None,vm_dnsDomain=None,vm_hostname=None):
    #网络配置修改
    adapter_list = []
    netinfo = vim.vm.customization.AdapterMapping()
    netinfo.adapter = vim.vm.customization.IPSettings()
    netinfo.adapter.ip = vim.vm.customization.FixedIp()
    netinfo.adapter.ip.ipAddress = vm_ip
    netinfo.adapter.subnetMask = vm_subnet
    netinfo.adapter.gateway = vm_gateway
    if vm_dnsDomain:
        netinfo.adapter.dnsDomain = vm_dnsDomain
    adapter_list.append(netinfo)

    #设置DNS
    gloablip = vim.vm.customization.GlobalIPSettings()
    if vm_dns:
        gloablip.dnsServerList=[vm_dns]

    #设置主机名
    ident = vim.vm.customization.LinuxPrep()
    if vm_dnsDomain:
        ident.domain = vm_dnsDomain
    ident.hostName = vim.vm.customization.FixedName()
    if vm_hostname:
        ident.hostName.name = vm_hostname

    customspec =  vim.vm.customization.Specification()
    customspec.nicSettingMap =  adapter_list
    customspec.globalIPSettings = gloablip
    customspec.identity = ident

    return customspec

def clone_vm(content,**args):
    vmargs = VM_ARGS(**args)
    #模板
    if vmargs.template:
        template = pchelper.get_obj(content,[vim.VirtualMachine],vmargs.template)
    else:
        print("template not found")

    #获取数据中心
    datacenter = pchelper.get_obj(content,[vim.Datacenter],vmargs.datacenter_name)

    #虚拟机目录
    if vmargs.vm_folder:
        destfolder = pchelper.search_for_obj(content,[vim.Folder],vmargs.vm_folder)
    else:
        destfolder = datacenter.vmFolder
    
    #虚拟机使用存储
    if vmargs.datastore_name:
        datastore = pchelper.search_for_obj(content,[vim.Datastore],vmargs.datastore_name)
    else:
        datastore = pchelper.get_obj(content,[vim.Datastore],vmargs.datastore[0].info.name)

    #集群组
    cluster = pchelper.search_for_obj(content,[vim.ClusterComputeResource],vmargs.cluster_name)
    if not cluster:
        clusters = pchelper.get_all_obj(content,[vim.ResourcePool])
        cluster = list(clusters)[0]

    if vmargs.resource_pool:
        resource_pool = pchelper.search_for_obj(content,[vim.ResourcePool],vmargs.resource_pool)
    else:
        resource_pool = cluster.resourcePool

    #vmconf = vim.vm.ConfigSpec()

    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    relospec.pool = resource_pool

    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = vmargs.power_on

    #修改网络配置和主机名
    if all([vmargs.vm_ip,vmargs.vm_subnet,vmargs.vm_gateway]):
        clonespec.customization = update_vm_customspec(vmargs.vm_ip,vmargs.vm_subnet,vmargs.vm_gateway,vmargs.vm_dns,vmargs.vm_dnsDomain,vmargs.vm_hostname)

    print("cloinging VM...")
    task = template.Clone(folder=destfolder,name=vmargs.vm_name,spec=clonespec)
    wait_for_task(task)
    print("Vm cloned")

VM_ARGS = namedtuple('args',['template','vm_name','datacenter_name','vm_folder','datastore_name',
                            'cluster_name','resource_pool','power_on',
                            'vm_ip','vm_subnet','vm_gateway','vm_dns','vm_dnsDomain','vm_hostname'])

def main():
    content = si.RetrieveContent()
    clone_info = {
        "template":"k8s-nginx1",
        "vm_name":"wwu-clone",
        "datacenter_name":"cenboomh",
        "vm_folder":"test",
        "datastore_name":"devops_pool",
        "cluster_name":"devops",
        "resource_pool":"",
        "power_on":True,
        "vm_ip":"192.168.10.250",
        "vm_subnet":"255.255.255.0",
        "vm_gateway":"192.168.10.254",
        "vm_dns":"202.103.24.68",
        "vm_dnsDomain":"",
        "vm_hostname":"wwu-clone"
    }
    clone_vm(content,**clone_info)

if __name__ == '__main__':
    main()