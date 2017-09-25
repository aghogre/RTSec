# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 17:01:27 2017

@author: ADMIN
"""

import os

DEFAULT_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'TwitterHandle'))

with open('stream.json','r') as f:
    flines = f.readlines()
    l1 = [l.strip().split('\"')  for l in flines if "created_at" in l]

#print l1

from functools import reduce

dateslist = []
for ld in l1:
    lstr = ld[3].split()
    ls = lstr[-1]+"-"+lstr[1]+"-"+lstr[2]
    dateslist.append(ls)

#print dateslist


reducelist = []
for num in dateslist:
    count =0
    for num2 in dateslist:
        if num == num2:
            count +=1
    reducelist.append((num,count))

print sorted(set(reducelist))

