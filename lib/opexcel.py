#!/usr/bin/python
# -*- coding:UTF-8 -*-
# author: wwu

import xlrd

class MyExcel:
    def __init__(self,file_path):
        try:
            self.xlsdata = xlrd.open_workbook(file_path)
        except Exception as e:
            print(e)

    def get_sheets_name(self):
        sheets = self.xlsdata.sheet_names()
        return sheets

    def get_execl_data(self,sheet_name):
        sname = self.get_sheets_name()
        if sheet_name in sname:
            table = self.xlsdata.sheet_by_name(sheet_name)
            #获取行数
            rows = table.nrows
            #获取列数
            cols = table.ncols
            rows_first = table.row_values(0)
            vm_list=[]
            for n in range(1,rows):
                row = table.row_values(n)
                vm_dict={}
                for i in range(len(rows_first)):
                    vm_dict[rows_first[i]] = row[i]
                vm_list.append(vm_dict)
            return vm_list

if __name__ == '__main__':
    myxls = MyExcel('./data/vm_info.xls')
    myxls.get_sheets_name()
    result = myxls.get_execl_data('test')
    print(result)
    