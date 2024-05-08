# -*- coding: utf-8 -*-
"""
Created on Sat May  4 13:39:38 2024

@author: sean

Export Sector Data into a PDF

v0.0.1
"""

import logging

# Set the logging level to DEBUG
logging.basicConfig(level=logging.DEBUG)

# Create a logger
logger = logging.getLogger(__name__)

# Log a debug message
logging.debug("Debug message")

# Check the output destination
print("Check output stream for debug messages")


from reportlab.platypus import SimpleDocTemplate,Table, TableStyle, Paragraph, PageBreak, KeepTogether, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle



import sqlite3
import pandas as pd

from traveller_functions import tohex, get_subsector_number_list



def get_db():
    # Select the db file to print
    return 'C:/Users/sean/Dropbox/RPG/Traveller/MTU/solo-6/solo-6.db'

def get_location(c):
    # Produce a list of locations to be included in the export
    
    logging.debug("Entering get_location")
    
    subsector = 'J'
    location_sql = '''SELECT location from system_stats'''
    c.execute(location_sql)
    sector_locations = c.fetchall()
    first_dimension_list = list(zip(*sector_locations))[0]
    
    
    subsector_locations = get_subsector_number_list(subsector)
    

    
    intersected_locations = list(set(first_dimension_list).intersection(subsector_locations))
    intersected_locations.sort()
    logging.debug(f"Selected locations: {intersected_locations}")
    
    
    
    return intersected_locations

def get_output_file_name():
    return 'sector_test.pdf'

def get_culture_stats(c, location):
    culture_sql = '''SELECT age, appearance,tendency, materialism, honesty, 
                            bravery, social_conflict, work_ethic, consumerism,
                            spiritual_outlook, status_quo_outlook, custom, interests,
                            common_skills 
                            FROM perceived_culture
                            WHERE location = ?'''
                            
    c.execute(culture_sql, (location,))
    return c.fetchall()
                            
    
    

def get_system_stats(c,location):
    # Collect the system table data
    # This data will go on the top of the page as it is system-wide
 #   logging.debug(f'get_system_stats local location: {location}')

    line_sql = '''SELECT ts.system_name, remarks, ix, ex, cx, n, bases, zone, pbg, w, allegiance, stars 
                     FROM system_stats ss
                     LEFT JOIN traveller_stats ts
                     ON ss.location = ts.location
                     WHERE ts.location = ? AND ts.main_world = 1'''

    c.execute(line_sql, (location,))
    system_stats = c.fetchall()
    return system_stats
    
def get_far_trader_stats(c, location):
    # Collect the far trader table data
    # This data will go on the top of the page as it is system-wide    
    far_trader_sql = '''SELECT wtn, gwp, exchange, needs, wants
                            FROM far_trader
                            WHERE location = ? '''

    c.execute(far_trader_sql, (location,)) 
    return c.fetchall()    

def get_detail_stats(c, loc_orb):
    orbital_detail_sql = '''
    SELECT 
    ob.id,
    ob.location,
    ob.stellar_orbit_no,
    ob.planetary_orbit_no,
    ob.stellar_distance,
    ob.orbital_radius,
    ob.zone,
    ob.body,
    ob.density,
    ob.mass,
    ob.gravity,
    ob.hill_radius,
    ob.natural_moons,
    ob.ring,
    ob.impact_moons,
    ob.impact_chance,
    ob.year,
    ob.day,
    ob.size_class,
    ob.wtype,
    ob.atmos_pressure,
    ob.atmos_composition,
    ob.temperature,
    ob.climate
    FROM orbital_bodies ob 
    WHERE ob.location_orbit = ?
    '''
    
    journey_detail_sql = '''SELECT planet_stellar_masked, jump_point_Mm,
                            hrs_1g, hrs_2g, hrs_3g, hrs_4g, hrs_5g, hrs_6g
                            FROM journey_data
                            WHERE location_orbit = ?
                            '''
    
    
    
    c.execute(orbital_detail_sql,(loc_orb,))
    orbital_detail_data =  c.fetchall()
    
    c.execute(journey_detail_sql,(loc_orb,))
    journey_detail_data =  c.fetchall()
  #  logging.debug(f' journey detail: {journey_detail_data}')
    
    return orbital_detail_data, journey_detail_data

def get_culture_stats_object(c, location):
    culture_detail_row = get_culture_stats(c, location)
    
    culture_object = Culture_details(
        culture_detail_row[0][0],
        culture_detail_row[0][1],
        culture_detail_row[0][2],
        culture_detail_row[0][3],
        culture_detail_row[0][4],
        culture_detail_row[0][5],
        culture_detail_row[0][6],
        culture_detail_row[0][7],
        culture_detail_row[0][8],
        culture_detail_row[0][9],
        culture_detail_row[0][10],
        culture_detail_row[0][11],
        culture_detail_row[0][12],
        culture_detail_row[0][13],
        )
    
    return culture_object

def get_detail_stats_object(c, loc_orb, uwp_dict):
    orbital_detail_row, journey_detail_row = get_detail_stats(c, loc_orb)
    
    detail_stats_object = Detail_stats(
    orbital_detail_row[0][0],      # db_id
    uwp_dict[loc_orb][0],  # name
    orbital_detail_row[0][1],      # location
    uwp_dict[loc_orb][1],  # uwp
    orbital_detail_row[0][2],
    orbital_detail_row[0][3],
    orbital_detail_row[0][4],
    orbital_detail_row[0][5],
    orbital_detail_row[0][6],
    orbital_detail_row[0][7],
    round(orbital_detail_row[0][8],2),      # density
    orbital_detail_row[0][9],
    orbital_detail_row[0][10],
    orbital_detail_row[0][11],
    orbital_detail_row[0][12],
    orbital_detail_row[0][13],
    orbital_detail_row[0][14],
    orbital_detail_row[0][15],
    orbital_detail_row[0][16],
    orbital_detail_row[0][17],
    orbital_detail_row[0][18],
    orbital_detail_row[0][19],
    orbital_detail_row[0][20],
    orbital_detail_row[0][21],
    orbital_detail_row[0][22],
    orbital_detail_row[0][23],  # climate
    journey_detail_row[0][0],   # planet masked
    journey_detail_row[0][1],   # jump distance
    journey_detail_row[0][2],   # 1G Hrs
    journey_detail_row[0][3],   # 2G Hrs
    journey_detail_row[0][4],   # 3G Hrs
    journey_detail_row[0][5],   # 4G Hrs
    journey_detail_row[0][6],   # 5G Hrs
    journey_detail_row[0][7])    # 6G Hrs
    detail_stats_object.jump_point_Mm = round(detail_stats_object.jump_point_Mm/1000,2)
    detail_stats_object.jump_point_Mm = "{:,}".format(detail_stats_object.jump_point_Mm)
 #   logging.debug(f' detail_stats: {journey_detail_row[0][0]}')
    
    return detail_stats_object

def get_system_object(c, location):
    logging.debug(f'get_system_object local location: {location}')
    system_row = get_system_stats(c, location)
#    logging.debug(system_row)
    system_object = System_details(
    system_row[0][0],
    system_row[0][1],
    system_row[0][2],
    system_row[0][3],
    system_row[0][4],
    system_row[0][5],
    system_row[0][6],
    system_row[0][7],
    system_row[0][8],
    system_row[0][9],
    system_row[0][10],
    system_row[0][11])
    return system_object 

def get_far_trader_object(c, location):
    trader_row = get_far_trader_stats(c, location)
    trader_object = Far_trader_details(
    trader_row[0][0],
    trader_row[0][1],
    trader_row[0][2],
    trader_row[0][3],
    trader_row[0][4])
    
    trader_object.gwp = "{:,}".format(trader_object.gwp)
    
    return trader_object

def fix_uwp(df):

    df['size'] = df['size'].apply(tohex)
    df['hydrographics'] = df['hydrographics'].apply(tohex)
    df['atmosphere'] = df['atmosphere'].apply(tohex)
    df['population'] = df['population'].apply(tohex)
    df['government'] = df['government'].apply(tohex)
    df['law'] = df['law'].apply(tohex)
    df['tech_level'] = df['tech_level'].apply(tohex)
    
    df['ring'] = df['ring'].str[0]
    df['atmos_composition'] = df['atmos_composition'].str[0:2]
    
    df['uwp'] = df['starport'] + df['size'] + df['hydrographics'] + df['atmosphere'] + \
        df['population'] + df['government'] + df['law'] + '-' + df['tech_level']
        
        
    df = df.drop(['starport','size','hydrographics','atmosphere','population','government','law','tech_level'], axis=1)    
    
    uwp = df.pop('uwp')
    
    df.insert(2, 'uwp', uwp)

    return df



def get_orbital_data(conn, location):
    # Body of the table (each orbital bodies)
    table_sql = '''SELECT ob.location_orbit, ts.system_name, ts.starport, ts.size, ts.hydrographics, ts.atmosphere,
                    ts.population, ts.government, ts.law, ts.tech_level,
                    gravity, ring, year, day, 
                    atmos_pressure, atmos_composition, temperature, hrs_1g, hrs_2g, hrs_3g, hrs_4g, hrs_5g, hrs_6g
                    FROM orbital_bodies ob
                    LEFT JOIN traveller_stats ts
                    ON ts.location_orb = ob.location_orbit
                    LEFT JOIN journey_data jd
                    ON ob.location_orbit = jd.location_orbit
                    WHERE ob.location = ?'''
                    
    df = pd.read_sql_query(table_sql,conn, params=(location,))

    df = fix_uwp(df)      


    return df


def get_styles():
    # Get styles for the Header, Lines, and WantsNeeds sections of the page
    
    
    # Get the default sample stylesheet
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        name='Header',
        parent=styles['Normal'],  # You can base your style on an existing style, like 'Normal'
        fontName="Courier",  # Specify the font name
        fontSize=14,  # Specify the font size
        textColor='black',  # Specify the text color
        spaceBefore=0,  # Add space before the paragraph
        spaceAfter=10  # Add space after the paragraph
    )



    travel_style = ParagraphStyle(
        name='LineText',  # Give it a unique name
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=7,
        textColor=colors.whitesmoke,
        spaceBefore=0,
        spaceAfter=0
    )


    wantsneeds_style = ParagraphStyle(
        name='WantsNeedsText',  # Give it a unique name
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=7,
        textColor=colors.black,
        spaceBefore=0,
        spaceAfter=0
    )
    
    detail_style = ParagraphStyle(
        name='DetailText',  # Give it a unique name
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=8,
        textColor=colors.black,
        spaceBefore=0,
        spaceAfter=0
    )
    
    detail_header_style = ParagraphStyle(
        name='DetailHeader',  # Give it a unique name
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=10,
        textColor=colors.whitesmoke,
        spaceBefore=5,
        spaceAfter=5
    )


    
    return header_style, travel_style, wantsneeds_style, detail_style, detail_header_style

def get_summary_table_data(df):
    data = [
    ['Loc-Orb','Name','UWP','Gr','Ri','Yr','Dy','Atm','Comp','Temp','1G','2G','3G','4G','5G','6G'],
    ]

    list_of_lists = df.values.tolist()

    data += list_of_lists
    
    return data



    
def get_summary_table_style():
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.gray),
        ('BACKGROUND', (0,1), (-1,-1), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Courier'),
        ('FONTNAME', (1,1), (-1,-1), 'Courier'),
        ('FONTSIZE', (0,0), (-1, 0), 7),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('GRID',(0,1),(-1,-1),.5,colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])  
    return style

def alternate_background(table, table_data):
    row_num = len(table_data)
    for i in range(1,row_num):
        if i % 2 == 0:
            bc = colors.white
        else:
            bc = colors.lightgrey
            
        ts = TableStyle(
            [('BACKGROUND', (0,i), (-1,i), bc)])
        table.setStyle(ts)

    
def get_summary_table(table_data):
    col_widths = [45,75,45,25,15,25,20,25,20,30,20,20,20,20,20,20]
    table = Table(table_data, colWidths=col_widths,rowHeights=15)
    return table

def update_summary_elems(text_before_table, summary_table, culture_lines):
    # Create a Spacer with a specified width and height
    spacer = Spacer(10, 10)

    # Add the Spacer to your elements list
    return  [
        PageBreak(),
        text_before_table.header_line,
        text_before_table.t5_line,
        text_before_table.detail_line,        
        text_before_table.gurps_line,
        text_before_table.wants_line,
        text_before_table.needs_line,
        summary_table,
        spacer,
        culture_lines.header_line,
        culture_lines.age_line,
        culture_lines.bravery_line,
        culture_lines.status_quo_line,
        culture_lines.skills_line,
        PageBreak()
    ]



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
                 common_skills):
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
        
    
class System_details:
    def __init__(self, 
                 name, 
                 remarks,
                 ix,
                 ex,
                 cx,
                 nobles,
                 bases,
                 zone,
                 pbg,
                 w,
                 allegiance,
                 stars):
        self.name = name
        self.remarks = remarks
        self.ix = ix
        self.ex = ex
        self.cx = cx
        self.nobles = nobles
        self.bases = bases
        self.zone = zone
        self.pbg = pbg
        self.w = w
        self.allegiance = allegiance
        self.stars = stars
        
class Far_trader_details:
    def __init__(self,
                 wtn,
                 gwp,
                 exchange,
                 needs,
                 wants):
        self.wtn = wtn
        self.gwp = gwp
        self.exchange = exchange
        self.needs = needs
        self.wants = wants        

class Text_before_table:
    def __init__(self,
                 header_line,
                 t5_line,
                 detail_line,
                 gurps_line,
                 wants_line,
                 needs_line):
        self.header_line = header_line
        self.t5_line = t5_line
        self.detail_line = detail_line
        self.gurps_line = gurps_line
        self.wants_line = wants_line
        self.needs_line = needs_line
        
class Culture_lines:
    def __init__(self,
                 header_line,
                 age_line,
                 bravery_line,
                 status_quo_line,
                 skills_line):
        self.header_line = header_line
        self.age_line = age_line
        self.bravery_line = bravery_line
        self.status_quo_line = status_quo_line
        self.skills_line = skills_line
        
  
class Detail_stats:
    def __init__(self,
                 db_id,
                 name,
                 location,
                 uwp,
                 stellar_orbit_no,
                 planetary_orbit_no,
                 stellar_distance,
                 orbital_radius,
                 zone,
                 body,
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
                 atmos_composition,
                 temperature,
                 climate,
                 planet_stellar_masked,
                 jump_point_Mm,
                 hrs_1g,
                 hrs_2g,
                 hrs_3g,
                 hrs_4g,
                 hrs_5g,
                 hrs_6g
                 ):
        
        self.db_id = db_id
        self.name = name
        self.location = location
        self.uwp = uwp
        self.stellar_orbit_no = stellar_orbit_no
        self.planetary_orbit_no = planetary_orbit_no
        self.stellar_distance = stellar_distance
        self.orbital_radius = orbital_radius
        self.zone = zone
        self.body = body
        self.density = density
        self.mass = mass
        self.gravity = gravity
        self.hill_radius = hill_radius
        self.natural_moons = natural_moons
        self.ring = ring
        self.impact_moons = impact_moons
        self.impact_chance = impact_chance
        self.year = year
        self.day = day
        self.size_class = size_class
        self.wtype = wtype,
        self.atmos_pressure = atmos_pressure
        self.atmos_composition = atmos_composition
        self.temperature = temperature
        self.climate = climate
        self.planet_stellar_masked = planet_stellar_masked 
        self.jump_point_Mm =jump_point_Mm
        self.hrs_1g = hrs_1g
        self.hrs_2g = hrs_2g
        self.hrs_3g = hrs_3g
        self.hrs_4g = hrs_4g
        self.hrs_5g = hrs_5g
        self.hrs_6g = hrs_6g
        
    
    
##### Beginning of Program


# Set parameters and file names
db_name = get_db()
output_file_name = get_output_file_name()
elems = []


# Connect to DB
conn = sqlite3.connect(db_name)
c = conn.cursor()

# Get locations
location_list = get_location(c)

pdf = SimpleDocTemplate(
    output_file_name,
    page_size = letter)


for location in location_list:

    # Header, Lines, WantsNeeds Activities
    
 #   logging.debug(f'System: {location}')
    
 #   logging.debug(f'main program for statement: {location} {type(location)}')
    
    system_details = get_system_object(c, location)
    trader_details = get_far_trader_object(c, location)
    header_style, travel_style, wantsneeds_style, detail_style, detail_header_style = get_styles()
    
    text_1 = Paragraph(f"(<b>{location}) {system_details.name}</b>", header_style)
    text_2 = Paragraph(f"{system_details.remarks}   {system_details.ix}   {system_details.ex}  \
                                    {system_details.cx}", wantsneeds_style)
    text_3 = Paragraph(f"<b>Bases:</b> {system_details.bases}  <b>Travel Zone</b>: {system_details.zone}   \
                         <b>PBG:</b>{system_details.pbg}   <b>Stellar:</b> {system_details.stars}", wantsneeds_style)
    text_4 = Paragraph(f"<b>WTN:</b> {trader_details.wtn}  <b>GWP:</b> {trader_details.gwp}CR ",wantsneeds_style)
    text_5 = Paragraph(f"<b>Surplus:</b> {trader_details.wants}", wantsneeds_style)
    text_6 = Paragraph(f"<b>Needs:</b> {trader_details.needs} ", wantsneeds_style)

    text_before_table = Text_before_table(text_1,text_2,text_3,text_4,text_5,text_6)
    
   
    # Orbital Data Table Activities 
    df = get_orbital_data(conn, location)
    summary_table_data = get_summary_table_data(df)
    summary_table = get_summary_table(summary_table_data)
    summary_table_style = get_summary_table_style()
    summary_table.setStyle(summary_table_style)
    alternate_background(summary_table, summary_table_data)
    
    culture_details = get_culture_stats_object(c, location)
 #   logging.debug(f"culture_details: {culture_details}")
    
    

        
    culture_header_line = Paragraph("Cultural Perceptions",detail_style)
    culture_age_line = Paragraph(f"{culture_details.age.capitalize()}.  \
                                 {culture_details.appearance.capitalize()} appearance.  \
                                 {culture_details.tendency.capitalize()} tendency.  \
                                 {culture_details.materialism.capitalize()} materialism.  \
                                 {culture_details.honesty.capitalize()} honesty.",wantsneeds_style)
                                 
    culture_bravery_line = Paragraph(f"{culture_details.bravery.capitalize()} bravery.  \
                                 {culture_details.social_conflict.capitalize()} social conflict.  \
                                 {culture_details.work_ethic.capitalize()} work ethic.  \
                                 {culture_details.consumerism.capitalize()} consumerism.",wantsneeds_style)                                
                                 
    culture_status_quo_line = Paragraph(f"{culture_details.spiritual_outlook.capitalize()} spiritual outlook. \
                                 {culture_details.status_quo_outlook.capitalize()} status_quo_outlook.  \
                                 {culture_details.custom.capitalize()}.  \
                                 Interested in {culture_details.interest}.",wantsneeds_style)                              
                                
    culture_skills_line = Paragraph(f"<b>Common skills:</b> {culture_details.common_skills}",wantsneeds_style)  
                                  
                             
    culture_lines = Culture_lines(culture_header_line,
                                    culture_age_line,
                                    culture_bravery_line,
                                    culture_status_quo_line,
                                    culture_skills_line)
    
    elems += update_summary_elems(text_before_table, summary_table, culture_lines)
    

    # Begin work on individual orbital bodies details

    # Grab the pre-loaded UWPs into a UWP dictionary with location_orbit as key
    loc_orbit_list = df['location_orbit'].to_list()
    name_list = df['system_name'].to_list()
    uwp_list = df['uwp'].to_list()

    uwp_dict = {loc_orbit_list: [name_list, uwp_list] for loc_orbit_list, name_list, uwp_list in zip(loc_orbit_list, name_list, uwp_list)}
    detail_list = df['location_orbit'].tolist()


    for d in detail_list:
        
 #       logging.debug(f'entering details for {d}')
           
        detail_stats = get_detail_stats_object(c,d,uwp_dict)
        
 #       logging.debug(f'object received for {d}')
        
        travel_hours_string = f'''{detail_stats.hrs_1g}-
                                {detail_stats.hrs_2g}-
                                {detail_stats.hrs_3g}-
                                {detail_stats.hrs_4g}-
                                {detail_stats.hrs_5g}-
                                {detail_stats.hrs_6g}'''
                                
        
        detail_headers = [
            Paragraph(f"<b>({d})</b>", detail_header_style),
            Paragraph(f"<b>{detail_stats.name}</b>", detail_header_style),
            Paragraph(f"<b>{detail_stats.location}</b>", detail_header_style),  
            Paragraph(f"<b>{detail_stats.uwp}</b>", detail_header_style),
            None,
            Paragraph(f"<b>{travel_hours_string}</b>", travel_style), 
        ]
        
        
        
        detail_body = [
            [
                Paragraph("<b>Stellar Orbit Number:</b>", detail_style),
                Paragraph(str(detail_stats.stellar_orbit_no), detail_style),
                Paragraph("<b>Planetary Orbit Number:</b>", detail_style),
                Paragraph(str(detail_stats.planetary_orbit_no), detail_style),
                Paragraph("<b>Year:</b>", detail_style),
                Paragraph(f"{detail_stats.year} earth years", detail_style),

            ],
            [
                Paragraph("<b>Day:</b>", detail_style),
                Paragraph(f"{detail_stats.day} hours", detail_style),
                Paragraph("<b>Distance to star:</b>", detail_style),
                Paragraph(f"{detail_stats.stellar_distance} AUs",detail_style),
                Paragraph("<b>Orbital Radius:</b>", detail_style),
                Paragraph(f"{detail_stats.orbital_radius} AUs", detail_style),
            ],
            [
                Paragraph("<b>Orbital Zone:</b>", detail_style),
                Paragraph(str(detail_stats.zone), detail_style),
                Paragraph("<b>Body Type:</b>", detail_style),
                Paragraph(str(detail_stats.body), detail_style),
                Paragraph("<b>Density:</b>", detail_style),
                Paragraph(f"{detail_stats.density} g/cc", detail_style),
            ],
            [
                Paragraph("<b>Mass:</b>", detail_style),
                Paragraph(f"{detail_stats.mass}", detail_style),
                Paragraph("<b>Gravity:</b>", detail_style),
                Paragraph(f"{detail_stats.gravity}G", detail_style),
                Paragraph("<b>Hill Radius:</b>", detail_style),
                Paragraph(str(detail_stats.hill_radius), detail_style),
            ],
            [
                Paragraph("<b>Natural Moons:</b>", detail_style),
                Paragraph(f"{detail_stats.natural_moons}", detail_style),
                Paragraph("<b>Impact Moons:</b>", detail_style),
                Paragraph(f"{detail_stats.impact_moons}", detail_style),
                Paragraph("<b>Impact Chance:</b>", detail_style),
                Paragraph(str(detail_stats.impact_chance), detail_style),
            ],
            [
                Paragraph("<b>Ring:</b>", detail_style),
                Paragraph(f"{detail_stats.ring}", detail_style),
                Paragraph("<b>Size Class:</b>", detail_style),
                Paragraph(f"{detail_stats.size_class}", detail_style),
                Paragraph("<b>World Type:</b>", detail_style),
                Paragraph(str(detail_stats.wtype[0]), detail_style),
            ],
            [
                Paragraph("<b>Mean Temperature:</b>", detail_style),
                Paragraph(f"{detail_stats.temperature}K", detail_style),
                Paragraph("<b>Climate:</b>", detail_style),
                Paragraph(f"{detail_stats.climate}", detail_style),
                Paragraph("<b>Stellar Jump Mask:</b>", detail_style),
                Paragraph(f"{detail_stats.planet_stellar_masked}", detail_style),
            ],
            [
                Paragraph("<b>Atmospheric Pressure:</b>", detail_style),
                Paragraph(f"{detail_stats.atmos_pressure}atm", detail_style),
                Paragraph("<b>Atmospheric Composition:</b>", detail_style),
                Paragraph(f"{detail_stats.atmos_composition}", detail_style),
                Paragraph("<b>Distance to jump:</b>", detail_style),
                Paragraph(f"{detail_stats.jump_point_Mm}Mkm", detail_style),
            ],
            
        ]
        


        
 #       logging.debug(f'detail completed for {d}')
                      
        # Define the style for the table
        detail_table_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.gray),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align all cells to the left
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align all cells to the middle vertically
            ('LINEBELOW', (0, 0), (-1, 0), 1, 'gray'),  # Add a line below the first row
            ('LINEABOVE', (0, 1), (-1, -1), 1, 'gray'),  # Add a line above each row starting from the second row
            ('FONTNAME', (0, 0), (-1, -1), 'Courier'), 
  
        ])
        
        # Create the table
        detail_table = Table([detail_headers] + detail_body)

        
        # Apply the table style
        detail_table.setStyle(detail_table_style)              
        detail_table = KeepTogether([detail_table])
        elems.append(detail_table)
        elems.append(Spacer(1, 30)) 
    
    
                   
    

pdf.build(elems)


conn.commit()  
c.close()
conn.close() 