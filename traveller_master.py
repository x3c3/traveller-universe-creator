def make_sector_master(decisions_provided):

    # Master program for Traveller universe build
    

    from first_in_generation import generate_stars
    from mainworld_calculator import generate_mainworld_scores
    from mainworld_selector import choose_mainworld
    from travellerization import add_traveller_stats
    from traveller_map import build_travellermap_file
    from non_mw import generate_non_mainworlds
    from far_trader import generate_far_trader_stats
    from journey_data import build_journey_table
    from routes_short_path import create_route_xml
    from culture import create_culture_stats
    import FreeSimpleGUI as sg

    
    seed_number = decisions_provided.random_seed
    sector_name = decisions_provided.sector_name
    settlement_mod = decisions_provided.settlement_mod
    


    db_name = 'sector_db/' + sector_name + '.db'
    print('Generating Stars and Planets')
    generate_stars(db_name,decisions_provided)
    print('Building the Journey stats table')
    build_journey_table(seed_number,db_name)
    print('Evaluating each orbital body for main world suitability')
    generate_mainworld_scores(db_name)
    print('Finalizing main world selections and building mainworld table')
    choose_mainworld(db_name)
    print('Travellerizing the main worlds')
    add_traveller_stats(seed_number,db_name,settlement_mod)
    print('Building Traveller Map extract')
    build_travellermap_file(db_name,sector_name)
    print('Adding data for non-main worlds') 
    generate_non_mainworlds(seed_number,db_name)
    print('Building Far Trader table')
    generate_far_trader_stats(seed_number,db_name)
    print('Building Culture table')
    create_culture_stats(seed_number,db_name)
    print('Building Routes file')
    create_route_xml(seed_number,db_name,settlement_mod)


    sg.popup('Sector completed successfully')    

