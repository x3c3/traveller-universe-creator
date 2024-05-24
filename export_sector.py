def export_ss_to_pdf(db,ss):


    # -*- coding: utf-8 -*-
    """
    Created on Sat May  4 13:39:38 2024
    
    @author: sean
    
    Export Sector Data into a PDF
    
    v 1.1.0b  2024-05-24  Added error variables to debug log in try/excepts   
    v 1.1.0c  2024-05-24  Added style class to hold all styles
    v 1.1.0d  2024-05-24  Cleaned up code
    """
    
    
### IMPORTS

    
    import logging
    import sqlite3
    import pandas as pd
    import os
    
    # Set the logging level to DEBUG
    logging.basicConfig(level=logging.DEBUG)
    
    
    # Log a debug message
    logging.debug("Debug message")
    

    
    
    from reportlab.platypus import SimpleDocTemplate,Table, TableStyle, Paragraph, PageBreak, KeepTogether, Spacer, Image
    
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    from reportlab.lib.units import inch
    
    from reportlab.lib.enums import TA_CENTER
    from reportlab.pdfgen import canvas

    
    from traveller_functions import tohex, get_subsector_number_list
    from traveller_functions import Culture_details, get_remarks_list
    from traveller_functions import Api_image_parameters, download_image_via_api
    
    from PyPDF2 import PdfMerger
    
    
### CLASSES    

    class Program_details:
        def __init__(self, db, ss):
            self.db_name  = self._get_db(db)
            self.sector   = self._get_sector(db)
            self.subsector = self._get_subsector(ss)
            self.output_file_name = self._get_output_file_name(db,ss)
            self.image_path = self._get_image_path()
            self.elems = []
        
        
        
        def _get_db(self, db):
            return db
        
        def _get_sector(self, db):
            return os.path.basename(self.db_name)[0:-3].capitalize()
        
        def _get_subsector(self, ss):
            # Select the subsector letter
            return ss
        
        def _get_output_file_name(self, db,ss):
            return 'sector_db/subector_'+ ss + '.pdf'
            
            
        def _get_image_path(self):
            return 'covers/' + self.subsector + '.jpg'
    

    class Db_details:
        def __init__(self, conn, cursor):
            self.conn = None
            self.cursor = None
        
    
    class System_details:
        def __init__(self,
                     location,
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
            self.location = location
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
                     header_line = None,
                     t5_line = None,
                     detail_line = None,
                     gurps_line = None,
                     wants_line = None,
                     needs_line = None):
            self.header_line = header_line
            self.t5_line = t5_line
            self.detail_line = detail_line
            self.gurps_line = gurps_line
            self.wants_line = wants_line
            self.needs_line = needs_line
            
            
        def populate_system_text_before_table(self, system_details, ex_styles):
            self.header_line = Paragraph(f"(<b>{system_details.location}) {system_details.name}</b>", ex_styles.header_style)
            self.t5_line = Paragraph(f"{system_details.remarks}   {system_details.ix}   {system_details.ex}  \
                                     {system_details.cx}",  ex_styles.wantsneeds_style)
            
            self.detail_line = Paragraph(f"<b>Bases:</b> {system_details.bases}  \
                                         <b>Travel Zone</b>: {system_details.zone}   \
                                         <b>PBG:</b> {system_details.pbg}   \
                                         <b>Stellar:</b> {system_details.stars}",  ex_styles.wantsneeds_style)
            
 
        def populate_trader_text_before_table(self, trader_details, ex_styles):
             
            self.gurps_line = Paragraph(f"<b>WTN:</b> {trader_details.wtn}  \
                                           <b>GWP:</b> CR {trader_details.gwp} \
                                           <b>Exchange:</b> {trader_details.exchange}",ex_styles.wantsneeds_style)
             
            self.wants_line = Paragraph(f"<b>Surplus:</b> {trader_details.wants}",  ex_styles.wantsneeds_style)
             
            self.needs_line = Paragraph(f"<b>Needs:</b> {trader_details.needs} ",  ex_styles.wantsneeds_style)    
            
           
    class Culture_lines:
        def __init__(self,
                     header_line = None,
                     age_line = None,
                     status_quo_line = None,
                     symbol_line = None,
                     skills_line = None):
            self.header_line = header_line
            self.age_line = age_line
            self.status_quo_line = status_quo_line
            self.symbol_line = symbol_line
            self.skills_line = skills_line
            
            
        def populate_culture_lines(self, culture_details, ex_styles):    
            
            self.header_line = Paragraph("Cultural Perception",ex_styles.detail_style)
        
            self.age_line = Paragraph(f"{culture_details.age.capitalize()}.  \
                                       {culture_details.appearance.capitalize()} appearance. \
                                       {culture_details.tendency.capitalize()} tendency.", ex_styles.wantsneeds_style)
                               
            self.status_quo_line = Paragraph(f"<b>Spr: </b>{culture_details.spiritual_outlook.capitalize()}. \
                                              <b>StQ: </b>{culture_details.status_quo_outlook.capitalize()}. \
                                              <b>Cus: </b>{culture_details.custom.capitalize()}.  \
                                              <b>Int: </b>{culture_details.interest.capitalize()}.", ex_styles.wantsneeds_style)            
                                              
            self.symbol_line = Paragraph(f"Mat{culture_details.materialism_symbol}  \
                                          Hon{culture_details.honesty_symbol} \
                                          Brv{culture_details.bravery_symbol}  \
                                          SC{culture_details.social_conflict_symbol}  \
                                          WE{culture_details.work_ethic_symbol}  \
                                          Con{culture_details.consumerism_symbol}", ex_styles.wantsneeds_style)
                                          
                           
            self.skills_line = Paragraph(f"<b>Common skills:</b> {culture_details.common_skills}", ex_styles.wantsneeds_style)  
        
                  
            
            
      
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
                     moons,
                     ring,
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
            self.mass = mass = round(mass,4)
            self.gravity = round(gravity,4)
            self.hill_radius = hill_radius
            self.moons = moons
            self.ring = ring
            self.impact_chance = impact_chance
            self.year = year
            self.day = day
            self.size_class = size_class
            self.wtype = wtype,
            self.atmos_pressure = round(atmos_pressure,2)
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
            
    class Export_page_styles():
        def __init__(self,
                     header_style = None,
                     travel_style = None,
                     wants_needs_style = None,
                     detail_style = None,
                     detail_header_style = None,
                     detail_table_style = None,
                     image_table_style = None,
                     summary_table_style = None,
                     index_header_style = None,
                     index_table_style = None,
                     index_entry_style = None
                     ):
            self.header_style = header_style
            self.travel_style = travel_style
            self.wants_needs_style = wants_needs_style
            self.details_style = detail_style
            self.detail_header_style = detail_header_style
            self.detail_table_style = detail_table_style
            self.image_table_style = image_table_style
            self.summary_table_style = summary_table_style
            self.index_header_style = index_header_style
            self.index_table_style = index_table_style
            self.index_entry_style = index_entry_style
            
        def populate_styles(self):
            styles = getSampleStyleSheet()
        
            self.header_style = ParagraphStyle(
                name='Header',
                parent=styles['Normal'], 
                fontName="Courier",  # Specify the font name
                fontSize=14,  # Specify the font size
                textColor='black',  # Specify the text color
                spaceBefore=0,  # Add space before the paragraph
                spaceAfter=10  # Add space after the paragraph
            )
        
        
        
            self.travel_style = ParagraphStyle(
                name='LineText',  # Give it a unique name
                parent=styles["BodyText"],
                fontName="Courier",
                fontSize=7,
                textColor=colors.whitesmoke,
                spaceBefore=0,
                spaceAfter=0
            )
        
        
            self.wantsneeds_style = ParagraphStyle(
                name='WantsNeedsText',  # Give it a unique name
                parent=styles["BodyText"],
                fontName="Courier",
                fontSize=7,
                textColor=colors.black,
                spaceBefore=0,
                spaceAfter=0
            )
            
            self.detail_style = ParagraphStyle(
                name='DetailText',  # Give it a unique name
                parent=styles["BodyText"],
                fontName="Courier",
                fontSize=9,
                textColor=colors.black,
                spaceBefore=0,
                spaceAfter=0
            )
            
            self.detail_header_style = ParagraphStyle(
                name='DetailHeader',  # Give it a unique name
                parent=styles["Normal"],
                fontName="Courier",
                fontSize=10,
                textColor=colors.whitesmoke,
                spaceBefore=5,
                spaceAfter=5
            )
            
            self.detail_table_style = TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.gray),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 
                    ('LINEBELOW', (0, 0), (-1, 0), 1, 'gray'), 
                    ('LINEABOVE', (0, 1), (-1, -1), 1, 'gray'), 
                    ('FONTNAME', (0, 0), (-1, -1), 'Courier'), 
          
                ])
            
            self.image_table_style = TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('BACKGROUND', (0,0), (-1,0), colors.gray),
                    ])
                   
            
            
            self.summary_table_style = TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.gray),
                    ('BACKGROUND', (0,1), (-1,-1), colors.lightgrey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    
                    
                    ('FONTNAME', (0,0), (-1,-1), 'Courier'),
                    ('FONTNAME', (0,1), (1, -1), 'Helvetica'),
                    
                    ('FONTSIZE', (3,1), (-1, -1), 7), 
                    ('FONTSIZE', (0,1), (2, -1), 7),
                   
    
                    ('GRID',(0,1),(-1,-1),.5,colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
            
            self.index_header_style = ParagraphStyle(name='IndexHeader', fontSize=12, alignment=TA_CENTER)
                   
            self.index_table_style = TableStyle([
                    ('FONTNAME', (0,0), (-1,-1), 'Courier'),
                    ('FONTSIZE', (0,0), (-1, -1), 7), 
                    ])
            
            self.index_entry_style = ParagraphStyle(name='IndexEntry', fontSize=7)
                   




        
### FUNCTIONS

    def get_location(c, subsector):
        # Produce a list of locations to be included in the export
        
        logging.debug("Entering get_location")
        
        location_sql = '''SELECT location from system_stats'''
        c.execute(location_sql)
        sector_locations = c.fetchall()
        first_dimension_list = list(zip(*sector_locations))[0]
        
        subsector_locations = get_subsector_number_list(subsector)
        
        intersected_locations = list(set(first_dimension_list).intersection(subsector_locations))
        intersected_locations.sort()
        logging.debug(f"Selected locations: {intersected_locations}")
        
        return intersected_locations
    
    def get_index_names(c, location_list):
        # Construct the SQL query with parameterized query placeholders
        placeholders = ','.join(['?' for _ in location_list])  # Ensure locations are strings
        name_sql = f"SELECT system_name, location_orb FROM traveller_stats WHERE location IN ({placeholders})"
        
        # Print list length for verification (optional)
        print(f"Number of locations in list: {len(location_list)}")
        
        # c.rowfactory = sqlite3.Row  # This line should be removed
    
        
        # Execute the SQL query with the list of locations as parameters
        c.execute(name_sql, location_list)
        index_name_list = c.fetchall()
        sorted_list = sorted(index_name_list , key=lambda x: x[0])
        return sorted_list     

    
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
    
    
    def build_cover_page(program_details):
        
     # Create a canvas
     cover = canvas.Canvas("sector_db/cover.pdf", pagesize=letter)
     
     # Define page size
     page_width, page_height = letter
     
     # Define image size
     image_width, image_height = 439, 685
     
     # Calculate x coordinate to center the image horizontally
     x = (page_width - image_width) / 2
     
     # Calculate y coordinate to center the image vertically
     y = (page_height - image_height) / 2
     
     # Draw the image
     cover.drawImage(program_details.image_path, x, y, width=image_width, height=image_height)
  
     
     # Set the fill color to white
     cover.setFillColor(colors.white)
  
     # Add text on top of the image
  
     cover.setFont("Helvetica-Bold", 20)    
     text_sector = f"{program_details.sector}"
  
      
     cover.setFont("Helvetica", 18) 
     text_subsector = f"Subsector {program_details.subsector}"

     cover.drawString(100, 675, text_sector)  # Adjust x, y coordinates as needed
     cover.drawString(100, 655, text_subsector)  # Adjust x, y coordinates as needed
  
     # Add the canvas object to the list of elements
     
     cover.save()   
    
    def build_sector_map(program_details):
        try:
            logging.debug('Traveller Sector Map')

            
            tab = program_details.db_name + '_tab.txt'  
            routes = program_details.db_name + '_routes.txt'  
            url = "https://travellermap.com/api/poster?style=print"
            files = {
            'file': tab,
            'metadata': routes
            }
            png_name = program_details.db_name + '_sector_map.png'
              
            
            api_parm_object = Api_image_parameters(url, files, png_name)

            download_image_via_api(api_parm_object)
            
            logging.debug("Traveller Map File Saved")   
           
              
        except Exception as e:
            logging.debug(f'Unexpected error in Traveller Map API {e}')
        
        
       
        
        # Create a canvas
        sec_map = canvas.Canvas("sector_db/sec_map.pdf", pagesize=letter)
        
        # Define page size
        page_width, page_height = letter
        
        # Define image size
        image_width, image_height = 470, 679
        
        # Calculate x coordinate to center the image horizontally
        x = (page_width - image_width) / 2
        
        # Calculate y coordinate to center the image vertically
        y = (page_height - image_height) / 2
        
        # Draw the image
        sec_map.drawImage(png_name, x, y, width=image_width, height=image_height)
     
        
        # Set the fill color to white
        sec_map.setFillColor(colors.black)
     
        # Add text on top of the image
     
        sec_map.setFont("Helvetica-Bold", 20)    
        text_sector = f"{program_details.sector}"
     

        sec_map.drawString(90, 750, text_sector)  # Adjust x, y coordinates as needed

     
        # Add the canvas object to the list of elements
        
        sec_map.save()
        



    def build_system_images(system_details, trader_details):
        
        system_images = []
        
        importance = system_details.ix
        for i in ['{','}']: importance = importance.strip(i)
        importance = int(importance)
        if importance >= 4: 
            system_image_path = "images/important.png"
            system_image = Image(system_image_path)
            system_image.drawWidth = 25
            system_image.drawHeight = 25
            system_images.append(system_image)
        
        bases = system_details.bases
        if 'N' in bases or 'B' in bases:
            system_image_path = "images/naval.png"
            system_image = Image(system_image_path)
            system_image.drawWidth = 25
            system_image.drawHeight = 25
            system_images.append(system_image)
            
        if 'S' in bases or 'B' in bases:
            system_image_path = "images/scout.png"
            system_image = Image(system_image_path)
            system_image.drawWidth = 25
            system_image.drawHeight = 25
            system_images.append(system_image)
    
        int_gwp =  trader_details.gwp.replace(",", "")       
        if int(int_gwp) >= 1000000:
            system_image_path = "images/wealthy.png"
            system_image = Image(system_image_path)
            system_image.drawWidth = 25
            system_image.drawHeight = 25
            system_images.append(system_image)
            
        if system_details.pbg[2] != '0':
            system_image_path = "images/gas giant.PNG"
            system_image = Image(system_image_path)
            system_image.drawWidth = 25
            system_image.drawHeight = 25
            system_images.append(system_image)
            
        return system_images
    
    def add_remarks_images(system_images,system_details):
        remarks_list = get_remarks_list()
    
        logging.debug(f'Actual remarks: {system_details.remarks}')
        for rem in remarks_list:
            if system_details.remarks.count(rem[0]) >= 1: 
                logging.debug(f'Remark found: {rem[0]}, {rem[1]}')
                system_image_path = 'images/' + rem[1] + '.png'
                system_image = Image(system_image_path)
                system_image.drawWidth = 25
                system_image.drawHeight = 25
                system_images.append(system_image)
                logging.debug(f'Remark found in {system_details.location}: {system_image_path}')
        return system_images
        
    
    def add_images_to_elems(system_images, elems, ex_styles):
        
        if len(system_images) > 0:
    
            
            # Create a table with a single row and add the images to it
            system_image_table = Table([system_images])
            
            system_image_table.setStyle(ex_styles.image_table_style)
               
    
            elems.append(system_image_table)
        
        else:
            logging.debug('No images for system')
            
        return elems    

        
    def build_travel_hours_string(detail_stats):
        return  f'''{detail_stats.hrs_1g}-
                    {detail_stats.hrs_2g}-
                    {detail_stats.hrs_3g}-
                    {detail_stats.hrs_4g}-
                    {detail_stats.hrs_5g}-
                    {detail_stats.hrs_6g}'''
                                           
        
    
    def build_detail_body(detail_stats, detail_style):
            detail_body = [
                [

                    Paragraph("<b>Body Type:</b>", detail_style),
                    Paragraph(str(detail_stats.body), detail_style),
                    Paragraph("<b>Size Class:</b>", detail_style),
                    Paragraph(f"{detail_stats.size_class}", detail_style),
                    Paragraph("<b>World Type:</b>", detail_style),
                    Paragraph(str(detail_stats.wtype[0]), detail_style),

                ],

                [
                    Paragraph("<b>Day:</b>", detail_style),
                    Paragraph(f"{detail_stats.day} hours", detail_style),
                    Paragraph("<b>Year:</b>", detail_style),
                    Paragraph(f"{detail_stats.year} earth years", detail_style),
                    Paragraph("<b>Distance to star:</b>", detail_style),
                    Paragraph(f"{detail_stats.stellar_distance} AUs",detail_style),

                ],
                [
                    Paragraph("<b>Moons:</b>", detail_style),
                    Paragraph(f"{detail_stats.moons}", detail_style),
                    Paragraph("<b>Ring:</b>", detail_style),
                    Paragraph(f"{detail_stats.ring}", detail_style),
                    Paragraph("<b>Orbital Zone:</b>", detail_style),
                    Paragraph(str(detail_stats.zone), detail_style),

                ],
                [
                    Paragraph("<b>Mass:</b>", detail_style),
                    Paragraph(f"{detail_stats.mass}", detail_style),
                    Paragraph("<b>Density:</b>", detail_style),
                    Paragraph(f"{detail_stats.density} g/cc", detail_style),
                    Paragraph("<b>Gravity:</b>", detail_style),
                    Paragraph(f"{detail_stats.gravity}G", detail_style),

                ],

                [
                    Paragraph("<b>Mean Temperature:</b>", detail_style),
                    Paragraph(f"{detail_stats.temperature}K", detail_style),
                    Paragraph("<b>Climate:</b>", detail_style),
                    Paragraph(f"{detail_stats.climate}", detail_style),
                    Paragraph("<b>Atmospheric Composition:</b>", detail_style),
                    Paragraph(f"{detail_stats.atmos_composition}", detail_style),

                ],
                [
                    Paragraph("<b>Atmospheric Pressure:</b>", detail_style),
                    Paragraph(f"{detail_stats.atmos_pressure}atm", detail_style),
                    Paragraph("<b>Stellar Jump Mask:</b>", detail_style),
                    Paragraph(f"{detail_stats.planet_stellar_masked}", detail_style),
                    Paragraph("<b>Distance to jump:</b>", detail_style),
                    Paragraph(f"{detail_stats.jump_point_Mm}Mkm", detail_style),
                ]
                
            ]
            return detail_body
        
        
    def build_detail_headers(d, detail_stats,travel_hours_string, ex_styles):
        return      [
                        Paragraph(f"<b>({d})</b>", ex_styles.detail_header_style),
                        Paragraph(f"<b>{detail_stats.name}</b>", ex_styles.detail_header_style),
                        Paragraph(f"<b>{detail_stats.location}</b>", ex_styles.detail_header_style),  
                        Paragraph(f"<b>{detail_stats.uwp}</b>", ex_styles.detail_header_style),
                        None,
                        Paragraph(f"<b>{travel_hours_string}</b>", ex_styles.travel_style), 
                    ]
                    
        
    def build_images(detail_stats):
        images = []
        if detail_stats.planet_stellar_masked != 'none':
            image_path = "images/mask.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)
        
        if detail_stats.body == 'Gas Giant':
            image_path = "images/gas giant.PNG"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)
        elif detail_stats.body == 'Impact Moon' or detail_stats.body == 'Natural Moon':
            image_path = "images/moon.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)

        elif detail_stats.uwp[1] == '0':
            image_path = "images/asteroid.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)


        if detail_stats.wtype[0] == 'Ocean*':
            logging.debug(f'Found an Ocean world {detail_stats.location}: {detail_stats.name} ')
            image_path = "images/ocean.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)
            
        if detail_stats.atmos_composition == 'Exotic':
            image_path = "images/exotic.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)
        elif detail_stats.atmos_composition == 'Corrosive':
            image_path = "images/corrosive.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)
        elif detail_stats.uwp[2] == '0':
            image_path = "images/vacuum.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)
            
        if  detail_stats.gravity > 1.50:
            image_path = "images/heavy.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)
        elif  detail_stats.gravity < .50:
            image_path = "images/light.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)
            
        if detail_stats.temperature > 324:
            image_path = "images/hot.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)
        elif detail_stats.temperature < 239:
            image_path = "images/cold.png"
            image = Image(image_path)
            image.drawWidth = 25
            image.drawHeight = 25
            images.append(image)            


        return images


    def append_detail_entry(d, detail_stats, ex_styles, program_details):
        
        travel_hours_string = build_travel_hours_string(detail_stats)
        
        detail_headers = build_detail_headers(d, detail_stats, travel_hours_string, ex_styles)
        
        images = build_images(detail_stats)
    
        image_table = Table([images])
        
        image_table.setStyle(ex_styles.image_table_style)
    
        detail_body = build_detail_body(detail_stats, ex_styles.detail_style)
    
        detail_table = Table([detail_headers] + detail_body)
    
        detail_table.setStyle(ex_styles.detail_table_style)              
    
        detail_table = KeepTogether([image_table,detail_table])
    
        program_details.elems.append(detail_table)
    
        program_details.elems.append(Spacer(1, 30)) 
    
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
            culture_detail_row[0][13]
            )
        
        culture_object_with_symbols = Culture_details.convert_culture_to_symbol(culture_object)
        
       # logging.debug(f"culture object: {culture_object_with_symbols.materialism} - {culture_object_with_symbols.materialism_symbol}")
        return culture_object_with_symbols
    
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
        orbital_detail_row[0][12] + orbital_detail_row[0][14],
        orbital_detail_row[0][13],
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
        int(round(journey_detail_row[0][2],0)),   # 1G Hrs
        int(round(journey_detail_row[0][3],0)),   # 2G Hrs
        int(round(journey_detail_row[0][4],0)),   # 3G Hrs
        int(round(journey_detail_row[0][5],0)),   # 4G Hrs
        int(round(journey_detail_row[0][6],0)),   # 5G Hrs
        int(round(journey_detail_row[0][7],0))    # 6G Hrs
        )
        detail_stats_object.jump_point_Mm = round(detail_stats_object.jump_point_Mm/1000,2)
        detail_stats_object.jump_point_Mm = "{:,}".format(detail_stats_object.jump_point_Mm)
     #   logging.debug(f' detail_stats: {journey_detail_row[0][0]}')
        
        return detail_stats_object
    
    def get_system_object(c, location):
        logging.debug(f'get_system_object local location: {location}')
        system_row = get_system_stats(c, location)
    #    logging.debug(system_row)
        system_object = System_details(
        location,
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
        trader_row[0][0],  #wtn
        trader_row[0][1],  #gwp
        round(trader_row[0][2],2),  #exchange
        trader_row[0][3],  #needs
        trader_row[0][4])  #wants/surplus
        
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
        
        df['uwp'] = df['starport'] + df['size'] + df['atmosphere'] + df['hydrographics'] +  \
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
        df['atmos_pressure'] = df['atmos_pressure'].round(2)
    
        df = fix_uwp(df)      
    
    
        return df
    
    
    
    def get_summary_table_data(df):
        data = [
        ['Loc-Orb','Name','UWP','Gr','Ri','Yr','Dy','Atm','Comp','Temp','1G','2G','3G','4G','5G','6G'],
        ]
        
        df['hrs_1g'] = df['hrs_1g'].round().astype(int)
        df['hrs_2g'] = df['hrs_2g'].round().astype(int)
        df['hrs_3g'] = df['hrs_3g'].round().astype(int)
        df['hrs_4g'] = df['hrs_4g'].round().astype(int)
        df['hrs_5g'] = df['hrs_5g'].round().astype(int)
        df['hrs_6g'] = df['hrs_6g'].round().astype(int)
        
    
        list_of_lists = df.values.tolist()
    
        data += list_of_lists
        
        return data

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
        col_widths = [45,75,45,25,15,27,20,25,20,32,20,20,20,18,18,18]
        table = Table(table_data, colWidths=col_widths,rowHeights=15)
        return table
    
    def update_summary_elems(text_before_table, summary_table, culture_lines):
        # Create a Spacer with a specified width and height
        spacer = Spacer(10, 10)
    
        # Add the Spacer to your elements list
        return  [
            
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
            culture_lines.status_quo_line,
            culture_lines.symbol_line,
            culture_lines.skills_line,
            PageBreak()
        ]
    
    
    # Add page numbers
    def add_page_number(canvas, doc):
            page_num = canvas.getPageNumber()
            if page_num != 1:  # Exclude page number from the first page
                text = "%s" % (page_num - 1)  # Adjust page number if excluding the first page
                canvas.setFont("Helvetica", 9)
                # Calculate the center position of the page number at the bottom of the page
                x = (letter[0] - inch) / 2  # Center horizontally
                y = 0.75 * inch  # Offset from the bottom
                canvas.drawString(x, y, text)
    
    
    # Reorder index for columns
    def reorder_for_table(data, num_columns):
        reordered_data = []
        num_rows = (len(data) + num_columns - 1) // num_columns  # Calculate the number of rows
        for i in range(num_rows):
            for j in range(num_columns):
                index = j * num_rows + i  # Calculate the new index for column-wise reordering
                if index < len(data):
                    reordered_data.append(data[index])
        return reordered_data
    
    
            
    # Generate paragraphs from index entries
    def create_index_paragraphs(index_name_list, ex_styles):
        for index_entry in index_name_list:
            if index_entry[0] != '*':
                cell_content = f"{index_entry[0]}: {index_entry[1]}"
            else:
                cell_content = "  "
            yield Paragraph(cell_content, ex_styles.index_entry_style)    
    
    
    
    # Generate and add the index table
    def create_index_table(paragraphs, index_table_style):
        # Define parameters
        num_columns = 4  # Adjust as needed
        page_width, page_height = letter
        # column_width = page_width / num_columns
        column_width = 120
    
        # Create table data list (one row per paragraph)
        table_data = []
        for i in range(0, len(paragraphs), num_columns):
            # Create a sublist with "num_columns" paragraphs
            row_data = paragraphs[i:i + num_columns]
            table_data.append(row_data)
    
        # Create table object
        index_table = Table(table_data, colWidths=[column_width] * num_columns, style=index_table_style)
    
        return index_table
    
    
    def build_index(index_name_list, ex_styles):
        pdf_index = []
        
        pdf_index.append(PageBreak())
        
        index_header_style = ex_styles.index_header_style
        
        pdf_index.append(Paragraph('INDEX', index_header_style))
        pdf_index.append(Spacer(1,30))
        
        index_page_limit = 120
        index_name_total = len(index_name_list)
        
        padding_entries = index_page_limit - (index_name_total % index_page_limit)
        if padding_entries > 0:
            for each_entry in range(0, padding_entries): index_name_list.append(('*','*'))
        
        index_name_total = len(index_name_list)
        
        index_name_pages = index_name_total // index_page_limit 
        
        logging.debug(f"Total index entries: {index_name_total}")
        logging.debug(f"Total expected index pages: {index_name_pages}")
        
        
        for index_page in range(0,index_name_pages):
            page_start = index_page_limit * index_page
            page_end = page_start + index_page_limit
            if page_end > index_name_total: page_end = index_name_total
            index_sub_list = index_name_list[page_start:page_end]
        
            reordered_index = reorder_for_table(index_sub_list, 4)
            
            index_paragraphs = list(create_index_paragraphs(reordered_index, ex_styles))
            index_table = create_index_table(index_paragraphs, ex_styles.index_table_style) 
           
            pdf_index.append(index_table)  # Add the table to the index list
            pdf_index.append(PageBreak())
    

        return pdf_index        

    def append_system_data(location, 
                                program_details, 
                                export_page_styles,
                                cursor,
                                conn):
        
        system_details = get_system_object(cursor, location)

        trader_details = get_far_trader_object(cursor, location)

        system_images = build_system_images(system_details, trader_details)
        
        system_images = add_remarks_images(system_images, system_details)

        program_details.elems = add_images_to_elems(system_images, program_details.elems, export_page_styles)
        
        text_before_table = Text_before_table()
        
        text_before_table.populate_system_text_before_table(system_details, export_page_styles)
        text_before_table.populate_trader_text_before_table(trader_details, export_page_styles)


        # Orbital Data Table for Location 
        df = get_orbital_data(conn, location)
        
        summary_table_data = get_summary_table_data(df)
        summary_table = get_summary_table(summary_table_data)
        summary_table.setStyle(export_page_styles.summary_table_style)
        alternate_background(summary_table, summary_table_data)
        
        culture_details = get_culture_stats_object(cursor, location)
        culture_lines = Culture_lines()
        culture_lines.populate_culture_lines(culture_details, export_page_styles)
        
        program_details.elems += update_summary_elems(text_before_table, summary_table, culture_lines)
        
    
        # Begin work on individual orbital bodies details
    
        # Grab the pre-loaded UWPs into a UWP dictionary with location_orbit as key
        loc_orbit_list = df['location_orbit'].to_list()
        name_list = df['system_name'].to_list()
        uwp_list = df['uwp'].to_list()
    
        uwp_dict = {loc_orbit_list: [name_list, uwp_list] for loc_orbit_list, name_list, uwp_list in zip(loc_orbit_list, name_list, uwp_list)}
        detail_list = df['location_orbit'].tolist()
    
    
        for d in detail_list:
            detail_stats = get_detail_stats_object(cursor,d,uwp_dict)                
            append_detail_entry(d, detail_stats, export_page_styles, program_details)
            
            

    def program_control(db,ss):
        program_details = Program_details(db, ss)
        
     
        # Connect to DB

        conn = sqlite3.connect(program_details.db_name)
        cursor = conn.cursor()
        
        # Gather Data
        location_list = get_location(cursor, program_details.subsector)
        index_name_list = get_index_names(cursor, location_list)

        export_page_styles = Export_page_styles()
        export_page_styles.populate_styles()
        
        
        build_cover_page(program_details)
        build_sector_map(program_details)

        
        first_run = True
        for location in location_list:

         
            if first_run:
                program_details.elems.append(PageBreak())       
            else:
                first_run = False
                
            append_system_data(location, 
                                    program_details, 
                                    export_page_styles,
                                    cursor,
                                    conn)
         
            

        
        # Add PageBreak to start the index on a new page
        pdf_index = build_index(index_name_list, export_page_styles)
        
        
        
        # Append the index_table to the elems list
        program_details.elems += pdf_index
        
        # Assign the custom canvas with page numbers to the PDF document
        pdf = SimpleDocTemplate(program_details.output_file_name,page_size = letter)
        pdf.build(program_details.elems, onLaterPages=add_page_number)
        
        # Merge the cover PDF with the main PDF
        merger = PdfMerger()
        merger.append("sector_db/cover.pdf")  # Add the cover PDF
        merger.append("sector_db/sec_map.pdf")  # Add the cover PDF
        merger.append(program_details.output_file_name)
        merger.write(program_details.output_file_name)  # Save the merged PDF
        merger.close()
        
        
        conn.commit()  
        cursor.close()
        conn.close() 

    
        
### FUNCTION START

    program_control(db,ss)


