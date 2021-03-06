#-*- coding: UTF-8 -*-
'''
Объединение диапазонов нумерации. Если изначально диапазоны записываются
последовательно, то есть, например, с 9024100000 по 90242999999 и с 9024300000 по 9024499999,
то на выходе получим 9024100000;9024499999

Входные данные: csv-файл с двумя колонками - начало и конец диапазона. Диапазоны должны быть отсортированы
по возрастанию. Например:
9024100000;9024599999
9025000000;9025999999

На выходе: такой же csv-файл, но с укрупненными диапазонами и с размером диапазона.
'''
'''
Алгоритм:
1. Открываем каждый файл из директории файлов.
2. Началу и концу первого диапазона присваиваем значения первой строки из этого файла.
3. Для каждой строки из файла
    3.1. 

'''

'''
Ошибки:
- неправильно формируется список коротких диапазонов, поскольку при печати видно, что в один список
  добавляется много диапазонов
'''


import sqlite3

#-------------- FUNCTIONS ---------------------
def get_addition_symbols(item):
    symbol = item[len(item)-1]
    s = ''
    for i in range(10-len(item)):
        s += symbol
    return s

def add_symbols(var):
    #print var
    str_var = str(var)
    addition_symbols = get_addition_symbols(str_var)
    var = long(str_var+addition_symbols)
    return var

def correct_range_vals(range_row):
    i = 0
    for item in range_row:
        if isinstance(item, long) and len(str(item)) < 10:
            range_row[i] = add_symbols(item)
        i += 1
    return range_row

def add_fist_range(row):
    list = []
    row = correct_range_vals(row)
    for item in row:
        list.append(item)
    return list

def add_range(ranges_list, range_2check):
    range_2check = correct_range_vals(range_2check)
    range_start = ranges_list[len(ranges_list)-1][0]
    range_end = ranges_list[len(ranges_list)-1][1]
    if range_end + 1 == range_2check[0]:
        ranges_list[len(ranges_list)-1][1] = range_2check[1]
    elif range_end + 1 > range_2check[0]:
        if range_end < range_2check[1]: # правая граница предыдущего диап. меньше правой границы следующего
            ranges_list[len(ranges_list)-1][1] = range_2check[1] #то меняем правую границу на правую
            # границу нового диапазона.
            # иначе - ranges_list остается неизменным и с range_2check не делаем ничего.
    else:
        ranges_list.append(range_2check)
    return ranges_list
    
def str2num_list(str, str_delimiter, filename, i):
    str_list = str.split(str_delimiter)
    num_list = []
    for item in str_list:
        try:
            x = long(item)
        except ValueError:
            x = item
        num_list.append(x)
    return num_list
    
def str_list2int_list(str_list):
    int_list = []
    for str_item in str_list:
        if isinstance(str_item, str) or isinstance(str_item, unicode):
            str_item = int(str_item)
        elif not isinstance(str_item, int):
            e = "The value list have to contain from strs or ints only! " + \
                str(type(str_item)) + " involves."
            raise ValueError, e
        int_list.append(str_item)
    return int_list
    
def get_ranges(ranges, file):   
    #num_range_part = []
    with open(file) as f:   
        file_start_flag = 1
        i = 0
        for line in csv.reader(f):
            row = str2num_list(line[0], ';', file, i)
            if file_start_flag == 1:
                ranges.append(add_fist_range(row))
                file_start_flag = 0
            else:
                ranges = add_range(ranges, row)
            i += 1
    
    return ranges

def put_ranges_intoDB(ranges):
    conn = sqlite3.connect(":memory:")#./ranges.sqlite")
    cur = conn.cursor()
    sql = '''
          create table ranges
          (range_start number, 
           range_end number, 
           region varchar2(100))
          '''
    cur.execute(sql)
    for range in ranges:
        s = unicode(range[2], 'cp1251')
        #a = s.encode('cp1251')
        #print s, a
        sql = '''
              insert into ranges values
              ({r_start}, {r_end},
              '''.format(r_start=range[0], r_end=range[1])#unicode(range[2], 'cp1251'))
        sql += '"' + s + '")'
        cur.execute(sql)
    return conn, cur 

def is10in_list(chr_list):
    '''
    на входе список из цифр,
    чтобы проверить, все ли цифры от 0 до 10 
    у нем представлены.
    '''
    num_list = str_list2int_list(chr_list)
    for i in range(10):
        if i not in num_list:
            return False
    return True

def append_ranges(ranges, range_base, range_rests, region = ''):
    for item in range_rests:
        range = []
        range.append(add_symbols(range_base+item+'0'))
        range.append(add_symbols(range_base+item+'9'))
        range.append(region)
        ranges.append(range)
    return ranges

    
def get_unique_sort(list):
    '''
    На входе - список значений, из которых 
    получаем сортированый список.
    '''
    l_set = set()
    for item in list:
        l_set.add(item)
    list = sorted(l_set)
    return list
    
def tup2list(tup_list):
    '''
    на входе список из одинарных тьюплов 
    (как результат работы fetchall),
    чтобы на выходе получить список из значений,
    записанных в tuple
    '''
    list = []
    for tup in tup_list:
        list.append(tup[0])
    return list
    
def get_short_ranges(full_ranges):
    conn, cur = put_ranges_intoDB(num_ranges)
    sql = '''
          select distinct substr(range_start, 1, 4)
          from ranges
          ''' 
    cur.execute(sql)
    short_ranges = []
    i = 0
    lines = get_unique_sort(tup2list(cur.fetchall())) # lines - это список, содержащий диапазоны из 4 символов.
    for range4 in lines:
        sql = '''
              select substr(range_start, 5, 1) 
              from ranges
              where substr(range_start, 1, 4) like "{r_4}"
              '''.format(r_4=range4)
        cur2 = conn.cursor()
        cur2.execute(sql)
        print sql
        ranges4 = get_unique_sort(tup2list(cur2.fetchall()))
        print ranges4
        if is10in_list(ranges4) is True:
            short_range = []
            short_range.append(add_symbols(range4+'0'))
            short_range.append(add_symbols(range4+'9'))
            #short_ranges[n].append(get_region(region))
            short_range.append('')
            short_ranges.append(short_range)
        else: 
            range_rests = ranges4 # получаем список пятых цифр
            #region = line[len(line)-1]
            short_ranges = append_ranges(short_ranges, range4, range_rests)#, region)
    conn.close()
    return short_ranges

def to_cp1251(list):
    res_list = []
    for i in range(len(list)):
        if isinstance(list[i], unicode):
            list[i] = list[i].encode('cp1251')
        res_list.append(list[i])
    return res_list
    

def write_out_ranges(writer, ranges, DBflag = 0):
    header = ['Код диапазона', 'Начало диапазона', 'Конец диапазона', 'Емкость', 'Регион']
    writer.writerow(header)
    for list in ranges:
        list.insert(0, long(str(list[0])[0:3])) # код диапазона
        list.insert(3, list[2]-list[1]+1) # емкость
        if DBflag == 1: 
            list = to_cp1251(list)
        try:
            writer.writerow(list)
        except UnicodeEncodeError:
            print "Can't encode chars for ", DBflag, list
            exit()

    
#----------- FUNCTIONS END --------------------

import csv
from os import walk
from os.path import join

nums_dir = './data'
num_ranges = []

csv.register_dialect('num_dialect', delimiter = ';', lineterminator = '\n')
dialect = csv.get_dialect('num_dialect')
for root, dirs, files in walk(nums_dir):
    for file in files:
        num_ranges = get_ranges(num_ranges, join(root, file))
    
short_ranges = get_short_ranges(num_ranges)    
w = csv.writer(open('ranges_out.csv', 'w'), delimiter=';', lineterminator='\n')
write_out_ranges(w, num_ranges)

w = csv.writer(open('ranges_out_short.csv', 'w'), delimiter=';', lineterminator='\n')
write_out_ranges(w, short_ranges, 1)