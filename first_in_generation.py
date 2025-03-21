def generate_stars(db_name,decisions_provided):

# v1.1.0 2024-05-25 PBG Updated to include binaries

# Sector Generation

    import sqlite3
    import math 
    import random
    from traveller_functions import integer_root, roll_dice

    def create_tables(c,conn):
        sql_create_stellar_bodies = """CREATE TABLE stellar_bodies( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            companion_class TEXT,
            luminosity_class TEXT,
            spectral_type TEXT,
            age REAL,
            temperature REAL,
            luminosity REAL,
            mass REAL,
            radius REAL,
            inner_limit REAL,
            life_zone_min REAL,
            life_zone_max REAL,
            snow_line REAL,
            outer_limit REAL,
            base_orbital_radius REAL,
            bode_constant REAL,
            orbits INTEGER,
            belts INTEGER,
            gg INTEGER,
            s_orbit_description TEXT,
            s_orbital_average REAL,
            s_orbital_ecc REAL,
            min_orbit REAL,
            max_orbit REAL,
            inner_forbidden REAL,
            outer_forbidden REAL,
            companions INTEGER
            );"""
        c.execute('DROP TABLE IF EXISTS stellar_bodies')
        c.execute(sql_create_stellar_bodies) 
        
        
        sql_create_orbital_bodies = """CREATE TABLE orbital_bodies( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_orbit TEXT,
            location TEXT,
            stellar_orbit_no INTEGER,
            planetary_orbit_no INTEGER,
            stellar_distance REAL,
            orbital_radius REAL,
            zone TEXT,
            body TEXT,
            size integer,
            density REAL,
            mass REAL,
            gravity REAL,
            hill_radius REAL,
            natural_moons INTEGER,
            ring TEXT,
            impact_moons INTEGER,
            impact_chance INTEGER,
            year REAL,
            day INTEGER,
            size_class TEXT,
            wtype TEXT,
            atmos_pressure REAL,
            hydrographics INTEGER,
            atmos_composition TEXT,
            temperature INTEGER,
            climate TEXT
            );"""
        c.execute('DROP TABLE IF EXISTS orbital_bodies')
        c.execute(sql_create_orbital_bodies)   
        
        
        sql_create_dice_table = """CREATE TABLE die_rolls( 
            location TEXT,
            number INTEGER,
            reason TEXT,
            total INTEGER
            );"""
        c.execute('DROP TABLE IF EXISTS die_rolls')
        c.execute(sql_create_dice_table)  
        
    
          
        
    def get_multiple_stars(location):
    #   A function that returns the # of companions of the primary (not including sub-companions)
        mult_roll = roll_dice(3,'# of stars',location, conn, c)
        if mult_roll <= MULTIPLE_STAR_CHANCE_S:
            rolled_multiple = 0
        elif mult_roll <= MULTIPLE_STAR_CHANCE_B:
            rolled_multiple = 1
        else:
            rolled_multiple = 2
        return rolled_multiple
        
    def get_luminosity_class(location):
    #   A function that returns the stellar luminosity
        lum_roll = roll_dice(3,'stellar luminosity',location, conn, c)
        if lum_roll <= LUM_CLASS_CHANCE_III:
            rolled_lum = "III"
        elif lum_roll <= LUM_CLASS_CHANCE_V:   
            rolled_lum = "V"
        else:
            rolled_lum = "D"
            
        return rolled_lum   
        
    def get_spectral(location):
    #   A function that returns the spectral class
        spec_roll = roll_dice(3,'spectral class',location, conn, c)
        if spec_roll <= SPEC_CLASS_CHANCE_A:
            rolled_spec = "A"
        elif spec_roll <= SPEC_CLASS_CHANCE_F:
            rolled_spec = "F"
        elif spec_roll <= SPEC_CLASS_CHANCE_G:
            rolled_spec = "G"
        elif spec_roll <= SPEC_CLASS_CHANCE_K:
            rolled_spec = "K"
        else:
            rolled_spec = "M"
        
        subspec_roll = roll_dice(1,'sub spectral class',location, conn, c)
        if subspec_roll <4:
            subspec = "0"
        else:
            subspec = "5"
        finalspec = (rolled_spec + subspec)
        return finalspec
        
    def get_stellarcharsv():
    # Loading the Stellar Characteristics for Class V Table         
        temp_stellarcharsv = {}
        for line in open(r"tables\Star Characteristics V.txt"):
            data = line.strip().split(',')
            temp_stellarcharsv[data[0]] = dict(zip(('temperature', 'luminosity', 'mass', 'radius', 'lifespan'), data[1:]))
          
        return temp_stellarcharsv
    
    def get_stellarcharsiii():
    # Loading the Stellar Characteristics for Class V Table         
        temp_stellarcharsiii = {}
        for line in open(r"tables\Star Characteristics III.txt"):
            data = line.strip().split(',')
            temp_stellarcharsiii[data[0]] = dict(zip(('temperature', 'luminosity', 'mass', 'radius', 'lifespan'), data[1:]))
          
        return temp_stellarcharsiii    
        
        
    def get_companion_separation():
    # Loading the Orbital Separation Table 
        temp_orbitalsep = {}
        for line in open(r"tables\Orbital Separation Table.txt"):
            data = line.strip().split(',')
            temp_orbitalsep[data[0]] = dict(zip(('separation', 'orbital_mod'), data[1:])) 
        
        return temp_orbitalsep
        
    def get_planet_density_table():
    # Loading the Planet Density Table
        temp_planet_density = {}
        for line in open(r"tables\Planet Density Table.txt"):
            data = line.strip().split(',')
            temp_planet_density[data[0]] = dict(zip(('inside_snow_line', 'outside_snow_line'), data[1:])) 
           
        return temp_planet_density
        
    def get_world_type_table():
    # Loading the World Type Table
        temp_world_type = {}
        for line in open(r"tables\World Type Table.txt"):
            data = line.strip().split(',')
            temp_world_type[data[0]] = dict(zip(('Inner Zone', 'Life Zone', 'Middle Zone', 'Outer Zone', 'Forbidden'), data[1:])) 
           
        return temp_world_type
        
    
    def populate_orbit_distance(D,B):
    # Uses a list and Bodes law to return the orbital distances
        od_list = list()
        od_list.append(0) # First items a 0, handles 0 indexing later
        od_list.append(D)
        od_list.append(D + B)
        od_list.append(D + B * 2)
        od_list.append(D + B * 4)
        od_list.append(D + B * 8)
        od_list.append(D + B * 16)
        od_list.append(D + B * 32)
        od_list.append(D + B * 64)
        od_list.append(D + B * 128)
        od_list.append(D + B * 256)
        od_list.append(D + B * 512)
        od_list.append(D + B * 1024)
        od_list.append(D + B * 2048)
        od_list.append(D + B * 999999999)
    
        return od_list


    def find_csd_spectral_type(third_roll,prime_spec_type):
    # Use the spectral type of the primary to find the spectral type of the companion
    # Only used when companion has the same luminosity class as the primary
    
        if third_roll <=3:
            spec_diff = 0
        elif third_roll == 4:
            spec_diff = 1
        elif third_roll == 5:
            spec_diff = 2
        else:
            spec_diff = 3
        
        spec_list = ["A","F","G","K","M"]
        spec_number = spec_list.index(prime_spec_type[0])
        spec_number = spec_number + spec_diff
        if spec_number > 4:
            spec_number = 4
        companion_spec = (spec_list[spec_number] + '5')  # Assume 5 subtype
        return companion_spec

 

    def get_orbit_ecc(o_separation, location):
        ecc_list = list()
        ecc_list = [0.05,0.1,0.2,0.3,0.4,0.4,0.5,0.5,0.5,0.6,0.6,0.7,0.7,0.8,0.9,0.95]
        ecc_roll = roll_dice(3, 'orbital eccentricity',location, conn, c)
        if o_separation == "Very Close":
            ecc_roll = ecc_roll - 6
        elif o_separation == "Close":
            ecc_roll = ecc_roll - 4
        elif o_separation == "Moderate":
            ecc_roll = ecc_roll - 2
    
        if ecc_roll < 3:
            ecc_roll = 3
        elif ecc_roll > 18:
            ecc_roll = 18
        
        #adjust ecc_roll to match list index (0 to 15)
        ecc_roll = ecc_roll - 3
        
        orbit_ecc = 0
        orbit_ecc = ecc_list[ecc_roll]
    
        return orbit_ecc
    
        
    def get_companion_orbit(location,n,sub_companion):
        
        
    #   n represents which number star this is in the system
    #   sub_companion is a boolean indicating if this body is a subcompanion of another companion
    
    
        if (n > 1) and (sub_companion == False):
            die_mod = 13  # First In says +6, but that means the third could be closer than the second
        elif sub_companion == True:
            die_mod = -6
        else:
            die_mod = 0
        sep_roll_lu = "X"
        sep_roll = roll_dice(3,'separation distance',location, conn, c) + die_mod
        if sep_roll <= 6:
            sep_roll_lu = "6"
        elif sep_roll <= 9:
            sep_roll_lu = "9"
        elif sep_roll <= 11:
            sep_roll_lu = "11"
        elif sep_roll <= 14:
            sep_roll_lu = "14"
        else:
            sep_roll_lu = "15"
            
        sep_dict = {}
        sep_dict = COMP_SEP
        
        # Below is the separation description from the Orbital Separation Table
        sep_desc = sep_dict[sep_roll_lu]['separation']                      
        # Below is the radius multiplier from the Orbital Separation Table
        sep_rad_mod = round(float(sep_dict[sep_roll_lu]['orbital_mod']),4)  
        
        sep_rad_roll = roll_dice(2, 'companion orbital_average',location, conn, c)
        orbital_average = float(sep_rad_mod + sep_rad_roll)
        
          
        #check to see if the companion is Distant and has its own companion.  For now mark with an asterisk in Separation description
        own_companion = 0  # assume no companion of its own
        if sep_desc == "Distant":
            check_distant = roll_dice(3, 'distant companion check',location, conn, c)
            if check_distant >= DISTANT_COMPANION_CHANCE:
                sep_desc = "Distant*"
                own_companion = 1 #flag the presence of a companion, which will result in a new stellar body
    
       
        orbital_ecc = float(get_orbit_ecc(sep_desc,location))
        
        min_orbit = (1.00 - orbital_ecc) * orbital_average 
        max_orbit = (1.00 + orbital_ecc) * orbital_average 
        
        inner_forbidden = min_orbit/3
        outer_forbidden = max_orbit*3
       
        comp_orbit_dict = {
                    'sep_desc': sep_desc,
                    'orbital_average': orbital_average,
                    'orbital_ecc': orbital_ecc,
                    'min_orbit': round(min_orbit,2),
                    'max_orbit': round(max_orbit,2),
                    'inner_forbidden' : round(inner_forbidden,2),
                    'outer_forbidden' : round(outer_forbidden,2),
                    'companions': own_companion}
                    
        
                    
        return comp_orbit_dict

    def populate_stellar_dict(location,companion_no,stellar_dict,primary_companions,sub_companion):
    # Generate data for new stellar body - place into dictionary
    # location is hex location in sector
    # stellar_dict is data of the primary if this star is a companion
    # companion_no identifies which primary companion this is (e.g. 0 is primary, 1 is first to orbit primary)
    # sub_companion is a boolean indicating if the body is a subcompanion

        if companion_no > 0:
           

            lum_class_list=['I','III','V']
           

            if stellar_dict["luminosity_class"] == 'D':
                luminosity_class = 'D'
                spec = 'w'
            else:
                sec_lum_roll_a = roll_dice(1, 'comp lum class #1',location, conn, c)
                if sec_lum_roll_a <= 4:
                    luminosity_class = stellar_dict["luminosity_class"]
                    csd_spec_roll = roll_dice(1, 'comp spec roll',location, conn, c)
                    spec = find_csd_spectral_type(csd_spec_roll,stellar_dict["spectral_type"])
                else:
                    lum_class_index = lum_class_list.index(stellar_dict["luminosity_class"])
                    if sec_lum_roll_a == 5:
                        lum_class_index += 1
                    else:
                        lum_class_index += 2
                        
                    if lum_class_index < 3:
                        luminosity_class = lum_class_list[lum_class_index]
                    else:
                        sec_lum_roll_b = roll_dice(1, 'comp lum class #2',location, conn, c)
                        if sec_lum_roll_b <= 4:
                            luminosity_class = 'V'
                            
                        else:
                            luminosity_class = 'D'
                    
                    if luminosity_class == 'D':
                        spec = 'w'
                    elif luminosity_class in lum_class_list:
                        csd_spec_roll = roll_dice(1, 'comp spec roll',location, conn, c)
                        spec = find_csd_spectral_type(csd_spec_roll,stellar_dict["spectral_type"])
                    else:
                        luminosity_class = 'X'
                        spec = 'X'

            


         
        else:
    
            luminosity_class = get_luminosity_class(location)

            if luminosity_class == "D":
                    spec = "w"
            else:
                    spec = get_spectral(location)
    
        if luminosity_class == 'V':
            stellar_temp = CHARSV[spec]["temperature"]
            stellar_luminosity = CHARSV[spec]["luminosity"]
            stellar_mass = CHARSV[spec]["mass"]
            stellar_radius = CHARSV[spec]["radius"]
            temp_stellar_lifespan = CHARSV[spec]["lifespan"]
            # for main sequence(V) planets this number is maximum age.  
            # We need to assign an age for this particular star
            adjust_age = roll_dice(2, 'stellar age',location, conn, c)
            if adjust_age > float(temp_stellar_lifespan):
                adjust_age = temp_stellar_lifespan
            stellar_lifespan = str(adjust_age)
            

        elif luminosity_class == 'III':
            stellar_temp = CHARSIII[spec]["temperature"]
            stellar_luminosity = CHARSIII[spec]["luminosity"]
            stellar_mass = CHARSIII[spec]["mass"]
            stellar_radius = CHARSIII[spec]["radius"]
            stellar_lifespan = CHARSIII[spec]["lifespan"]    
        
                 
        else:
            stellar_temp = 0
            stellar_luminosity = 0.001
            stellar_mass = 0.14 + (roll_dice(3, 'wD Mass', location, conn, c) * 0.04)
            stellar_radius = 0.00003
            stellar_lifespan = 0


        # companion info
        

        if companion_no == 0:
            comp_orbit_dict = {
                    'sep_desc': 'Primary',
                    'orbital_average' : 0,
                    'orbital_ecc': 'NA',
                    'min_orbit': 0,
                    'max_orbit': 0,
                    'inner_forbidden': 0,
                    'outer_forbidden': 0,
                    'companions': primary_companions}
        else:
            comp_orbit_dict = get_companion_orbit(location,companion_no,sub_companion)


        if sub_companion == True: 
            companion_no += 0.1
            
            
        # if this stellar body is a companion, overwrite the calculated age with the primary
        if companion_no > 0:
            stellar_lifespan = stellar_dict['age']


        stellar_dict = {"location"            : location,
                        "companion_class"     : companion_no,
                        "luminosity_class"    : luminosity_class,
                        "spectral_type"       : spec,
                        "temperature"         : stellar_temp,
                        "luminosity"          : stellar_luminosity,
                        "mass"                : stellar_mass,
                        "radius"              : stellar_radius,
                        "age"                 : stellar_lifespan,
                        "inner_limit"         : -1,
                        "lz_min"              : -1,
                        "lz_max"              : -1,
                        "snow_line"           : -1,
                        "outer_limit"         : -1,
                        "base_orbital_radius" : -1,
                        "bode_constant"       : -1,
                        "orbits"              : -1,
                        "belts"               : -1,
                        "gg"                  : -1,
                        "orbit_description"   : comp_orbit_dict['sep_desc'],
                        "orbital_average"     : comp_orbit_dict['orbital_average'],
                        "orbital_ecc"         : comp_orbit_dict['orbital_ecc'],
                        "min_orbit"           : comp_orbit_dict['min_orbit'],
                        "max_orbit"           : comp_orbit_dict['max_orbit'],
                        "inner_forbidden"     : comp_orbit_dict['inner_forbidden'],
                        "outer_forbidden"     : comp_orbit_dict['outer_forbidden'],
                        "companions"          : comp_orbit_dict['companions']}
    
                            
        return stellar_dict


    def populate_stellar_orbit_info(location, stellar_dict_list):
            
        #receive a list of dictionaries of stellar bodies in a system and add orbit info
        #if companions are very close, temporarily combine their mass and luminosity for orbit purposes
        #in such cases the orbit info goes to the primary and the companion's orbit info is 0
        
        return_list = []
        
        for ix_star, star_dict in enumerate(stellar_dict_list):

            
            if star_dict['orbit_description'] == 'Very Close':
                stellar_mass = 0
                stellar_luminosity = 0
            elif star_dict['companions'] == 0:
                stellar_mass = float(star_dict['mass'])
                stellar_luminosity = float(star_dict['luminosity'])
            
            else: 
                companion_orbit = stellar_dict_list[ix_star+1]['orbit_description']
                if companion_orbit == 'Very Close':
                    stellar_mass = float(star_dict['mass']) + \
                    float(stellar_dict_list[ix_star+1]['mass']) 
                    stellar_luminosity = float(star_dict['luminosity']) + \
                    float(stellar_dict_list[ix_star+1]['luminosity'])
                else:
                    stellar_mass = float(star_dict['mass'])
                    stellar_luminosity = float(star_dict['luminosity'])
               
        
            r1 = 0.2 * stellar_mass   # using First In detailed gen rules 
            r2 = 0.0088 * (stellar_luminosity ** 0.5)
            
            if r1 > r2: orbital_inner_limit = r1 
            else: orbital_inner_limit = r2
            
            orbital_lz_min = 0.95 * (stellar_luminosity ** 0.5)
            orbital_lz_max = 1.3 * (stellar_luminosity ** 0.5)
            orbital_snow_line = 5 * (stellar_luminosity ** 0.5)
            orbital_outer_limit = 40 * stellar_mass    
            if orbital_outer_limit < 10: orbital_outer_limit = 10
                    
            base_orbital_radius_int = (roll_dice(1,'base orbital radius',location, conn, c) + 1)
            base_orbital_radius = float(base_orbital_radius_int/2)
            base_orbital_radius = float(base_orbital_radius) * float(orbital_inner_limit)
            bode_roll = roll_dice(1,'bode constant roll',location, conn, c)
            if bode_roll < 3:
                bode_constant = 0.3
            elif bode_roll < 5:
                bode_constant = 0.35
            else:
                bode_constant = 0.4
        
            orbits_distance_list = list()
            orbits_distance_list = populate_orbit_distance(base_orbital_radius, bode_constant)
                
            orbits = -1
            loop_a = 0
        
            if base_orbital_radius > 0:
                while (float(orbits_distance_list[loop_a]) < float(orbital_outer_limit)):
                    loop_a = loop_a + 1

            orbits = loop_a - 1 #above while will go one too far, needs to be corrected
    
    
            star_dict["inner_limit"] = round(orbital_inner_limit,3)
            star_dict["lz_min"] = round(orbital_lz_min,3)
            star_dict["lz_max"] = round(orbital_lz_max,3)
            star_dict["snow_line"] = round(orbital_snow_line,3)
            star_dict["outer_limit"] = round(orbital_outer_limit,3)
            star_dict["base_orbital_radius"] = round(base_orbital_radius,3)
            star_dict["bode_constant"] = round(bode_constant,3)
            star_dict["orbits"] = orbits
            star_dict["distance_list"] = orbits_distance_list
            
            return_list.append(star_dict)
            
        return return_list



    
    def get_size(r,z,s,location):
    # returns the planetary size
    # r = orbit number 
    # z = zone type 
    # s = spectral type
    
        size_roll = roll_dice(2, 'size roll',location, conn, c)
    
        if r == 1:
            size_roll = size_roll - 4
        elif z == "Inner Zone":
            size_roll = size_roll - 2
        elif z != "Outer Zone":
            size_roll = size_roll + 4
        
        if s == "M0":
            size_roll = size_roll - 1
        elif s == "M5":
            size_roll = size_roll - 2
            
        if size_roll < 1:
            size_roll = 1
        
        return size_roll
    
    def get_gg_size(r,z,s,location):
        gg_size_int = get_size(r,z,s,location)
        gg_size_int = gg_size_int * 5
        if gg_size_int < 25: gg_size_int = 25
        return gg_size_int
    
    
    def get_gg_density(gg_size):
        gg_density = 0.0
        if gg_size < 40: gg_density = 1.4
        elif gg_size < 60: gg_density = 1.0
        elif gg_size < 80: gg_density = 0.7
        elif gg_size < 85: gg_density = 1.0
        else: gg_density = 1.4
        return gg_density    
            
    def get_planet_density(p_star_dict,zone,planet_size,location):
        density_float = 0
        age_float = float(p_star_dict["age"])
        age_mod = age_float / 2
        density_roll = roll_dice(3, 'density roll',location, conn, c)
        density_float = (density_roll - age_mod)/10
        size_adjust = planet_size
        if size_adjust <= 3:
            size_adjust = 3
        elif size_adjust <= 5:
            size_adjust = 5
        elif size_adjust <= 8:
            size_adjust = 8
        else:
            size_adjust = 1000
        
        density_final = -10    
        density_age_dict = {}
        density_age_dict = get_planet_density_table()
        if zone == "Outer Zone":
            size_str = str(size_adjust)
            density_look = float(density_age_dict[size_str]["outside_snow_line"])
            density_final = density_look + density_float
    
        else:
            size_str = str(size_adjust)
            density_look = float(density_age_dict[size_str]["inside_snow_line"])
            density_final = density_look + density_float
    
           
        return density_final
    
    def get_hill_radius(distance,mass_planet,mass_star):
        # from Architect of Worlds
        # used to create moons
        # distance = min distance from planet to star
        
        part_one = (2.17 * 10**6) * distance
        temp = float(mass_planet)/float(mass_star)
        part_two = integer_root(3,temp)
        hill_radius = round(part_one * part_two,2)
        return hill_radius
    
    def get_major_natural_satellites(hill_radius, current_distance):
        # from Architect of Worlds
        # used to calculate large satellites forming naturally via accretion
        part_one = (2 * 10 ** -15)
        part_two = (hill_radius**2) / integer_root(2,current_distance)
        moons = part_one * part_two
        moons = int(moons)
        if moons >8:  moons =8
        return moons
    
    def get_major_impact_satellites(hill_radius, radius, location):
        # from Architect of Worlds
        # used to calculate large satellites forming from impact
        chance = round(hill_radius/radius,0)
        moon = 0
        if chance > 300:
            moon_check = roll_dice(1,'impact satellite chance',location, conn, c)
            if moon_check >= 5:
                moon = 1
            else: 
                moon = 0
        return [chance,moon]
            
    
    def get_year(mass, distance):
        # return the planetary year in earth years (orbital period)
        # mass = mass of the primary
        # distance = orbital radius of planet
        distance_float = float(distance)
        mass_float = float(mass)
        temp_year = (distance_float**3) / mass_float
        temp_year = round(math.sqrt(temp_year),2)
        return temp_year
        
    def get_day(size, location):
        # return the planetary day in earth hours (rotation period)
        # size is planetary size_adjust
        # First In also used Tidal Lock, not used here
        
        day_roll = roll_dice(3, 'day roll', location, conn, c)
        day_mod = 0
        
        if size != 0:
            if size < 3:
                day_mod = 10
            elif size <6:
                day_mod = 8
            elif size <9:
                day_mod = 6
            else:
                day_mod = -1
            day_int = day_roll + day_mod
        else:
            day_int = 0
        
        return day_int
        
    def get_world_size_class(world_mass, world_size, body_type):
    
        world_size_class = "Not Found"
        if body_type == "Planetoid Belt":
            world_size_class = "Belt"
        elif body_type == "Gas Giant":
            world_size_class = "Gas Giant"
        elif body_type == "Lost":
            world_size_class = "Lost"
        elif body_type == "Planet":
            world_size_parameter = round((7.93) * world_mass / world_size,2)
            if world_size_parameter <= .13:
                world_size_class = "Tiny"
            elif world_size_parameter <= .24:
                world_size_class = "Very Small"
            elif world_size_parameter <= .38:
                world_size_class = "Small"
            elif world_size_parameter <= 1.73:
                world_size_class = "Standard"
            else:
                world_size_class = "Large"
        else:
            world_size_class = "Enigma"
        
        return world_size_class
    
    def get_world_type(size_class, zone):    
        world_type_var = "Something Crazy"
        world_type_var = WORLD_TYPE[size_class][zone]
        return world_type_var
        
    def get_atmos_pressure(size_class, world_type, location):
        atmos_var = -1
        if size_class == 'Tiny':
            atmos_var = 0.0
        elif size_class == 'Very Small':
            atmos_var = 0.1
        elif world_type == 'Belt':
            atmos_var = 0.0
        elif world_type == 'Gas Giant':
            atmos_var = 10.0
        elif world_type == 'Greenhouse':
            atmos_var = 2.0
        else:
            atmos_var = roll_dice(3,'atmos roll',location, conn, c) * 0.1
            
        return atmos_var
            
    def get_hydro_pct(size_class, world_type, atmos_pressure, zone, primary_type, orbit_distance, snow_line, location):
        clear_for_hydro = True
        hydro_var = -1
        hydro_mod = 0
        ok_class = ('Large', 'Standard', 'Small')
        ok_atmos = 0.2
        not_ok_zone = ('Inner')
        
        if str(size_class) not in ok_class:
            clear_for_hydro = False
            hydro_var = -2
            
        if float(atmos_pressure) < float(ok_atmos):
            clear_for_hydro = False
            hydro_var = -3
            
        if zone == not_ok_zone:
            clear_for_hydro = False
            hydro_var = -4
            
        if float(orbit_distance) > (float(snow_line) * 3):
            clear_for_hydro = False
            hydro_var = -5
     
        if primary_type[0] == 'M': hydro_mod += 2
        if primary_type[0] == 'K': hydro_mod += 1
        if primary_type[0] == 'F': hydro_mod -= 1
        if primary_type[0] == 'A': hydro_mod -= 2
        
        if world_type[0] == 'D':
            if zone == 'Life Zone': hydro_mod -= 8
            elif zone == 'Middle Zone': hydro_mod -= 6
        elif world_type[0] == 'H': hydro_mod -= 2
    
     
        if clear_for_hydro == True:
            hydro_var = roll_dice(2, 'hydro roll',location, conn, c) - 2
           
        hydro_var = hydro_var + hydro_mod
        
        if hydro_var < 0: hydro_var = 0
        if hydro_var > 10: hydro_var = 10
        
       
        return hydro_var
     
    def check_sulfur(location):
            if roll_dice(3, 'sulfur roll',location, conn, c) > 12:
                atm = 'Corrosive'
            else:
                atm = 'Exotic'
            return atm
            
    def check_pollutant(location):
            if roll_dice(3, 'tainted roll',location, conn, c) > 11:
                atm = 'Tainted'
            else:
                atm = 'Standard'
            return atm
                
                
    def get_atmos_comp(world_type,location):
        get_atmos_c_var = 'N/A'
        if world_type.find('(SG)') > 0:
            get_atmos_c_var = 'Corrosive'
        elif world_type.find('(A)') > 0:
            get_atmos_c_var = 'Corrosive'
        elif world_type.find('(N)') > 0:
            get_atmos_c_var = check_sulfur(location)
        elif world_type.find('Gas') == 0:
            get_atmos_c_var = 'GG'
        elif world_type[0] == 'D':
            get_atmos_c_var = check_sulfur(location)
        elif world_type.find('Green') == 0:
            get_atmos_c_var = 'Corrosive'
        elif world_type[0] == 'O':
            get_atmos_c_var = check_pollutant(location)
        else: get_atmos_c_var = 'None'
        
        return get_atmos_c_var
    
        
    def get_albedo(world_type, hydro):
        c_albedo = -1
        if world_type.find('(SG)') > 0:
            c_albedo = 0.50
        elif world_type.find('(A)') > 0:
            c_albedo = 0.50
        elif world_type.find('(N)') > 0:
            c_albedo = 0.20
        elif world_type[0] == 'D':
            c_albedo = 0.02
        elif world_type[0] == 'R':
            c_albedo = 0.02
        elif world_type[0] == 'I':
            c_albedo = 0.45
        elif world_type[0] == 'O':
            if hydro < 3:
                c_albedo = 0.02
            elif hydro < 6:
                c_albedo = 0.10
            elif hydro < 9:
                c_albedo = 0.20
            else:
                c_albedo = 0.28
        
        return c_albedo
    
    def get_greenhouse(world_type, atmos_pressure, gravity):
        c_greenhouse = -1
        greenhouse_factor = -1
        if world_type[0] == 'H':
            c_greenhouse = 0.2
        elif world_type[0] == 'O':
            c_greenhouse = 0.15
        elif world_type[0] == 'D':
            c_greenhouse = 0.10
        else:
            c_greenhouse = 0.00
        
        if gravity > 0:
            greenhouse_factor = c_greenhouse * (atmos_pressure / gravity)
        else:
            greenhouse_factor = 0
        return greenhouse_factor
        
    def get_blackbody(luminosity, orbit_distance):
        c_blackbody = -1
        c_blackbody = (278 * (integer_root(4,luminosity)) / (math.sqrt(orbit_distance)))
        return c_blackbody
        
    def get_temperature(world_type, hydro, atmos_pressure, gravity, luminosity, orbit_distance,location):
        albedo = get_albedo(world_type, hydro)
        greenhouse = get_greenhouse(world_type, atmos_pressure, gravity)
        blackbody = get_blackbody(luminosity, orbit_distance)
        c_temperature = -1
    
        c_temperature = blackbody * (integer_root(4,1 - albedo)) * (1 + greenhouse)
        
        return round(c_temperature,2)
        
    def get_climate(temperature, world_type):
        c_climate = 'N/A'
        if world_type[0] == 'O':
            if temperature <= 238: c_climate = 'Uninhabitable (Frigid)'
            elif temperature <= 249: c_climate = 'Frozen'
            elif temperature <= 260: c_climate = 'Very Cold'
            elif temperature <= 272: c_climate = 'Cold'
            elif temperature <= 283: c_climate = 'Chilly'
            elif temperature <= 294: c_climate = 'Cool'
            elif temperature <= 302: c_climate = 'Earth-normal'
            elif temperature <= 308: c_climate = 'Warm'
            elif temperature <= 313: c_climate = 'Tropical'
            elif temperature <= 319: c_climate = 'Hot'
            elif temperature <= 324: c_climate = 'Very Hot'
            else: c_climate = 'Uninhabitable (Torrid)'
        return c_climate
    
        
    def populate_orbital_body_table(ob_db_key,
                                        location,
                                        stellar_orbit_no,
                                        planetary_orbit_no,
                                        stellar_distance,
                                        orbital_radius,
                                        zones,
                                        zone_objects,
                                        size,
                                        density,
                                        mass,
                                        gravity,
                                        hill_radius,
                                        natural_moons,
                                        ring,
                                        impact_moons,
                                        impact_chance,
                                        year,
                                        day,
                                        size_class,
                                        wtype,
                                        atmos_press,
                                        hydro_pct,
                                        atmos_comp,
                                        temperature,
                                        climate):
        sqlcommand = '''    INSERT INTO orbital_bodies 
                    (location_orbit, 
                    location, 
                    stellar_orbit_no, 
                    planetary_orbit_no,
                    stellar_distance,
                    orbital_radius,
                    zone, 
                    body, 
                    size, 
                    density,
                    mass,
                    gravity,
                    hill_radius,
                    natural_moons,
                    ring,
                    impact_moons,
                    impact_chance,
                    year,
                    day,
                    size_class,
                    wtype,
                    atmos_pressure,
                    hydrographics,
                    atmos_composition,
                    temperature,
                    climate) 
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
                                            
        body_row =          (str(ob_db_key),
                            str(location),
                            stellar_orbit_no,
                            planetary_orbit_no,
                            stellar_distance,
                            orbital_radius,
                            zones,
                            zone_objects,
                            size,
                            density,
                            mass,
                            gravity,
                            hill_radius,
                            natural_moons,
                            ring,
                            impact_moons,
                            impact_chance,
                            year,
                            day,
                            size_class,
                            wtype,
                            atmos_press,
                            hydro_pct,
                            atmos_comp,
                            temperature,
                            climate)
                            
        
        c.execute(sqlcommand, body_row)  
        
    def populate_planets(location,dict_list):
        # location is the parsec location

        # dict list is a list of dictionaries for stars in the location

        new_star_list = []
        

        
        for star_no, star in enumerate(dict_list):
            forbidden_planet = False
            orbit_adjust = 0
            no_gg = 0
            no_belts = 0
            orbits = int(star['orbits'])
            if orbits > 0:
                distance_list = star['distance_list']
                for planet_no in range(1,orbits+1):
                    ob_db_key = (str(location) + '-' + str(star['companion_class']) + '-' + str(planet_no)) 
                                        
                    current_distance = round(distance_list[planet_no],4)


                    # If the current star has a companion, we need to load the companion's forbidden zone
                    
                    if star['companions'] > 0:
                        comp_inner_forbidden = dict_list[star_no+1]['inner_forbidden']
                        comp_outer_forbidden = dict_list[star_no+1]['outer_forbidden']
                        if comp_inner_forbidden < current_distance < comp_outer_forbidden:
                            zones = "Forbidden"
                            zone_objects = "Lost"
                            size = 0
                            density = 0                    
                            mass = 0
                            gravity = 0
                            orbit_adjust -= 1        
                            forbidden_planet = True
  #                          print(location, star_no, planet_no, 'companion forbidden', current_distance)

                    # We now build the planet using details from its current star


                    if forbidden_planet == False:    
                        if current_distance < float(star["inner_limit"]):
                            zones= "Beyond Inner"
                            zone_objects = "Vapour"
                            size = 0
                            density = 0     
                            mass = 0
                            gravity = 0
                            orbit_adjust -= 1
                            print(location, star_no, planet_no, 'Beyond Inner', current_distance)
                            
                        elif current_distance < float(star["lz_min"]):
                            zones = "Inner Zone"
                            gg_check = roll_dice(3,'GG check',ob_db_key, conn, c)
                            if gg_check <= 3:
                                zone_objects = "Gas Giant"
                                size = get_gg_size(planet_no,zones,star["spectral_type"],location)
                                density= get_gg_density(size)
                                no_gg += 1
                            else:
                                planetoid_roll = roll_dice(3, 'planetoid check',ob_db_key, conn, c)
                                if planetoid_roll <= 6:
                                    zone_objects = "Planetoid Belt"
                                    size = 0
                                    density = 0
                                    no_belts += 1
                                else:
                                    zone_objects = "Planet"
                                    size = get_size(planet_no,zones,star["spectral_type"],location)
                                    density = get_planet_density(star, zones, size,location)
                                    
                        elif current_distance < float(star["lz_max"]):
                            zones = "Life Zone"
                            gg_check = roll_dice(3,'GG check',ob_db_key, conn, c)
                            if gg_check <= 4:
                                zone_objects = "Gas Giant"
                                size = get_gg_size(planet_no,zones,star["spectral_type"],location)
                                density= get_gg_density(size)
                                no_gg += 1
                            else:
                                planetoid_roll = roll_dice(3, 'planetoid check',ob_db_key, conn, c)
                                if planetoid_roll <= 6:
                                    zone_objects = "Planetoid Belt"
                                    size = 0
                                    density = 0
                                    no_belts += 1
                                else:
                                    zone_objects = "Planet"
                                    size = get_size(planet_no,zones,star["spectral_type"],location)
                                    density = get_planet_density(star, zones, size,location)
    
                                    
                        elif current_distance < float(star["snow_line"]):
                            zones = "Middle Zone"
                            gg_check = roll_dice(3,'GG check',ob_db_key, conn, c)
                            if gg_check <= 7:
                                zone_objects="Gas Giant"
                                size = get_gg_size(planet_no,zones,star["spectral_type"],location)
                                density= get_gg_density(size)
                                no_gg += 1
                            else:
                                planetoid_roll = roll_dice(3, 'planetoid check',ob_db_key, conn, c)
                                if planetoid_roll <= 6:
                                    zone_objects = "Planetoid Belt"
                                    size = 0
                                    density = 0
                                    no_belts += 1
                                else:
                                    zone_objects = "Planet"
                                    size = get_size(planet_no,zones,star["spectral_type"],location)
                                    lookup_density = get_planet_density(star, zones[planet_no], size,location)
                                    density = lookup_density
                                    
                                    
                        elif current_distance >= float(star["snow_line"]):
                        
                            zones = "Outer Zone"
                            gg_check = roll_dice(3,'GG check',ob_db_key, conn, c)
                            if gg_check <= 14:
                                zone_objects = "Gas Giant"
                                size = get_gg_size(planet_no,zones,star["spectral_type"],location)
                                density= get_gg_density(size)
                                no_gg += 1
                            else:
                                planetoid_roll = roll_dice(3, 'planetoid check',ob_db_key, conn, c)
                                if planetoid_roll <= 6:
                                    zone_objects = "Planetoid Belt"
                                    size = 0
                                    density = 0
                                    no_belts += 1
                                else:
                                    zone_objects = "Planet"
                                    size = get_size(planet_no,zones,star["spectral_type"],location)
                                    density = get_planet_density(star, zones, size,location)
    
    
    
                            
                        else:
                            zones = "Test"
                            zone_objects = "Test"
                            size = -99
                            density = -99
                            mass = -99
                            gravity = -99
                            year =360
                            day = 24
                            size_class = 0
                            wtype = 'Test'
                            atmos_press = 0
                            hydro_pct = 0
                            atmos_comp = 0
                            temperature = 0
                            climate = "Test"
                            
                    

    
                        mass = round((density * (size**3)) / 2750 ,2)


                        
                        if size == 0:
                            gravity = 0
                            hill_radius = 0
                            natural_moons = 0
                            impact_chance = 0
                            impact_moons = 0
                        else:
                            gravity = round((62.9 * mass) / (size ** 2),2)
                        
                            hill_radius = get_hill_radius(mass,current_distance,star["mass"])
                            
                            radius = size/2 * 1609.3
                            
                            natural_moons = get_major_natural_satellites(hill_radius, current_distance )
                            if size < 25:
                                impact_chance, impact_moons = get_major_impact_satellites(hill_radius, radius, location)
                            else:
                                impact_chance = 0
                                impact_moons = 0
                        
                        
                        if natural_moons > 0:
                            ring_roll = roll_dice(3,"ring check",ob_db_key, conn, c)
                            if ring_roll < 6:
                                ring = 'None'
                            elif ring_roll <= 9:
                                ring = 'Thin'
                            elif ring_roll <= 13:
                                ring = 'Moderate'
                            elif ring_roll <=19:
                                ring = 'Dense'
                            else:
                                ring = 'Magic'
                        else:
                            ring = 'None'
                        
                        
                        year = get_year(star["mass"],current_distance)
                        day = get_day(size,location)
                        size_class = get_world_size_class(mass,size,zone_objects)
                        wtype = get_world_type(size_class, zones)
                        atmos_press = round(get_atmos_pressure(size_class, wtype,location),2)
                        
                        hydro_pct = get_hydro_pct( size_class, 
                                                        wtype,
                                                        atmos_press,
                                                        zones,
                                                        star["spectral_type"],
                                                        current_distance,
                                                        star["snow_line"],
                                                        location)
                                                        
                        atmos_comp = get_atmos_comp(wtype,location)
                        temperature = get_temperature(wtype, 
                                                            hydro_pct, 
                                                            atmos_press,
                                                            gravity,
                                                            star["luminosity"],
                                                            current_distance,
                                                            location)
        
                        climate = get_climate(temperature, wtype)
    

    
                        
#                        print(ob_db_key)
    
    
    
                        
                        populate_orbital_body_table(
                                            ob_db_key,
                                            location,
                                            planet_no,
                                            0,                     # 0 for planets
                                            current_distance,
                                            current_distance,
                                            zones,
                                            zone_objects,
                                            size,
                                            density,
                                            mass,
                                            gravity,
                                            hill_radius,
                                            natural_moons,
                                            ring,
                                            impact_moons,
                                            impact_chance,
                                            year,
                                            day,
                                            size_class,
                                            wtype,
                                            atmos_press,
                                            hydro_pct,
                                            atmos_comp,
                                            temperature,
                                            climate)

            
            
                       
                        if natural_moons > 0:
                            for m in range(1, natural_moons+1):
                                
                                moon_key = str(ob_db_key) + '-n' + str(m) # Note 'n' for natural accretion moon

                                moon_orbital_radius_roll = roll_dice(1,'moon_radius', moon_key, conn, c)
                                
                                moon_orbital_radius_km = ((moon_orbital_radius_roll + 2) * (1.8 * m)) * radius
                                moon_orbital_radius = round(moon_orbital_radius_km / 149597870.700,3)  # convert to AU
                                zone_objects =  "Natural Moon"

                                mass_roll = roll_dice(3,'moon mass roll',moon_key, conn, c)

                                part_one = mass_roll * mass
                            
                                try:
                                    part_two = part_one / natural_moons

                                except:
                                    part_two = 0
                                    print('problem:',moon_key,natural_moons)
                                    
                                part_three = (.0001 ) * part_two    
                                moon_mass = round(part_three,4)

                                
                                density_roll = roll_dice(3, 'moon density roll', moon_key, conn, c)
                                moon_density = round((integer_root(5,moon_mass)) + ((density_roll - 10)/100),2)
                                
                                if moon_density == 0:
                                    moon_size = 0
                                    print('Zero density moon!',moon_key)
                                else:
                                    moon_size = round((6370 * (integer_root(3,(moon_mass/moon_density)))) * 2 / 1609.3,0)
                                
                                moon_gravity = round(integer_root(3,(moon_mass*(moon_density**2))),2)
                                
                                hill_radius = 'N/A'
                                moon_natural_moons = 0
                                moon_impact_moons = 0
                                moon_impact_chance = 0
                                
                                moon_year = get_year(mass,moon_orbital_radius)
                                moon_day = get_day(moon_size,moon_key)
                                
                                if moon_size == 0: moon_body = 'Planetoid Belt'
                                else: moon_body = 'Planet'
                                
                                moon_size_class = get_world_size_class(moon_mass,moon_size,moon_body)
                                moon_wtype = get_world_type(moon_size_class, zones)
                                moon_atmos_press = get_atmos_pressure(moon_size_class, moon_wtype,moon_key)
                                
                                moon_hydro_pct = get_hydro_pct( moon_size_class, 
                                                                moon_wtype,
                                                                moon_atmos_press,
                                                                zones,
                                                                star["spectral_type"],
                                                                current_distance,
                                                                star["snow_line"],
                                                                moon_key)
                                                                
                                moon_atmos_comp = get_atmos_comp(moon_wtype,moon_key)
                                moon_temperature = get_temperature(moon_wtype, 
                                                                    moon_hydro_pct, 
                                                                    moon_atmos_press,
                                                                    moon_gravity,
                                                                    star["luminosity"],
                                                                    current_distance,
                                                                    moon_key)
                
                                moon_climate = get_climate(moon_temperature, moon_wtype)
                                ring = 'None'
                                
                                
                                populate_orbital_body_table(
                                        moon_key,
                                        location,
                                        planet_no,
                                        m,
                                        current_distance,
                                        moon_orbital_radius,
                                        zones,
                                        zone_objects,
                                        moon_size,
                                        moon_density,
                                        moon_mass,
                                        moon_gravity,
                                        hill_radius,
                                        moon_natural_moons,
                                        ring,
                                        moon_impact_moons,
                                        moon_impact_chance,
                                        moon_year,
                                        moon_day,
                                        moon_size_class,
                                        moon_wtype,
                                        moon_atmos_press,
                                        moon_hydro_pct,
                                        moon_atmos_comp,
                                        moon_temperature,
                                        moon_climate)



                        if impact_moons > 0:

                            
                            moon_key = str(ob_db_key) + '-i1' # Note 'i' for impact moon

                            moon_orbital_radius_roll = roll_dice(3,'impact moon_radius', moon_key, conn, c)
                            
                            moon_orbital_radius_km = ((moon_orbital_radius_roll + 7) * (4 * radius))
                            moon_orbital_radius = round(moon_orbital_radius_km / 149597870.700,3)  # convert to AU
                            zone_objects =  "Impact Moon"

                            mass_roll = roll_dice(3,'moon mass roll',moon_key, conn, c)


                            moon_mass = round(mass_roll * mass * .01,4)

                            
                            density_roll = roll_dice(3, 'moon density roll', moon_key, conn, c)
                            moon_density = round((integer_root(5,moon_mass)) + ((density_roll - 10)/100),2)
                            
                            if moon_density == 0:
                                moon_size = 0
                                print('Zero density moon!',moon_key)
                            else:
                                moon_size = round((6370 * (integer_root(3,(moon_mass/moon_density)))) * 2 / 1609.3,0)
                            
                            moon_gravity = round(integer_root(3,(moon_mass*(moon_density**2))),2)
                            
                            hill_radius = 'N/A'
                            moon_natural_moons = 0
                            moon_impact_moons = 0
                            moon_impact_chance = 0
                            
                            moon_year = get_year(mass,moon_orbital_radius)
                            moon_day = get_day(moon_size,moon_key)
                            
                            if moon_size == 0: moon_body = 'Planetoid Belt'
                            else: moon_body = 'Planet'
                            
                            moon_size_class = get_world_size_class(moon_mass,moon_size,moon_body)
                            moon_wtype = get_world_type(moon_size_class, zones)
                            moon_atmos_press = get_atmos_pressure(moon_size_class, moon_wtype,moon_key)
                            
                            moon_hydro_pct = get_hydro_pct( moon_size_class, 
                                                            moon_wtype,
                                                            moon_atmos_press,
                                                            zones,
                                                            star["spectral_type"],
                                                            current_distance,
                                                            star["snow_line"],
                                                            moon_key)
                                                            
                            moon_atmos_comp = get_atmos_comp(moon_wtype,moon_key)
                            moon_temperature = get_temperature(moon_wtype, 
                                                                moon_hydro_pct, 
                                                                moon_atmos_press,
                                                                moon_gravity,
                                                                star["luminosity"],
                                                                current_distance,
                                                                moon_key)
            
                            moon_climate = get_climate(moon_temperature, moon_wtype)
                            ring = 'None'
                            m = 1 # the only impact moon so it will go into the table as moon #1
                            
                            populate_orbital_body_table(
                                    moon_key,
                                    location,
                                    planet_no,
                                    m,
                                    current_distance,
                                    moon_orbital_radius,
                                    zones,
                                    zone_objects,
                                    moon_size,
                                    moon_density,
                                    moon_mass,
                                    moon_gravity,
                                    hill_radius,
                                    moon_natural_moons,
                                    ring,
                                    moon_impact_moons,
                                    moon_impact_chance,
                                    moon_year,
                                    moon_day,
                                    moon_size_class,
                                    moon_wtype,
                                    moon_atmos_press,
                                    moon_hydro_pct,
                                    moon_atmos_comp,
                                    moon_temperature,
                                    moon_climate)            
            
            
            

            else:
                no_gg = 0
                no_belts = 0                    

            star["orbits"] += orbit_adjust
            star["gg"] = no_gg
            star["belts"] = no_belts
            new_star_list.append(star)
                
        return new_star_list
    

    def populate_stellar_tables(stellar_list):
        
        for star in stellar_list:
            
            c.execute("INSERT INTO stellar_bodies (location, companion_class, luminosity_class,\
                  spectral_type, age, temperature, luminosity, mass, radius, inner_limit, \
                  life_zone_min, life_zone_max, snow_line, outer_limit, base_orbital_radius, \
                  bode_constant, orbits, belts, gg, s_orbit_description, s_orbital_average, \
                  s_orbital_ecc, min_orbit, max_orbit, inner_forbidden, outer_forbidden, companions) \
                  VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, \
                         ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",(
                  star["location"],
                  star["companion_class"],
                  star["luminosity_class"],
                  star["spectral_type"],
                  star["age"],
                  star["temperature"],
                  star["luminosity"],
                  star["mass"],
                  star["radius"],
                  star["inner_limit"],
                  star["lz_min"],
                  star["lz_max"],
                  star["snow_line"],
                  star["outer_limit"],
                  star["base_orbital_radius"],
                  star["bode_constant"],
                  star["orbits"],
                  star["belts"],
                  star["gg"],
                  star["orbit_description"],
                  star["orbital_average"],
                  star["orbital_ecc"],
                  star["min_orbit"],
                  star["max_orbit"],
                  star["inner_forbidden"],
                  star["outer_forbidden"],                  
                  star["companions"]))
                  

        
#------------------------------------------------------------------------------
# Main Program
#------------------------------------------------------------------------------



    seed_number = decisions_provided.random_seed
    random.seed(seed_number)
      
    SECTORS = 1   #Program set for building one sector at this time.  More than one sector will just erase the previous.
    LIKELIHOOD = decisions_provided.sector_density




    # Perhaps include these in the input menu one day - but for now set them as constants

    LUM_CLASS_CHANCE_III = 3
    LUM_CLASS_CHANCE_V = 14
    SPEC_CLASS_CHANCE_A = 4
    SPEC_CLASS_CHANCE_F = 6
    SPEC_CLASS_CHANCE_G = 8
    SPEC_CLASS_CHANCE_K = 10
    MULTIPLE_STAR_CHANCE_S = 13
    MULTIPLE_STAR_CHANCE_B = 17
    DISTANT_COMPANION_CHANCE = 11
    

    
    #------------------------------------------------------------------------------
    # Load the tables into global constants
    #------------------------------------------------------------------------------
    
    CHARSV = {}
    CHARSV = get_stellarcharsv()
    
    CHARSIII = {}
    CHARSIII = get_stellarcharsiii()
    
    COMP_SEP = {}
    COMP_SEP = get_companion_separation()
    
    WORLD_TYPE = {}
    WORLD_TYPE = get_world_type_table()
    
    
    #------------------------------------------------------------------------------
    # Prepare the SQLite DB
    #------------------------------------------------------------------------------
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    create_tables(c,conn)
    
    #   Loop for each sector
    for a in range(0,SECTORS):
    
    #   Loop for each parsec in a subsector
        for x in range (1,33):
            if x < 10:
                xstring = ("0" + str(x))
            else:
                xstring = (str(x))
            for y in range (1,41):
                if y < 10:
                    ystring = ("0" + str(y))
                else:           
                    ystring = (str(y))
                parsec = str(xstring + ystring)                
    #           Generate a random d6 to check for system presence against LIKELIHOOD
                rollgen = roll_dice(1, 'system presence',parsec, conn, c)
              
                #------------------------------------------------------------------------------
                # This section builds the system
                #------------------------------------------------------------------------------
    
                if rollgen >= LIKELIHOOD:  
                    stellar_dict_list = []
                    stellar_dict = {}
                    
                    primary_companions = get_multiple_stars(parsec)# companions of the primary
                    for pc in range(0,primary_companions+1):  # one loop for each non subcompanion star
                        if pc == 0: 
                            stellar_dict = populate_stellar_dict(parsec,pc,0,primary_companions,False)
                            stellar_dict_list.append(stellar_dict)
                        else: 
                            stellar_dict = populate_stellar_dict(parsec,pc,stellar_dict_list[0],primary_companions,False)
                            stellar_dict_list.append(stellar_dict)
                                                          
                            if stellar_dict['companions'] > 0:
                                stellar_dict = populate_stellar_dict(parsec,pc,stellar_dict,primary_companions,True)
                                stellar_dict_list.append(stellar_dict)
                    
                    stellar_dict_list = populate_stellar_orbit_info(parsec,stellar_dict_list)
                    stellar_dict_list = populate_planets(parsec, stellar_dict_list)
                    populate_stellar_tables(stellar_dict_list)


    #------------------------------------------------------------------------------
    # Count final stats
    #------------------------------------------------------------------------------

    sql_primary_count = '''SELECT COUNT(*) from stellar_bodies WHERE companion_class = 0'''
    sql_stellar_count = '''SELECT COUNT(*) from stellar_bodies '''
    sql_body_count = '''SELECT body, COUNT(body) as count from orbital_bodies GROUP BY body
                        UNION ALL
                        SELECT 'SUM' body, COUNT(body) from orbital_bodies'''

    c.execute(sql_primary_count)
    allrows = c.fetchall()
    print(str(allrows[0][0]),'stellar systems created.' )
    
    c.execute(sql_stellar_count)
    allrows = c.fetchall()
    print(str(allrows[0][0]),'total stars created.' )
    
    c.execute(sql_body_count)
    allrows = c.fetchall()

    for row_count, row in enumerate(allrows):
        if row_count <= 4:
            print(row[1],row[0]+'s created')
        else:
            print('Total orbital bodies created: ',row[1])

    
                 
    

   
    conn.commit()  
    c.close()
    conn.close()
    
    
    
       
    
    
    
  
    
        
