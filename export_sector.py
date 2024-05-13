def export_ss_to_pdf(db,ss):


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
    
    
    # Log a debug message
    logging.debug("Debug message")
    
    # Check the output destination
    print("Check output stream for debug messages")
    
    
    from reportlab.platypus import SimpleDocTemplate,Table, TableStyle, Paragraph, PageBreak, KeepTogether, Spacer, Image
    
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    from reportlab.lib.units import inch
    
    from reportlab.lib.enums import TA_CENTER
    
    import sqlite3
    
    import pandas as pd
    
    from traveller_functions import tohex, get_subsector_number_list, Culture_details, get_remarks_list
    
    
    def get_db(db):
        # Select the db file to print
        return db
    
    def get_subsector(ss):
        # Select the subsector letter
        return ss
    
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
    
    
    
    def get_output_file_name(db,ss):

        name = 'sector_db/subector_'+ ss + '.pdf'
        return name
    
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
    def create_index_paragraphs(index_name_list):
        for index_entry in index_name_list:
            if index_entry[0] != '*':
                cell_content = f"{index_entry[0]}: {index_entry[1]}"
            else:
                cell_content = "  "
            yield Paragraph(cell_content, ParagraphStyle(name='IndexEntry', fontSize=7))    
    
    
    
    # Generate and add the index table
    def create_index_table(paragraphs):
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
        index_table = Table(table_data, colWidths=[column_width] * num_columns, style=[
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Center all cells vertically
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center the entire table horizontally
        ])
    
        return index_table
    
    
        
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
                     status_quo_line,
                     symbol_line,
                     skills_line):
            self.header_line = header_line
            self.age_line = age_line
            self.status_quo_line = status_quo_line
            self.symbol_line = symbol_line
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
            self.mass = mass = round(mass,4)
            self.gravity = round(gravity,4)
            self.hill_radius = hill_radius
            self.natural_moons = natural_moons
            self.ring = ring
            self.impact_moons = impact_moons
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
            
        
        
    ##### Beginning of Program
    
    
    # Set parameters and file names
    db_name = get_db(db)
    subsector = get_subsector(ss)
    output_file_name = get_output_file_name(db_name,subsector)
    elems = []
    
    
    # Connect to DB
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # Gather Data
    location_list = get_location(c, subsector)
    index_name_list = get_index_names(c, location_list)
    
    
    
    
    
    # Path to the image file
    image_path = "atomic_cover.jpg"
    
    # Create an Image object with the specified image path and dimensions (if needed)
    image = Image(image_path)
    
    elems.append(image)
    
    
    
    
    
    for location in location_list:
        # Start with a new page
        
        elems.append(PageBreak())
    
        # Header, Lines, WantsNeeds Activities
        
    
        
     #   logging.debug(f'System: {location}')
        
     #   logging.debug(f'main program for statement: {location} {type(location)}')
     
     
     
     
        
        system_details = get_system_object(c, location)
        trader_details = get_far_trader_object(c, location)
        header_style, travel_style, wantsneeds_style, detail_style, detail_header_style = get_styles()
     
    
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
                logging.debug(f'Remark found in {location}: {system_image_path}')
        
        
        if len(system_images) > 0:
    
            
            # Create a table with a single row and add the images to it
            system_image_table = Table([system_images])
            
            system_image_table.setStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0,0), (-1,0), colors.gray),
            ])
               
    
            elems.append(system_image_table)
        
        else:
            logging.debug(f'No images for system {location}')
     
        
     
        
     
        
     
        
     
        
     
        
     
        
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
       # logging.debug(f"materialism: {culture_details.materialism_symbol}")
        
        
    
            
        culture_header_line = Paragraph("Cultural Perception",detail_style)
        culture_age_line = Paragraph(f"{culture_details.age.capitalize()}.  \
                                       {culture_details.appearance.capitalize()} appearance. \
                                       {culture_details.tendency.capitalize()} tendency." ,wantsneeds_style)
                               
        culture_status_quo_line = Paragraph(f"<b>Spr: </b>{culture_details.spiritual_outlook.capitalize()}. \
                                              <b>StQ: </b>{culture_details.status_quo_outlook.capitalize()}. \
                                              <b>Cus: </b>{culture_details.custom.capitalize()}.  \
                                              <b>Int: </b>{culture_details.interest.capitalize()}.",wantsneeds_style)            
                                              
        culture_symbol_line = Paragraph(f"Mat{culture_details.materialism_symbol}  \
                                          Hon{culture_details.honesty_symbol} \
                                          Brv{culture_details.bravery_symbol}  \
                                          SC{culture_details.social_conflict_symbol}  \
                                          WE{culture_details.work_ethic_symbol}  \
                                          Con{culture_details.consumerism_symbol}",wantsneeds_style)
                                          
                           
        culture_skills_line = Paragraph(f"<b>Common skills:</b> {culture_details.common_skills}",wantsneeds_style)  
        
        #logging.debug(f'Common skills for {location} are: {culture_details.common_skills}')
                                      
                                 
        culture_lines = Culture_lines(culture_header_line,
                                        culture_age_line,
                                        culture_status_quo_line,
                                        culture_symbol_line,
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
            
            images = []
            
            if detail_stats.year != 'none':
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
                logging.debug(f'Found an Ocean world {location}: {detail_stats.name} ')
                image_path = "images/ocean.png"
                image = Image(image_path)
                image.drawWidth = 25
                image.drawHeight = 25
                images.append(image)
            else:
                if location == '0922':
                    logging.debug(f'No Ocean world {detail_stats.name} {detail_stats.wtype}')
    
                    
    
    
    
                
                
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
                
    
                
                
                
          
                
            
    #        Create a table with a single row and add the images to it
            image_table = Table([images])
            
            image_table.setStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BACKGROUND', (0,0), (-1,0), colors.gray),
            ])
                
            
    
            
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
            detail_table = KeepTogether([image_table,detail_table])
            elems.append(detail_table)
            elems.append(Spacer(1, 30)) 
        
    
    
    
    # Initialize an empty list to store index entries
    
    # Add PageBreak to start the index on a new page
    pdf_index = []
    
    pdf_index.append(PageBreak())
    
    index_header_style = ParagraphStyle(name='IndexHeader', fontSize=12, alignment=TA_CENTER)
    
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
    logging.debug(f"Total expected pages: {index_name_pages}")
    
    
    for index_page in range(0,index_name_pages):
        page_start = index_page_limit * index_page
        page_end = page_start + index_page_limit
        if page_end > index_name_total: page_end = index_name_total
        index_sub_list = index_name_list[page_start:page_end]
    
        reordered_index = reorder_for_table(index_sub_list, 4)
        
        index_paragraphs = list(create_index_paragraphs(reordered_index))
        index_table = create_index_table(index_paragraphs)  # Call the function
       
        pdf_index.append(index_table)  # Add the table to the index list
        pdf_index.append(PageBreak())
    
    
    # Append the index_table to the elems list
    elems += pdf_index
    
    # Assign the custom canvas with page numbers to the PDF document
    pdf = SimpleDocTemplate(output_file_name,page_size = letter)
    pdf.build(elems, onLaterPages=add_page_number)
    
    
    conn.commit()  
    c.close()
    conn.close() 