#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from pyVmomi import vim
from lib import pchelper
from lib.login import si
from collections import namedtuple
from custom_spec import update_vm_customspec
from config_spec import config_vm_cpu_mem,config_vm_add_disk

def wait_for_task(task):
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            return task.info.result
        if task.info.state == 'error':
            print("there was an error")
            print(task.info.error)
            task_done = True
            
def add_description():
    pass

def clone_vm(content,**args):
    """
        功能：克隆虚拟机，并且能在克隆的过程中设置虚拟机的网络信息，资源信息，等。
        参数：
            args: 虚拟机克隆相关参数
    """
    VM_ARGS = namedtuple('args',['template','vm_name','datacenter_name','vm_folder','datastore_name',
                            'cluster_name','resource_pool','power_on',
                            'vm_ip','vm_subnet','vm_gateway','vm_dns','vm_dnsDomain','vm_hostname',
                            'vm_cpu_nums','vm_cpu_core_slot','vm_memGB','add_vmdiskGB'])                       
    vmargs = VM_ARGS(**args)
    #模板
    if vmargs.template:
        template = pchelper.get_obj(content,[vim.VirtualMachine],vmargs.template)
    else:
        print("无法找到克隆模板或虚拟机")
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
    #调整虚拟机cpu、内存
    if any([vmargs.vm_cpu_nums,vmargs.vm_cpu_core_slot,vmargs.vm_memGB]):
        #此处缺少一个判断vm_cpu_nums必须是vm_cpu_core_slot的倍数
        vmconf = config_vm_cpu_mem(cpu_nums=vmargs.vm_cpu_nums,cpu_cores=vmargs.vm_cpu_core_slot,memGB=vmargs.vm_memGB)
        clonespec.config = vmconf
    
    #修改网络配置和主机名
    if all([vmargs.vm_ip,vmargs.vm_subnet,vmargs.vm_gateway]):
        clonespec.customization = update_vm_customspec(vmargs.vm_ip,vmargs.vm_subnet,
                                                vmargs.vm_gateway,vmargs.vm_dns,
                                                vmargs.vm_dnsDomain,vmargs.vm_hostname)
    #开始克隆任务
    print("cloinging VM...")
    task = template.Clone(folder=destfolder,name=vmargs.vm_name,spec=clonespec)
    wait_for_task(task)
    print("Vm cloned")
    
    #添加磁盘
    if vmargs.add_vmdiskGB:
        print('need add disk')
        host = pchelper.get_obj(content,[vim.VirtualMachine],vmargs.vm_name)
        config_vm_add_disk(host,vmargs.add_vmdiskGB)


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
        "vm_hostname":"wwu-clone",
        "vm_cpu_nums":8,
        "vm_cpu_core_slot":4,
        "vm_memGB":8,
        "add_vmdiskGB": 50
    }
    clone_vm(content,**clone_info)

if __name__ == '__main__':
    main()