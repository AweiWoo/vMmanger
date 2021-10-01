#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

import asyncio
import time
from lib.opexcel import MyExcel
import asyncio

async def clone_vm(**clone_info):
    print(clone_info)
    print('-------------------------------------------')
    time.sleep(5)
    #await asyncio.sleep(0)
    

async def main(number):
    myxls = MyExcel('./data/vm_info.xls')
    clone_vm_list = myxls.get_execl_data('test')
    while True:
        print(asyncio.all_tasks())
        num = abs(len(asyncio.all_tasks()) - number - 1)
        task_list=[]
        for _ in range(num):
            try:
                clone_info1=clone_vm_list.popleft()
                task_list.append(asyncio.create_task(clone_vm(**clone_info1)))
            except IndexError as e:
                pass
        done = await asyncio.wait(task_list)
        if len(clone_vm_list) == 0:
            print('clone done')
            break

asyncio.run(main(3))



