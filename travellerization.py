def add_traveller_stats(seed_number,db_name,settlement_mod):


#   The goal is to read the Orbital Bodies table generated from the
#   First In program and adjust by the Mainworld_Calc module
#   and build a new table using Traveller 5 stats

#   The output is a new Traveller5 table.  It needs to run after First In, Mainworld_Calc,
#   and Mainworld Selector



#   COMPLETE:  Need to add a routine to get belts and GG totals
#   COMPLETE:  Stellar information added from all three stellar tables
#   2024-05-11 COMPLETE:  updated pbg to include secondary and tertiary stars


    
    import sqlite3
    import random
    import traceback
    import sys
    
    from traveller_functions import tohex, roll_dice
    
    random.seed(seed_number)
    
    
    def capture_primary_stats():
        sql3_select_p_stars = """  SELECT   location, 
                                            luminosity_class, 
                                            spectral_type,
                                            belts,
                                            gg,
                                            orbits
                                    FROM    stellar_bodies WHERE companion_class = '0' """
                                    
        c.execute(sql3_select_p_stars)
        allrows = c.fetchall()
        p_stars_dict = {}
        for row in allrows:
            p_stars_dict[row[0]] = {    'p_lumc'        :row[1],
                                        'p_spec'        :row[2],
                                        'no_belts'      :row[3],
                                        'no_gg'         :row[4],
                                        'worlds'        :row[5]}
    
        return p_stars_dict
    
    def capture_secondary_stats():
        sql3_select_c_stars = """  SELECT   location, 
                                            luminosity_class, 
                                            spectral_type,
                                            belts,
                                            gg,
                                            orbits
                                    FROM    stellar_bodies WHERE companion_class = '1'  """
                                    
        c.execute(sql3_select_c_stars)
        allrows = c.fetchall()
        c_stars_dict = {}
        for row in allrows:
            c_stars_dict[row[0]] = {    'c_lumc'        :row[1],
                                        'c_spec'        :row[2],
                                        'no_belts'      :row[3],
                                        'no_gg'         :row[4],
                                        'worlds'        :row[5]}
    
        return c_stars_dict
        
    def capture_tertiary_stats():
        sql3_select_t_stars = """  SELECT   location, 
                                            luminosity_class, 
                                            spectral_type,
                                            belts,
                                            gg,
                                            orbits
                                    FROM    stellar_bodies WHERE companion_class = '2' OR companion_class = '1.1' """
                                    
        c.execute(sql3_select_t_stars)
        allrows = c.fetchall()
        t_stars_dict = {}
        for row in allrows:
            t_stars_dict[row[0]] = {    't_lumc'        :row[1],
                                        't_spec'        :row[2],                                       
                                        'no_belts'      :row[3],
                                        'no_gg'         :row[4],
                                        'worlds'        :row[5]}
    
        return t_stars_dict    
    
        
       

    
    def create_traveller_tables():
        
        
        sql_create_system_stats_table = """CREATE TABLE system_stats( 
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            location TEXT,
                                            remarks TEXT,
                                            ix TEXT,
                                            ex TEXT,
                                            cx TEXT,
                                            n TEXT,
                                            bases TEXT,
                                            zone TEXT,
                                            pbg TEXT,
                                            w TEXT,
                                            allegiance TEXT,
                                            stars TEXT
                                            );"""
        c.execute('DROP TABLE IF EXISTS system_stats')
        c.execute(sql_create_system_stats_table) 
        
        
        
        sql_create_traveller_stats_table = """CREATE TABLE traveller_stats( 
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            location_orb TEXT,
                                            location TEXT,
                                            system_name TEXT,
                                            starport TEXT,
                                            size INTEGER,
                                            atmosphere INTEGER,
                                            hydrographics INTEGER,
                                            population INTEGER,
                                            government INTEGER,
                                            law INTEGER,
                                            tech_level INTEGER,
                                            main_world INTEGER
                                            
                                            
                                            );"""
        c.execute('DROP TABLE IF EXISTS traveller_stats')
        c.execute(sql_create_traveller_stats_table)
        
        
        
    def get_system_name(name_list):
        names_left = len(name_list)
        name_picked = name_list[random.randrange(0,names_left)]
        name_fixed = name_picked.rstrip('\n')
        name_list.remove(name_picked)
        return name_fixed
    
    def get_starport(location, population):
    # Using First In rules for Starport
        c_starport = 'Z'
        
        dice = roll_dice(3,'Starport A',location, conn, c)
        if population >= 6:
            if dice < population + 3: 
                c_starport = 'A'
                return c_starport
                
        dice = roll_dice(3,'Starport B',location, conn, c)
        if population >= 6:
            if dice < population + 6: 
                c_starport = 'B'
                return c_starport   
    
        dice = roll_dice(3,'Starport C',location, conn, c)
        if dice < population + 9: 
                c_starport = 'C'
                return c_starport
    
        dice = roll_dice(3,'Starport D',location, conn, c)            
        if dice < population + 8:
                c_starport = 'D'
                return c_starport
                
        dice = roll_dice(3,'Starport E',location, conn, c)            
        if dice < 15:
                c_starport = 'E'
                return c_starport
        
        dice = roll_dice(3,'Starport X',location, conn, c)
        c_starport = 'X'
        return c_starport
            
    def get_population(location,settlement_mod):
            pop_adjustment = 0
            if settlement_mod == 1:    # The Settlement Style of Diminished was chosen
                xcoord = int(location[0:2])  # location hex first two characters
                ycoord = int(location[2:4])  # location hex second two characters
                if xcoord >= 12 and xcoord <=22 and ycoord >= 14 and ycoord <=26:
                    pop_adjustment = 3
                elif xcoord <= 4 or xcoord >= 29 or ycoord <=4 or ycoord >=37:
                    pop_adjustment= -2
            
            dice = roll_dice(2,'Population, settlement adj ' + str(pop_adjustment),location, conn, c) - 2 + pop_adjustment
            
            if dice < 0: dice = 0
            if dice >= 10:
              dice = roll_dice(2,'Population after 10+ roll',location, conn, c) + 3
            return dice
            
    def get_belts(location,gg_belt_stats):
        c_no_belts = -1
        c_no_belts = gg_belt_stats[location]['no_belts']
        return c_no_belts
        
    def get_gg(location,gg_belt_stats):
        c_no_gg = -1
        c_no_gg = gg_belt_stats[location]['no_gg']
        return c_no_gg
            
            
    def get_pop_mod(location,population):
        if population != 0:    
            c_pop_mod = str(random.randrange(1,10))
        else:
            c_pop_mod = 0
        return c_pop_mod
        
    def get_bases(location, starport):
        str_base = 'X'
        base_list = list()
        if starport == 'D': 
            dice = roll_dice(2,'Scout Base',location, conn, c)
            if dice <= 7: base_list.append('S')
        elif starport == 'C': 
            dice = roll_dice(2,'Scout Base',location, conn, c)
            if dice <= 6: base_list.append('S')    
        elif starport == 'B': 
            dice1 = roll_dice(2,'Scout Base',location, conn, c)
            dice2 = roll_dice(2,'Naval Base',location, conn, c)
            if dice1 <= 5: base_list.append('S') 
            if dice2 <= 5: base_list.append('N')
        elif starport == 'A':
            dice1 = roll_dice(2,'Scout Base',location, conn, c)
            dice2 = roll_dice(2,'Naval Base',location, conn, c)
            if dice1 <= 4: base_list.append('S') 
            if dice2 <= 6: base_list.append('N')
        
        if 'S' in base_list:
            if 'N' in base_list:
                str_base = 'NS'
            else: str_base = 'S'
        elif 'N' in base_list: str_base = 'N'
        else: str_base = '-'
            
        return str_base
    
    def get_atmosphere(pressure,composition):
        c_atmosphere = -1
        if pressure == 0: c_atmosphere = 0
        elif pressure == 0.1: c_atmosphere = 1
        elif composition == 'Exotic': c_atmosphere = 10
        elif composition == 'Corrosive': c_atmosphere = 11
        elif composition == 'GG': c_atmosphere = 1 #need a function to get GG moon data
        elif composition == 'Standard':
            if pressure < 0.5: c_atmosphere = 3 
            elif pressure < 0.8: c_atmosphere = 5
            elif pressure < 1.2: c_atmosphere = 6
            elif pressure < 1.5: c_atmosphere = 8
            else: c_atmosphere = 13
        elif composition == 'Tainted':
            if pressure < 0.5: c_atmosphere = 2 
            elif pressure < 0.8: c_atmosphere = 4
            elif pressure < 1.2: c_atmosphere = 7
            elif pressure < 1.5: c_atmosphere = 9
            else: c_atmosphere = 12
        
        return c_atmosphere
        
    def get_hydrographics(body, hydro):
        c_hydro = -1
        if body == 'Gas Giant': c_hydro = 1 # add a function to get a GG moon data
        else: c_hydro = hydro
        return c_hydro
        
    def get_size(body, size):
        c_size = -1
        if body == 'Gas Giant': c_size = '1' # add a function to get a GG moon data
        else: c_size = size
        return c_size
    
    def get_government(location, population):
        dice = roll_dice(2,'Government',row[0], conn, c) + population - 7  
        if dice < 0: dice = 0
        elif dice > 15: dice = 15
        if population == 0: dice = 0    
        return dice
        
    def get_law_level(location, government):
        dice = roll_dice(2,'Law Level',row[0], conn, c) + government - 7 
        if dice < 0: dice = 0
        elif dice > 15: dice = 15
        if population == 0: dice = 0
        return dice
        
    def get_tech_level(location, starport, size, atmosphere, hydrographics, population, government):
    
        starport_mod = -100
        starport_mod_dict = {'A':6, 'B':4, 'C':2, 'X':-4}
        if starport in starport_mod_dict.keys():
            starport_mod = starport_mod_dict[starport]
        else: starport_mod = 0
        
        size_mod = -100
        size_mod_dict = {'0':2, '1':2, '2':1, '3':1, '4':1}
        if str(size) in size_mod_dict.keys():
            size_mod = size_mod_dict[str(size)]
        else: size_mod = 0    
        
        int_atmos = int(atmosphere)
        atmosphere_mod = -100
        if int_atmos <= 3: atmosphere_mod = 1
        elif int_atmos >= 10: atmosphere_mod = 1
        else: atmosphere_mod = 0
        
        hydro_mod = -100
        if hydrographics == 9:  hydro_mod = 1
        elif hydrographics == 10: hydro_mod = 2
        else: hydro_mod = 0
        
        pop_mod = -100
        if population <= 5: pop_mod = 1
        elif population == 9: pop_mod = 2
        elif population >= 10: pop_mod = 4
        else: pop_mod = 1
        
        gov_mod = -100
        if government == 0: gov_mod = 1
        elif government == 5: gov_mod = 1
        elif government == 13: gov_mod = -2
        else: gov_mod = 0
        
        dice =  roll_dice(1, 'Tech roll', location, conn, c) \
                + starport_mod \
                + size_mod  \
                + atmosphere_mod \
                + hydro_mod \
                + pop_mod \
                + gov_mod 
#        print ('Tech',starport,dice,starport_mod,size_mod,atmosphere_mod,hydro_mod,pop_mod,gov_mod)
        if population == 0: dice = 0
        return dice
    #    
    def remark_check(*varg):
        rem_result = False
        for i in varg:
            if i[0] in i[1]: 
                rem_result = True
#                print ('In',i[0],i[1])
            else: 
#                print ('Out',i[0],i[1])
                return False
        return rem_result
    
            
        
    def get_remarks(starport, size, atmosphere, hydrographics, population, government):   
        remarks_list = list()
       
        if remark_check((size,(0,)),(atmosphere,(0,)),(hydrographics,(0,))):
            remarks_list.append('As')
    
        atm_de = (2,3,4,5,6,7,8,9)
        hyd_de = (0,)
        if remark_check((atmosphere,atm_de),(hydrographics,hyd_de)):
            remarks_list.append('De')
                
        atm_fl = (10,11,12)
        hyd_fl = (1,2,3,4,5,6,7,8,9,10)
        if remark_check((atmosphere,atm_fl),(hydrographics,hyd_fl)):
            remarks_list.append('Fl')
                
        siz_ga = (6,7,8)
        atm_ga = (5,6,8)
        hyd_ga = (5,6,7)
        if remark_check((size,siz_ga),(atmosphere,atm_ga),(hydrographics,hyd_ga)):
            remarks_list.append('Ga')
    
        siz_he = (3,4,5,6,7,8,9,10,11,12)
        atm_he = (2,4,7,9,10,11,12)
        hyd_he = (0,1,2)
        if remark_check((size,siz_he),(atmosphere,atm_he),(hydrographics,hyd_he)):
            remarks_list.append('He')
                    
        atm_ic = (0,1)
        hyd_ic = (1,2,3,4,5,6,7,8,9,10)
#        print (atmosphere, hydrographics)
#        if remark_check((atmosphere,atm_ic),(hydrographics,hyd_ic)):
#                print('Found ice! <<<<<<<<<<<<<<<<<<<<<<<<<')
#                remarks_list.append('Ic')
#        else: print ('No Ice!')
#        print (remarks_list)
                
                
        siz_oc = (10,11,12)
        atm_oc = (3,4,5,6,7,8,9,10,11,12)
        hyd_oc = (10,)
        if remark_check((size,siz_oc),(atmosphere,atm_oc),(hydrographics,hyd_oc)):
            remarks_list.append('Oc')
                    
        if atmosphere == 0: remarks_list.append('Va')
        
        siz_wa = (3,4,5,6,7,8,9,10)
        atm_wa = (3,4,5,6,7,8,9)
        hyd_wa = (10,)
        if remark_check((size,siz_wa),(atmosphere,atm_wa),(hydrographics,hyd_wa)):
            remarks_list.append('Wa')
    
        pop_ba = (0,)
        gov_ba = (0,)
        law_ba = (0,)
        if remark_check((population,pop_ba),(government,gov_ba),(law_level,law_ba)):
            remarks_list.append('Ba')
                
        if 0 < population < 4: remarks_list.append('Lo')
    
        if 3 < population < 7: remarks_list.append('Ni')
    
        if population == 8: remarks_list.append('Ph')
    
        if population > 8: remarks_list.append('Hi')
        
        atm_pa = (4,5,6,7,8,9)
        hyd_pa = (4,5,6,7,8)
        pop_pa = (4,8)
        if remark_check((atmosphere,atm_pa),(hydrographics,hyd_pa),(population,pop_pa)):
            remarks_list.append('Pa')    
        
        atm_ag = (4,5,6,7,8,9)
        hyd_ag = (4,5,6,7,8)
        pop_ag = (5,6,7)
        if remark_check((atmosphere,atm_ag),(hydrographics,hyd_ag),(population,pop_ag)):
            remarks_list.append('Ag')      
        
        atm_na = (0,1,2,3)
        hyd_na = (0,1,2,3)
        pop_na = (6,7,8,9,10,11,12,13,14,15,16,17,18,19,20)
        if remark_check((atmosphere,atm_na),(hydrographics,hyd_na),(population,pop_na)):
            remarks_list.append('Na')
    
        atm_px = (2,3,10,11)
        hyd_px = (1,2,3,4,5)
        pop_px = (3,4,5,6)
        law_px = (6,7,8,9)
        if remark_check((atmosphere,atm_px),(hydrographics,hyd_px),(population,pop_px),(law_level,law_px)):
            remarks_list.append('Px')
            
        atm_pi = (0,1,2,3,4,7,9)
        pop_pi = (7,8)
        if remark_check((atmosphere,atm_pi),(population,pop_pi)):
            remarks_list.append('Pi')    
            
        atm_in = (0,1,2,3,4,7,9,10,11,12)
        pop_in = (9,10,11,12,13,14,15,16,17,18,19,20)
        if remark_check((atmosphere,atm_in),(population,pop_in)):
            remarks_list.append('In')  
    
        atm_po = (2,3,4,5)
        hyd_po = (0,1,2,3)
        if remark_check((atmosphere,atm_po),(hydrographics,hyd_po)):
            remarks_list.append('Po')        
    
        atm_pr = (6,8)
        pop_pr = (5,9)
        if remark_check((atmosphere,atm_pr),(population,pop_pr)):
            remarks_list.append('Pr')   
       
    
        atm_ri = (6,8)
        pop_ri = (6,7,8)
        if remark_check((atmosphere,atm_ri),(population,pop_ri)):
            remarks_list.append('Ri')   
            
        
       
        return remarks_list
        
    def get_ix(uwp, remarks, bases):
        c_ix = 0
        if uwp[0] in ('A','B'): c_ix += 1
        elif uwp[0] in ('D','E','X'): c_ix -= 1
        if uwp[8] in ['A','B','C','D','E','F','G','H']: c_ix += 1
        if uwp[8] in ['G','H']: c_ix += 1
        if uwp[8] in ['0','1','2','3','4','5','6','7','8']: c_ix -= 1
        if 'Ag' in remarks: c_ix += 1 
        if 'Hi' in remarks: c_ix += 1 
        if 'In' in remarks: c_ix += 1 
        if 'Ri' in remarks: c_ix += 1 
        if uwp[4] in ['0','1','2','3','4','5','6']: c_ix -= 1
        if 'N' in bases:
            if 'S' in bases: c_ix += 1
        
        return c_ix
        
    def get_ex(ix, tech_level, population, remarks, belts, gg, location):
        
        resources = roll_dice(2, 'Ex res', location, conn, c)
        if tech_level >= 8: 
            resources += gg
            resources += belts
        if resources < 0: resources = 0    
        resources = tohex(resources)
            
        labor = population - 1
        if labor < 0: labor = 0
        labor = tohex(labor)
        
        if 'Ba' in remarks: infrastructure = 0
        elif 'Lo' in remarks: infrastructure = 1
        elif 'Ni' in remarks: infrastructure = roll_dice(1, 'Ex infra Ni',location, conn, c) + ix
        else: infrastructure = roll_dice(2, 'Ex infra', location, conn, c) + ix
        if infrastructure < 0: infrastructure = 0
        infrastructure = tohex(infrastructure)
     
        
        efficiency = roll_dice(2, "Ex eff", location, conn, c) - 7
        if efficiency < 0:
            return('(' + str(resources) + str(labor) + str(infrastructure) + str(efficiency) + ')')
        else:    
            return('(' + str(resources) + str(labor) + str(infrastructure) + '+' + str(efficiency) + ')')
            
    
    def get_cx(population, ix, tech_level, location):
        homogeneity = population + roll_dice(2, 'Cx homo', location, conn, c) - 7
        if homogeneity < 1:  homogeneity = 1
        homogeneity = tohex(homogeneity)
        
        acceptance = int(population) + int(ix)
        if acceptance < 1: acceptance = 1  
        acceptance = tohex(acceptance)
    
        
        strangeness = roll_dice(2, 'Cx strange', location, conn, c) - 7 + 5
        if strangeness < 1: strangeness = 1
        strangeness = tohex(strangeness)
        
        symbols = (roll_dice(2, 'Cx symbols', location, conn, c) - 7 + tech_level)
        if symbols < 1: symbols = 1
        symbols = tohex(symbols)
        
        if population == 0: return '[0000]'
        else: return ('[' + str(homogeneity) + str(acceptance) + str(strangeness) + str(symbols) + ']')
        
        
    def get_zone(starport, population, government, law_level):
        zone = '-'
        if starport == 'X':
            zone = 'R'
        
        if (government + law_level) >= 31:  zone = 'R'
        elif (government + law_level) >= 26:  zone = 'A'
        
        return zone
    
    def get_noble(remarks, ix):
        noble_list = list()
    
        if ix >= 4: noble_list.append('f')
        if ('Hi') in remarks: noble_list.append('E')
        elif ('In') in remarks: noble_list.append('E')
        if ('Ph') in remarks: noble_list.append('e')
        if ('Pi') in remarks: noble_list.append('D')
        if ('Ri') in remarks: noble_list.append('C')
        elif ('Ag') in remarks: noble_list.append('C')
        if ('Pa') in remarks: noble_list.append('c')
        elif ('Pr') in remarks: noble_list.append('c')
    
        noble_list.append('B')
        
        return noble_list
        
    def get_worlds(location,gg_belt_stats):
        c_no_worlds = -1
        c_no_worlds = gg_belt_stats[location]['worlds']
        return c_no_worlds
    
    def get_stars(location,p_star_dict,c_star_dict,t_star_dict):
        stars_text = str(p_star_dict[location]['p_spec']) + ' ' +str(p_star_dict[location]['p_lumc'])
        if location in c_star_dict.keys():
            stars_text = stars_text + ' ' + str(
                                            c_star_dict[location]['c_spec']) + ' ' +str(
                                            c_star_dict[location]['c_lumc'])
        
        if location in t_star_dict.keys():
            stars_text = stars_text + ' ' + str(
                                            t_star_dict[location]['t_spec']) + ' ' +str(
                                            t_star_dict[location]['t_lumc'])    
        return stars_text
        
       
    # MAIN PROGRAM
        
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    
    # system names are pulled randomly from the names.txt file
    name_list = open("names.csv", "r").readlines()
    
    p_stars_dict = capture_primary_stats()
    c_stars_dict = capture_secondary_stats()
    t_stars_dict = capture_tertiary_stats()
    
    sector_population = 0
    create_traveller_tables()
    
    try:
    
        sql3_select_locorb = """        SELECT  m.location_orbit, 
                                                m.location, 
                                                o.atmos_pressure,
                                                o.atmos_composition, 
                                                o.body, 
                                                o.hydrographics, 
                                                o.size
                                        FROM main_world_eval m
                                        LEFT JOIN orbital_bodies o
                                        ON m.location_orbit = o.location_orbit
                                        WHERE   m.mainworld_status = 'Y' """

        c.execute(sql3_select_locorb)
        allrows = c.fetchall()
    
    
    except:
        print('Houston - travellerization reading problem')
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
        

    
    for row in allrows:

        system_name = get_system_name(name_list)
#        print(row[0],system_name,'Getting Population and System Details')
        population = get_population(row[0],settlement_mod)
        sector_population += 10**population
        pop_mod = get_pop_mod(row[0],population)
        
                
        belts = get_belts(row[1],p_stars_dict)
        gg = get_gg(row[1],p_stars_dict)
        w = get_worlds(row[1],p_stars_dict)
        
        if row[1] in c_stars_dict:
            belts += get_belts(row[1],c_stars_dict)
            gg += get_gg(row[1],c_stars_dict)
            w += get_worlds(row[1],c_stars_dict)
            
            if  row[1] in t_stars_dict:
                belts += get_belts(row[1],t_stars_dict)
                gg += get_gg(row[1],t_stars_dict)
                w += get_worlds(row[1],t_stars_dict)
                
                
            
        
        
        
        pbg = str(str(pop_mod) + str(belts) + str(gg))
        starport = get_starport(row[0], population)
        bases = get_bases(row[0],starport)
        
        
#        print(row[0],system_name,'Getting World Details')
        try:
            atmosphere = get_atmosphere(row[2],row[3])
            hydrographics = get_hydrographics(row[4],row[5])
            size = get_size(row[4],row[6])
            government = get_government(row[0], population)    
            law_level = get_law_level(row[0], government)
            tech_level = get_tech_level(row[0], starport, size, atmosphere, hydrographics, population, government)
            remarks = get_remarks(starport, size, atmosphere, hydrographics, population, government)
            str_remarks = ' '.join(remarks)
            
        except:
            print('Failed with standard stats')
            break
        
        
        try:
            int_size = size
            uwp = (starport + tohex(int(size))\
                   + tohex(int(atmosphere)) \
                   + tohex(int(hydrographics)) \
                   + tohex(int(population)) \
                   + tohex(int(government)) \
                   + tohex(int(law_level)) \
                   + '-'
                   + tohex(int(tech_level)))
                   
            ix = get_ix(uwp, remarks, bases)
            if ix >= 0:
                str_ix = ('{+' + str(ix) + '}')
            else:
                str_ix = ('{' + str(ix) + '}')
                
            ex = get_ex(ix, tech_level, population, remarks, belts, gg, row[1])
            
            cx = get_cx(population, ix, tech_level, row[1])
            
            zone = get_zone(starport, population, government, law_level)
            allegiance = 'Im'
            n_list = get_noble(remarks, ix)
            n = ''.join(n_list)
            stars = get_stars(row[1],p_stars_dict,c_stars_dict, t_stars_dict)
            main_world = 1
        
        except:
            print('Failed with detailed stats and UWP creation')
            break
        
    

        
##############################################################################################
# Traveler stats will have mainworlds and non-mainworlds 
# System stats are for stats common for the entire system   

        try:     
        
            sqlcommand = '''INSERT INTO traveller_stats(location_orb, 
                                location, 
                                system_name,
                                starport, 
                                size,
                                atmosphere, 
                                hydrographics, 
                                population, 
                                government,
                                law,
                                tech_level,
                                main_world)                                            
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
                                
            body_row =          (str(row[0]),
                                str(row[1]),
                                system_name,
                                starport,
                                size,
                                atmosphere,
                                hydrographics,
                                population,
                                government,
                                law_level,
                                tech_level,
                                main_world)
#            print(body_row)
            c.execute(sqlcommand, body_row)                             
        
        except:
            print('Failed to write into Traveller Stats')
            break
            
        try:
            

        
            sqlcommand = '''    INSERT INTO system_stats(
                                            location, 
                                            bases,
                                            pbg,
                                            remarks,
                                            ix,
                                            ex,
                                            cx,
                                            zone,
                                            n,
                                            allegiance,
                                            w,
                                            stars)                                            
                                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
                                            
                                            
                                
            body_row =          (str(row[1]),
                                bases,
                                pbg,
                                str_remarks,
                                str_ix,
                                ex,
                                cx,
                                zone,
                                n,
                                allegiance,
                                w,
                                stars)
                            
        
                                
  #          print(body_row)
            c.execute(sqlcommand, body_row) 
        except:
            print('Failed to write into System Stats')
            break
    
    
    
    
    sector_population /= 1000000000000
    print('Sector population approx.',round(sector_population,2), 'trillion sophonts.')
    conn.commit()
    conn.close()