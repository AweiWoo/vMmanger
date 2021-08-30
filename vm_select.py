#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

from pyVmomi import vim
from lib import pchelper
from lib.login import si

content = si.RetrieveContent()
datacenter_name = "cenboomh"
datacenter = pchelper.get_obj(content,[vim.Datacenter],datacenter_name)
resoucepool = pchelper.get_all_obj(content,[vim.ResourcePool])
datastore = pchelper.get_all_obj(content,[vim.Datastore])
clusterinfo = pchelper.get_all_obj(content,[vim.ClusterComputeResource])
pod = pchelper.get_all_obj(content,[vim.StoragePod])
relospec = vim.vm.RelocateSpec()
clonespec = vim.vm.CloneSpec()
maps = vim.vm.customization.AdapterMapping()
maps.adapter = vim.vm.customization.IPSettings()

print(dir(vim.vm.customization))
#container = pchelper.get_container_view(si,[vim.Datastore])

#print(vim.VirtualMachineNetworkInfo)



#print(container.view)

# print(help(vim.vm.customization))
# print(maps)
# print(maps.adapter)

# print("--------数据中心属性-----------")
# print(dir(datacenter))

# print('\n------------资源池-----------')
# print(dir(resoucepool))
# print(type(resoucepool))
# print(list(resoucepool))
# for key in resoucepool:
#     print(key,resoucepool[key])

# print("\n-----------------数据存储----------------")
# for key in datastore:
#     print(datastore[key])

# print("\n-------------集群信息---------------------") 
# for key in clusterinfo:
#     print(clusterinfo[key])

# print("\n--------------克隆配置---------------------")
# print(relospec)
# print(type(clonespec))
# print(clonespec)

   