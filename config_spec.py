#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from pyVmomi import vim 
from lib.login import si 
from lib import pchelper

def config_vm_cpu_mem(cpu_nums=None,cpu_cores=None,memGB=None):
    """
        功能：调整虚拟机的cpu和内存资源
        参数：
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

def config_vm_add_nic(nic_name,nic_type):
    """
        功能：给虚拟机添加网卡（网络适配器）
        参数：
            nic_type:网络适配器类型（E1000,E1000e,Vmxnet2,Vmxnet3）
            nic_name:网络适配器名称
    """
    vimconf = vim.vm.ConfigSpec()
    nic_changes = []
    nic_spec = vim.vm.device.VirtualDeviceSpec()
    #添加网卡
    nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    #四种网卡类型
    if nic_type == "E1000" :
        nic_spec.device = vim.vm.device.VirtualE1000()
    elif nic_type == "E1000e":
        nic_spec.device = vim.vm.device.VirtualE1000e()
    elif nic_type == "Vmxnet2":
        nic_spec.device = vim.vm.device.VirtualVmxnet2() 
    elif nic_type == "Vmxnet3":
        nic_spec.device = vim.vm.device.VirtualVmxnet3Vrdma()
    if nic_name:
        network = pchelper.get_obj(content,[vim.Network],nic_name)
        #网络适配器对应的文件信息
        nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
        if network:
            #禁止自动获取网络标签，通过传入的nic_name参数指定
            nic_spec.device.backing.useAutoDetect = False
            nic_spec.device.backing.deviceName = nic_name
    #网络设备的连接信息
    nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    nic_spec.device.connectable.allowGuestControl = True
    nic_spec.device.connectable.connected = False
    nic_spec.device.connectable.startConnected = True
    nic_spec.device.wakeOnLanEnabled = True
    nic_changes.append(nic_spec)
    vimconf.deviceChange=nic_changes
    return vimconf

def config_vm_add_disk(vm,disk_size,disk_type=None):
    """
        功能：给虚拟机添加磁盘
        参数：
            vm: 虚拟机对象
            disk_size: 磁盘大小（GB）
            disk_type: 磁盘类型，默认为：厚置备延迟置零，可选择参数“thin”设置为：Thin Provision类型磁盘
    """
    vmconf = vim.vm.ConfigSpec()
    unit_number = 0
    controller = None
    #查询虚拟机已经存在的磁盘控制器，在次基础上+1，
    for device in vm.config.hardware.device:
        if hasattr(device.backing, 'fileName'):
            unit_number = int(device.unitNumber) + 1
        if isinstance(device, vim.vm.device.VirtualSCSIController):
            controller = device
    if controller is None:
        print('Disk SCSI controller not found !')
    dev_changes=[]
    #添加的磁盘大小
    new_disk_kb = int(disk_size) * 1024 * 1024
    disk_spec = vim.vm.device.VirtualDeviceSpec()
    #磁盘都会生成一个.vmdk的文件，fileOperation操作就是创建一个磁盘文件
    disk_spec.fileOperation = "create"
    #添加磁盘
    disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    disk_spec.device = vim.vm.device.VirtualDisk()
    #Flat类型磁盘，应该是厚置备延迟置零类型（默认类型），使用thin参数，可以调整为Thin Provision类型磁盘
    disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
    if disk_type == 'thin':
        disk_spec.device.backing.thinProvisioned = True
    #磁盘模式为持久性
    disk_spec.device.backing.diskMode = 'persistent'
    disk_spec.device.capacityInKB =  new_disk_kb
    disk_spec.device.unitNumber = unit_number
    disk_spec.device.controllerKey = controller.key
    dev_changes.append(disk_spec)
    vmconf.deviceChange=dev_changes
    vm.Reconfigure(vmconf)
    print("%sGB disk added to %s" % (disk_size,vm.config.name))

def add_description(vm,description):
    """
        功能：给虚拟机添加注释
        参数：
            vm: 虚拟机对象
            description: 备注 
    """
    vmconf = vim.vm.ConfigSpec()
    vmconf.annotation = description
    vm.Reconfigure(vmconf)

if __name__ == "__main__":
    content = si.RetrieveContent()
    vm_name = "wwu-clone"
    host = pchelper.get_obj(content,[vim.VirtualMachine],vm_name)
    #修改cpu和内存
    # cpu_nums = 8
    # cpu_cores = 4
    # memGB = 8
    # vm_conf = config_vm_cpu_mem(cpu_nums=cpu_nums,cpu_core=cpu_cores,memGB=memGB)

    #添加网络
    # vm_conf = config_vm_add_nic(nic_name="20",nic_type="Vmxnet3")

    #添加磁盘
    #config_vm_add_disk(host,50)

    #添加备注
    message = "功能：wwu的克隆测试虚拟机\n操作系统：centos7\nroot密码：thzk2**"
    add_description(host,message)



