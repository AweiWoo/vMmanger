#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from re import T
from pyVmomi import vim
from lib import pchelper
from lib.login import si
from collections import namedtuple
from custom_spec import update_vm_customspec
from config_spec import config_vm_cpu_mem,config_vm_add_disk,add_description
from lib.opexcel import MyExcel
import asyncio

async def wait_for_task(task):
    task_done = False
    while not task_done:
        if task.info.state == 'success':
            print(task.info.result)
        if task.info.state == 'error':
            print("there was an error")
            print(task.info.error)
            task_done = True
        await asyncio.sleep(0)


async def clone_vm(content,**args):
    """
        功能：克隆虚拟机，并且能在克隆的过程中设置虚拟机的网络信息，资源信息，等。
        参数：
            args: 虚拟机克隆相关参数
    """
    VM_ARGS = namedtuple('args',['template','vm_name','datacenter_name','vm_folder','datastore_name',
                            'cluster_name','resource_pool','power_on',
                            'vm_ip','vm_subnet','vm_gateway','vm_dns','vm_dnsDomain','vm_hostname',
                            'vm_cpu_nums','vm_cpu_core_slot','vm_memGB','add_vmdiskGB','vm_note'])                       
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
        vmconf = config_vm_cpu_mem(cpu_nums=int(vmargs.vm_cpu_nums),cpu_cores=int(vmargs.vm_cpu_core_slot),memGB=int(vmargs.vm_memGB))
        clonespec.config = vmconf
    
    #修改网络配置和主机名
    if all([vmargs.vm_ip,vmargs.vm_subnet,vmargs.vm_gateway]):
        clonespec.customization = update_vm_customspec(vmargs.vm_ip,vmargs.vm_subnet,
                                                vmargs.vm_gateway,vmargs.vm_dns,
                                                vmargs.vm_dnsDomain,vmargs.vm_hostname)
    #开始克隆任务
    print("beging cloinging",vmargs.vm_name)
    task = template.Clone(folder=destfolder,name=vmargs.vm_name,spec=clonespec)
    await wait_for_task(task)
    print(vmargs.vm_name,"Vm cloned")
    
    #克隆后操作
    host = pchelper.get_obj(content,[vim.VirtualMachine],vmargs.vm_name)
    #添加磁盘
    if vmargs.add_vmdiskGB:
        print('need add disk')
        config_vm_add_disk(host,int(vmargs.add_vmdiskGB))
    #添加虚拟机备注
    if vmargs.vm_note:
        print('need add vm description')
        add_description(host,vmargs.vm_note)

async def main(number):
    content = si.RetrieveContent()
    myxls = MyExcel('./data/vm_info.xls')
    clone_vm_list = myxls.get_execl_data('test')
    while True:
        print(asyncio.all_tasks())
        num = abs(len(asyncio.all_tasks()) - number - 1)
        task_list=[]
        for _ in range(num):
            try:
                clone_info=clone_vm_list.popleft()
                task_list.append(asyncio.create_task(clone_vm(**clone_info)))
            except IndexError as e:
                pass
        done = await asyncio.wait(task_list)
        if len(clone_vm_list) == 0:
            print('clone done')
            break

if __name__ == '__main__':
    #实现目标：同时保持N个线程或协程在运行克隆，一个线程结束，启动一个新线程，永远保持N个虚拟机在克隆，直到所有虚拟机都克隆完成。
    asyncio.run(main(2))