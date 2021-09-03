#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from pyVmomi import vim
from lib import pchelper
from lib.login import si
from collections import namedtuple
from custom_spec import update_vm_customspec

def wait_for_task(task):
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result
        if task.info.state == 'error':
            print("there was an error")
            print(task.info.error)
            task_done = True

def update_resource_conf():
    #调整cpu和内存大小
    pass

def update_nic():
    #修改网卡
    pass

def add_nic():
    #添加网卡
    pass

def add_disk():
    #添加磁盘
    pass

def clone_vm(content,**args):

    VM_ARGS = namedtuple('args',['template','vm_name','datacenter_name','vm_folder','datastore_name',
                            'cluster_name','resource_pool','power_on',
                            'vm_ip','vm_subnet','vm_gateway','vm_dns','vm_dnsDomain','vm_hostname'])
                            
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

    #虚拟机所使用的资源池。每个集群组有自己的资源池（内存，cpu），如果单独不指定，则使用集群自己默认的资源池
    if vmargs.resource_pool:
        resource_pool = pchelper.search_for_obj(content,[vim.ResourcePool],vmargs.resource_pool)
    else:
        resource_pool = cluster.resourcePool

    #资源配置
    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    relospec.pool = resource_pool

    #克隆配置
    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = vmargs.power_on

    #修改网络配置和主机名
    if all([vmargs.vm_ip,vmargs.vm_subnet,vmargs.vm_gateway]):
        clonespec.customization = update_vm_customspec(vmargs.vm_ip,vmargs.vm_subnet,
                                                vmargs.vm_gateway,vmargs.vm_dns,
                                                vmargs.vm_dnsDomain,vmargs.vm_hostname)

    print("cloinging VM...")
    task = template.Clone(folder=destfolder,name=vmargs.vm_name,spec=clonespec)
    wait_for_task(task)
    print("Vm cloned")

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
        "vm_dns":"",
        "vm_dnsDomain":"",
        "vm_hostname":"wwu-clone"
    }
    clone_vm(content,**clone_info)

if __name__ == '__main__':
    main()