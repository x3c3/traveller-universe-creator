# -*- coding: utf-8 -*-
"""
Created on Tue May 21 14:36:01 2024

@author: sean
"""

import pandas as pd

df = pd.read_fwf('sector_db/solomani_rim.txt')
df.drop(index=0, inplace=True)  
df['Hex'] = df['Hex'].astype(str)
df.to_csv('sector_db/solomani_rim.csv', index=False)