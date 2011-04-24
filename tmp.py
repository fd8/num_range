import csv
import codecs

f = codecs.open('./data/DEF-3x.csv', encoding='cp1251')
for line in csv.reader(f):
    print line
