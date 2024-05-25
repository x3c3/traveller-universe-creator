# -*- coding: utf-8 -*-
"""
Created on Tue May 21 15:16:11 2024

@author: sean
"""

import pandas as pd
import sqlite3
from traveller_functions import hex_to_int
from traveller_map import build_travellermap_file
from routes_short_path import create_route_xml

new_sector_db = 'sector_db/solomani_rim.db'
sector_name = 'Solomani Rim'


conn_new = sqlite3.connect(new_sector_db)
conn_old = sqlite3.connect('sector_db/example-66.db')

df = pd.read_csv('sector_db/solomani_rim.csv',  dtype=str)

new_df = pd.DataFrame()

new_df['location_orb'] = df['Hex']
new_df['location'] = df['Hex']
new_df['system_name'] = df['Name']

new_df['starport'] = df['UWP'].str[0]

new_df['size'] =df['UWP'].str[1].apply(hex_to_int)
new_df['atmosphere'] = df['UWP'].str[2].apply(hex_to_int)
new_df['hydrographics'] = df['UWP'].str[3].apply(hex_to_int)

new_df['population'] = df['UWP'].str[4].apply(hex_to_int)
new_df['government'] = df['UWP'].str[5].apply(hex_to_int)
new_df['law'] = df['UWP'].str[6].apply(hex_to_int)

new_df['tech_level'] = df['UWP'].str[8].apply(hex_to_int)

new_df['main_world'] = 1

new_df.to_sql('traveller_stats', conn_new, if_exists='replace', index_label = 'id')



system_df = pd.DataFrame()
system_df['id'] = df.index
system_df['location']  = df['Hex']
system_df['remarks'] = df['Remarks']

system_df['ix'] = df['{Ix}']
system_df['ex'] = df['(Ex)']
system_df['cx'] = df['[Cx]']

system_df['n'] = df['N']
system_df['bases'] = df['B']
system_df['zone'] = df['Z']

system_df['pbg'] = df['PBG']
system_df['w'] = df['W']
system_df['allegiance'] = df['A']
system_df['stars'] = df['Stellar']

system_df['remarks'].fillna('None',inplace=True)


system_df.to_sql('system_stats', conn_new, if_exists='replace', index=False)




sql_statement = 'SELECT * FROM '

table_list = ['far_trader', 
              'journey_data', 
              'orbital_bodies', 
              'perceived_culture', 
              'stellar_bodies', 
              'main_world_eval']

for each_table in table_list:
    sql_command = sql_statement + each_table
    df = pd.read_sql(sql_command, conn_old)
    df = pd.DataFrame(columns=df.columns)  
    df['location'] = new_df['location']
    if each_table in ['journey_data', 'orbital_bodies','main_world_eval']:
        df['location_orbit'] = new_df['location']
        if each_table == 'orbital_bodies':
            df['gravity'] = 1
            df['wtype'] = 'N/A'
            df['size_class'] = 'N/A'
            df['atmos_composition'] = 'N/A'
            df['temperature'] = 300
            df['zone'] = 'Middle Zone'
            df['body'] = 'Planet'
            df['climate'] = 'N/A'
            
    elif each_table == 'traveller_stats':
        df['location_orb'] = new_df['location']
        
    elif each_table == 'far_trader':
        df['needs'] == 'NA'
        df['wants'] == 'NA'
    
        
    if each_table == 'perceived_culture':
        df.fillna('N/A', inplace=True)
    else:
        df.fillna(0, inplace=True)
        
        
    df['id'] = df.index  
    df.to_sql(each_table, conn_new, if_exists='replace')
    
    
    
build_travellermap_file(new_sector_db, sector_name)
create_route_xml(0,new_sector_db,0)
    
    


conn_old.commit()
conn_new.commit()
conn_new.close()
conn_old.close()



