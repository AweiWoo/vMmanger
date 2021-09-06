#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from pyVmomi import vim 
from lib.login import si 
from lib import pchelper

def config_vm_cpu_mem(cpu_nums=None,cpu_cores=None,memGB=None):
    """
        功能：调整虚拟机的cpu和内存资源
        参数说明：
            cpu_nums: cpu总的核心数
            cpu_cores: 单个插槽cpu核心数，即cpu_nums/cpu_cores=虚拟插槽数
    """
    vimconf = vim.vm.ConfigSpec()
    if cpu_nums:
        vimconf.numCPUs = cpu_nums
    if cpu_cores:
        vimconf.numCoresPerSocket = cpu_cores        
    if memGB:
        vimconf.memoryMB = memGB * 1024
    return vimconf

if __name__ == "__main__":
    vm_name = "wwu-clone"
    cpu_nums = 8
    cpu_cores = 4
    memGB = 8
    content = si.RetrieveContent()
    vm_conf = config_vm_cpu_mem(cpu_nums=cpu_nums,cpu_core=cpu_cores,memGB=memGB)
    host = pchelper.get_obj(content,[vim.VirtualMachine],vm_name)
    task=host.Reconfigure(vm_conf)
    print(task.info)



