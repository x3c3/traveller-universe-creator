# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 16:35:43 2021

@author: sean
"""

import random


# used for images on browser and export
def get_remarks_list():
    remarks_list = [['In', 'industrial'],
                    ['Ag', 'agricultural'],
                    ['Hi', 'hipop'],
                    ['Lo', 'lopop'],
                    ['Ba', 'barren'],
                    ['Na', 'non_agricultural'],
                    ['Ni', 'non_industrial'],
                    ['Px', 'prison']]
    return remarks_list

def integer_root(expo,num):
    num = float(num)
    root_expo = 1/expo
    return float(num ** root_expo)

def tohex(dec):
    if dec > 15: dec = 15
    x = (dec % 16)
    digits = "0123456789ABCDEF"
    return digits[int(x)]

    
def hex_to_int(hex_val):
    response = -1
    try:
        hex_list = ['A','B','C','D','E','F']
        hex_dict = {'F': 15,
                    'E': 14,
                    'D': 13,
                    'C': 12,
                    'B': 11,
                    'A': 10}  
        if hex_val in hex_list: response = int(hex_dict[hex_val])
        else: response = int(response)
        return response
    except:
        print('failed hex to int with',hex_val)
        
def cx_values(cx):
        het_no = hex_to_int(cx[0])
        acc_no = hex_to_int(cx[1])
        sta_no = hex_to_int(cx[2])
        sym_no = hex_to_int(cx[3])
        return (het_no,acc_no,sta_no,sym_no)
    
    
def roll_dice(no_dice, why, location, conn, c):
    
    
    no_dice_loop = no_dice + 1  #increment by one for the FOR loop
    sum_dice = 0
    for dice_loop in range (1,no_dice_loop):
        sum_dice = sum_dice + random.randrange(1,7)
        
    c.execute("INSERT INTO die_rolls (location, number, reason, total) VALUES(?, ?, ?, ?)",
           (str(location), 
            no_dice,
            why,
            sum_dice))
            
    return sum_dice   

def get_description(upp_type,upp_value):
    description = ''
    if upp_type == 'starport':
        dy_upp = {'A': 'Excellent',
                  'B': 'Good',
                  'C': 'Routine',
                  'D': 'Poor',
                  'E': 'Frontier',
                  'F': 'Spaceport - Good',
                  'G': 'Spaceport - Poor',
                  'H': 'Spaceport - Basic',
                  'X': 'None',
                  'Y': 'None'}
    elif upp_type == 'remarks':
        dy_upp = {'Oc': 'Ocean World',
                  'Va': 'Vacuum',
                  'Wa': 'Water World',
                  'Ba': 'Barren',
                  'Di': 'Dieback',
                  'Lo': 'Low Population',
                  'Hi': 'Hi Population',
                  'Ni': 'Non-Industrial',
                  'Ph': 'Pre-High Population',
                  'Pa': 'Pre-Agricultural',
                  'Ag': 'Agricultural',
                  'Na': 'Non-Agrictultural',
                  'Px': 'Prison or Exile Camp',
                  'Pi': 'Pre-Industrial',
                  'In': 'Industrial',
                  'Po': 'Poor',
                  'Pr': 'Pre-Rich',
                  'Ri': 'Rich',
                  'As': 'Asteroid Belt',
                  'De': 'Desert',
                  'Fl': 'Fluid',
                  'Ga': 'Garden World',
                  'Ic': 'Ice-Capped',
                  'He': 'Hell World'}
    elif upp_type == 'atmosphere':
        dy_upp = {'0':  'Vacuum',
                  '1':  'Trace',
                  '2':  'Very thin, tainted',
                  '3':  'Thin',
                  '4':  'Thin, tainted',
                  '5':  'Thin',
                  '6':  'Standard',
                  '7':  'Standad, tainted',
                  '8':  'Dense',
                  '9':  'Dense, tainted',
                  'A':  'Exotic',
                  'B':  'Corrosive',
                  'C':  'Insidious',
                  'D':  'Dense High',
                  'E':  'Thin Low',
                  'F':  'Unusual'
                  }
    elif upp_type == 'size':
        dy_upp = {'0': 'Asteroid Belt',
                  '1': '1,000 miles 1,600 km',
                  '2': '2,000 miles 3,200 km',
                  '3': '3,000 miles 4,800 km',
                  '4': '4,000 miles 6,400 km',
                  '5': '5,000 miles 8,000 km',
                  '6': '6,000 miles 9,600 km',
                  '7': '7,000 miles 11,200 km',
                  '8': '8,000 miles 12,800 km',
                  '9': '9,000 miles 14,400 km',
                  'A': '10,000 miles 16,000 km',
                  'B': '11,000 miles 17,600 km',
                  'C': '12,000 miles 19,200 km',
                  'D': '13,000 miles 20,800 km',
                  'E': '14,000 miles 22,400 km',
                  'F': '15,000 miles 24,000 km'}
    elif upp_type == 'government':
        dy_upp = {'0': 'No Government Structure.',
                  '1': 'Company/ Corporation.',
                  '2': 'Participating Democracy',
                  '3': 'Self-Perpetuating Oligarchy',
                  '4': 'Representative Democracy',
                  '5': 'Feudal Technocracy',
                  '6': 'Captive Government / Colony',
                  '7': 'Balkanization',
                  '8': 'Civil Service Bureaucracy',
                  '9': 'Impersonal Bureaucracy',
                  'A': 'Charismatic Dictatorship' ,
                  'B': 'Non-Charismatic Dictatorship',
                  'C': 'Charismatic Oligarchy',
                  'D': 'Religious Dictatorship',
                  'E': 'Religious Autocracy',
                  'F': 'Totalitarian Oligarchy'}
    elif upp_type == 'law':
        dy_upp = {
            '0': 'No Law. No prohibitions.',
            '1': 'Low Law. Prohibition of WMD, Psi weapons.',
            '2': 'Low Law. Prohibition of “Portable” Weapons.',
            '3': 'Low Law. Prohibition of Acid, Fire, Gas.',
            '4': 'Moderate Law. Prohibition of Laser, Beam.',
            '5': 'Moderate Law. No Shock,EMP,Rad, Mag, Grav.',
            '6': 'Moderate Law. Prohibition of Machineguns.',
            '7': 'Moderate Law. Prohibition of Pistols.',
            '8': 'High Law. Open display of weapons prohibited.',
            '9': 'High Law. No weapons outside the home.',
            'A': 'Extreme Law. All weapons prohibited.',
            'B': 'Extreme Law. Continental passports required.',
            'C': 'Extreme Law. Unrestricted invasion of privacy.',
            'D': 'Extreme Law. Paramilitary law enforcement.',
            'E': 'Extreme Law. Full-fledged police state.',
            'F': 'Extreme Law. Daily life rigidly controlled.',
            'G': 'Extreme Law. Disproportionate punishment.',
            'H': 'Extreme Law. Legalized oppressive practices.',
            'J': 'Extreme Law. Routine oppression.'
            }
    
    if upp_type == 'remarks':
        for x, y in dy_upp.items():
            if upp_value.find(x) >= 0:
                description += y + '. '          
    else:
        description = dy_upp[upp_value]     
    return description


def get_subsector_number_list(subsector):
    
    def get_string(num):
        str_num = str(num)
        if len(str_num) == 1: str_num = '0' + str_num
        return str_num
        
    def get_ranges(front_limits,back_limits):
        return (range(front_limits[0],front_limits[1]+1), range(back_limits[0], back_limits[1]+1))
    
    
    subsector_number_list = []
    

    subsector_letter_dictionary = {
        'A': [[1,8],[1,10]],   
        'B': [[9,16],[1,10]],
        'C': [[17,24],[1,10]],
        'D': [[25,32],[1,10]],
        
        'E': [[1,8],[11,20]],
        'F': [[9,16],[11,20]],
        'G': [[17,24],[11,20]],
        'H': [[25,32],[11,20]],
              
        'I': [[1,8],[21,30]],
        'J': [[9,16],[21,30]],
        'K': [[17,24],[21,30]],
        'L': [[25,32],[21,30]],
        
        'M': [[1,8],[31,40]],
        'N': [[9,16],[31,40]],
        'O': [[17,24],[31,40]],
        'P': [[25,32],[31,40]]
        
        }
    

            
    front_limits = subsector_letter_dictionary[subsector][0]
    back_limits = subsector_letter_dictionary[subsector][1]
    front_digits, back_digits = get_ranges(front_limits,back_limits)



    for each_front in front_digits:
        for each_back in back_digits:
            front_str = get_string(each_front)
            back_str = get_string(each_back)
            subsector_number_list.append(front_str+back_str) 
    
    return subsector_number_list


class Culture_details:
    def __init__(self,
                 age, 
                 appearance,
                 tendency, 
                 materialism, 
                 honesty, 
                 bravery, 
                 social_conflict, 
                 work_ethic, 
                 consumerism,
                 spiritual_outlook, 
                 status_quo_outlook, 
                 custom, 
                 interest,
                 common_skills,
                 materialism_symbol=None,
                 honesty_symbol=None,
                 bravery_symbol=None,
                 social_conflict_symbol=None,
                 work_ethic_symbol=None,
                 consumerism_symbol=None):
        self.age = age
        self.appearance = appearance
        self.tendency = tendency
        self.materialism = materialism
        self.honesty = honesty
        self.bravery = bravery
        self.social_conflict = social_conflict
        self.work_ethic = work_ethic
        self.consumerism = consumerism
        self.spiritual_outlook = spiritual_outlook
        self.status_quo_outlook = status_quo_outlook
        self.custom = custom
        self.interest = interest
        self.common_skills = common_skills
        self.materialism_symbol = materialism_symbol
        self.honesty_symbol = honesty_symbol
        self.bravery_symbol = bravery_symbol
        self.social_conflict_symbol = social_conflict_symbol
        self.work_ethic_symbol = work_ethic_symbol
        self.consumerism_symbol = consumerism_symbol
            
    @staticmethod
    def convert_culture_to_symbol(culture_object):
     
        materialism_dict = {
            'minimal possessions': '--',
            'average'            : '0',
            'modest possessions' : '+',
            'covet possessions'  : '++',
            'n/a'                : 'n/a'
        }
        
        honesty_dict = {
            'scrupulous'         : '++',
            'honour-bound'       : '++',
            'truthful'           : '+',
            'average'            : '0',
            'untrustworthy'      : '-',
            'deceitful'          : '--',
            'n/a'                : 'n/a'
            
        }
        
        bravery_dict = {
            'foolhardy'                  : '++',
            'brave'                      : '+',
            'average'                    : '0',
            'cautious'                   : '-',
            'reject bravery as an ideal' : '--',
            'n/a'                : 'n/a'
    
            }
        
        work_ethic_dict = {
            'beyond driven'      : '++',
            'driven'             : '+',
            'average'            : '0',
            'relaxed'            : '-',
            'very relaxed'       : '--',
            'n/a'                : 'n/a'
    
            }
        
        social_conflict_dict = {
            'thrive on conflict'  : '++',
            'enjoy conflict'      : '+',
            'average'             : '0',
            'conflict adverse'    : '-',
            'conflict phobic'     : '--',
            'n/a'                : 'n/a'
            
            }
        
        consumerism_dict = {
            'wasteful'             : '++',
            'spendthrift'          : '+',
            'average'              : '0',
            'miserly'              : '-',
            'conservative spender' : '--',
            'n/a'                : 'n/a'
            
            }
        
        # Update symbol attributes
        updated_culture_object = Culture_details(
            culture_object.age,
            culture_object.appearance,
            culture_object.tendency,
            culture_object.materialism,
            culture_object.honesty,
            culture_object.bravery,
            culture_object.social_conflict,
            culture_object.work_ethic,
            culture_object.consumerism,
            culture_object.spiritual_outlook,
            culture_object.status_quo_outlook,
            culture_object.custom,
            culture_object.interest,
            culture_object.common_skills,
            materialism_symbol=materialism_dict.get(culture_object.materialism),
            honesty_symbol=honesty_dict.get(culture_object.honesty),
            bravery_symbol=bravery_dict.get(culture_object.bravery),
            social_conflict_symbol=social_conflict_dict.get(culture_object.social_conflict),
            work_ethic_symbol=work_ethic_dict.get(culture_object.work_ethic),
            consumerism_symbol=consumerism_dict.get(culture_object.consumerism)
        )
                
        return updated_culture_object


def save_downloaded_image(response, png_name):
  """Saves the downloaded image content to a file."""
  with open(png_name, 'wb') as f:
    f.write(response.content)           