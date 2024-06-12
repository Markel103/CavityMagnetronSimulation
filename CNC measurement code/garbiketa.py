# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 16:28:45 2024

@author: Markel
"""

import math

filename = 'datuak_MAGNETS_CASING_center_plane.xml'

with open(filename, "r") as file_in, open(filename[:-4] + '_garbi.txt', 'w') as file_out:
    for lerro in file_in:
        if '<position unit=' in lerro:
            koord = [int(el) for el in lerro[34:lerro.find('/')-1].split(';')]
            for ko in koord:
                file_out.write(str(ko) + ' ')
        elif '<flux>' in lerro:
            data = [float(lerro.strip().split(';')[i]) for i in [1,3,4,5]]
            data[1] = -data[1]
            data[3] = -data[3]
            for da in data:
                file_out.write(str(da) + ' ')
            for da in data[1:]:
                file_out.write(str(da/data[0]) + ' ')
            file_out.write('\n')
            