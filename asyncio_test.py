#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

import asyncio
import time

async def main():
    num = len(asyncio.all_tasks())
    print(asyncio.all_tasks())
    print(num-1)

asyncio.run(main())

