# Comprehensive motorcycle database with 1000+ motorcycles
# This file contains the complete motorcycle data for seeding

def get_comprehensive_motorcycle_data():
    """Returns comprehensive motorcycle database with 1000+ entries"""
    
    # High-quality curated images for different motorcycle types
    SPORT_BIKE_IMAGES = [
        "https://images.unsplash.com/photo-1611873189125-324514ebd94e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwyfHxzcG9ydCUyMGJpa2V8ZW58MHx8fHwxNzUzNzA5MjAwfDA&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwzfHxzcG9ydCUyMGJpa2V8ZW58MHx8fHwxNzUzNzA5MjAwfDA&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwOTE5NHww&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1523375592572-5fa3474dda8b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHxzcG9ydCUyMGJpa2V8ZW58MHx8fHwxNzUzNzA5MjAwfDA&ixlib=rb-4.1.0&q=85"
    ]
    
    CRUISER_IMAGES = [
        "https://images.unsplash.com/photo-1558981806-ec527fa84c39?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwOTE5NHww&ixlib=rb-4.1.0&q=85",
        "https://images.unsplash.com/photo-1531327431456-837da4b1d562?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHw0fHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwOTE5NHww&ixlib=rb-4.1.0&q=85"
    ]
    
    NAKED_IMAGES = [
        "https://images.unsplash.com/photo-1591637333184-19aa84b3e01f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwzfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwOTE5NHww&ixlib=rb-4.1.0&q=85"
    ]
    
    ADVENTURE_IMAGES = [
        "https://images.pexels.com/photos/1416169/pexels-photo-1416169.jpeg"
    ]
    
    VINTAGE_IMAGES = [
        "https://images.pexels.com/photos/2116475/pexels-photo-2116475.jpeg"
    ]
    
    # Professional placeholder images for when specific images aren't available
    PLACEHOLDER_IMAGES = [
        "https://images.unsplash.com/photo-1558980664-2cd663cf8dde?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxtb3RvcmN5Y2xlfGVufDB8fHxibGFja19hbmRfd2hpdGV8MTc1MzgxMDQyNXww&ixlib=rb-4.1.0&q=85",  # Professional motorcycle silhouette
        "https://images.unsplash.com/photo-1532895215727-c006c8fdf560?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwyfHxtb3RvcmN5Y2xlfGVufDB8fHxibGFja19hbmRfd2hpdGV8MTc1MzgxMDQyNXww&ixlib=rb-4.1.0&q=85",  # Clean motorcycle profile
        "https://images.pexels.com/photos/104842/bmw-vehicle-ride-bike-104842.jpeg"  # Generic motorcycle image
    ]

    # BAJAJ - Complete Model Range (2000-2025)
    bajaj_models = [
        # Pulsar Series
        {"model": "Pulsar 220F", "years": list(range(2007, 2026)), "category": "Sport", "displacement": 220, "horsepower": 21, "price_base": 2800, "interest": 88},
        {"model": "Pulsar 200NS", "years": list(range(2012, 2026)), "category": "Naked", "displacement": 200, "horsepower": 23, "price_base": 2600, "interest": 85},
        {"model": "Pulsar 150", "years": list(range(2001, 2026)), "category": "Naked", "displacement": 149, "horsepower": 14, "price_base": 1800, "interest": 82},
        {"model": "Pulsar 180", "years": list(range(2005, 2026)), "category": "Sport", "displacement": 178, "horsepower": 17, "price_base": 2200, "interest": 80},
        {"model": "Pulsar RS200", "years": list(range(2015, 2026)), "category": "Sport", "displacement": 200, "horsepower": 24, "price_base": 3200, "interest": 86},
        
        # Dominar Series
        {"model": "Dominar 400", "years": list(range(2017, 2026)), "category": "Adventure", "displacement": 373, "horsepower": 40, "price_base": 4500, "interest": 84},
        {"model": "Dominar 250", "years": list(range(2020, 2026)), "category": "Adventure", "displacement": 248, "horsepower": 27, "price_base": 3800, "interest": 79},
        
        # Avenger Series
        {"model": "Avenger 220", "years": list(range(2008, 2026)), "category": "Cruiser", "displacement": 220, "horsepower": 19, "price_base": 2500, "interest": 75},
        {"model": "Avenger 160", "years": list(range(2015, 2026)), "category": "Cruiser", "displacement": 160, "horsepower": 15, "price_base": 2200, "interest": 72},
        
        # Platina Series
        {"model": "Platina 110", "years": list(range(2006, 2026)), "category": "Commuter", "displacement": 115, "horsepower": 8, "price_base": 1200, "interest": 65},
        {"model": "Platina 100", "years": list(range(2003, 2026)), "category": "Commuter", "displacement": 102, "horsepower": 8, "price_base": 1100, "interest": 68},
        
        # CT Series
        {"model": "CT 100", "years": list(range(2000, 2026)), "category": "Commuter", "displacement": 102, "horsepower": 7, "price_base": 1000, "interest": 70},
        {"model": "CT 110", "years": list(range(2008, 2026)), "category": "Commuter", "displacement": 115, "horsepower": 8, "price_base": 1150, "interest": 69},
        
        # Chetak Electric
        {"model": "Chetak Electric", "years": list(range(2020, 2026)), "category": "Electric", "displacement": 0, "horsepower": 6, "price_base": 3500, "interest": 76},
    ]

    # HERO - Complete Model Range (2000-2025)
    hero_models = [
        # Splendor Series
        {"model": "Splendor Plus", "years": list(range(2000, 2026)), "category": "Commuter", "displacement": 97, "horsepower": 8, "price_base": 1100, "interest": 85},
        {"model": "Splendor iSmart", "years": list(range(2013, 2026)), "category": "Commuter", "displacement": 113, "horsepower": 9, "price_base": 1300, "interest": 78},
        {"model": "Super Splendor", "years": list(range(2003, 2026)), "category": "Commuter", "displacement": 124, "horsepower": 11, "price_base": 1500, "interest": 80},
        
        # Passion Series
        {"model": "Passion Pro", "years": list(range(2006, 2026)), "category": "Commuter", "displacement": 113, "horsepower": 9, "price_base": 1200, "interest": 82},
        {"model": "Passion XPro", "years": list(range(2012, 2026)), "category": "Commuter", "displacement": 113, "horsepower": 9, "price_base": 1400, "interest": 79},
        
        # Glamour Series
        {"model": "Glamour", "years": list(range(2005, 2026)), "category": "Commuter", "displacement": 124, "horsepower": 11, "price_base": 1400, "interest": 77},
        {"model": "Glamour i3S", "years": list(range(2017, 2026)), "category": "Commuter", "displacement": 124, "horsepower": 11, "price_base": 1600, "interest": 75},
        
        # HF Series
        {"model": "HF Deluxe", "years": list(range(2006, 2026)), "category": "Commuter", "displacement": 97, "horsepower": 8, "price_base": 1000, "interest": 88},
        {"model": "HF 100", "years": list(range(2007, 2026)), "category": "Commuter", "displacement": 97, "horsepower": 8, "price_base": 950, "interest": 86},
        
        # Xtreme Series
        {"model": "Xtreme 200R", "years": list(range(2014, 2026)), "category": "Sport", "displacement": 199, "horsepower": 18, "price_base": 2200, "interest": 81},
        {"model": "Xtreme 160R", "years": list(range(2020, 2026)), "category": "Sport", "displacement": 163, "horsepower": 15, "price_base": 1800, "interest": 83},
        
        # Maestro Series
        {"model": "Maestro Edge 125", "years": list(range(2014, 2026)), "category": "Scooter", "displacement": 124, "horsepower": 9, "price_base": 1500, "interest": 74},
        {"model": "Maestro Edge 110", "years": list(range(2016, 2026)), "category": "Scooter", "displacement": 110, "horsepower": 8, "price_base": 1300, "interest": 76},
        
        # Destini Series
        {"model": "Destini 125", "years": list(range(2018, 2026)), "category": "Scooter", "displacement": 124, "horsepower": 9, "price_base": 1400, "interest": 73},
        
        # Pleasure Series
        {"model": "Pleasure Plus", "years": list(range(2013, 2026)), "category": "Scooter", "displacement": 110, "horsepower": 8, "price_base": 1200, "interest": 71},
        
        # Xpulse Series
        {"model": "Xpulse 200", "years": list(range(2019, 2026)), "category": "Adventure", "displacement": 199, "horsepower": 18, "price_base": 2500, "interest": 87},
        {"model": "Xpulse 200T", "years": list(range(2019, 2026)), "category": "Adventure", "displacement": 199, "horsepower": 18, "price_base": 2400, "interest": 84},
    ]

    # TVS - Complete Model Range (2000-2025)
    tvs_models = [
        # Apache Series
        {"model": "Apache RTR 160", "years": list(range(2006, 2026)), "category": "Sport", "displacement": 159, "horsepower": 17, "price_base": 1900, "interest": 85},
        {"model": "Apache RTR 200 4V", "years": list(range(2016, 2026)), "category": "Sport", "displacement": 197, "horsepower": 20, "price_base": 2500, "interest": 87},
        {"model": "Apache RR 310", "years": list(range(2017, 2026)), "category": "Sport", "displacement": 312, "horsepower": 34, "price_base": 4200, "interest": 89},
        {"model": "Apache RTR 180", "years": list(range(2013, 2026)), "category": "Sport", "displacement": 177, "horsepower": 17, "price_base": 2100, "interest": 82},
        {"model": "Apache RTR 310", "years": list(range(2022, 2026)), "category": "Naked", "displacement": 312, "horsepower": 34, "price_base": 3800, "interest": 86},
        
        # Star City Series
        {"model": "Star City Plus", "years": list(range(2007, 2026)), "category": "Commuter", "displacement": 109, "horsepower": 8, "price_base": 1200, "interest": 78},
        
        # Radeon Series
        {"model": "Radeon", "years": list(range(2018, 2026)), "category": "Commuter", "displacement": 109, "horsepower": 8, "price_base": 1100, "interest": 75},
        
        # Sport Series
        {"model": "Sport 110", "years": list(range(2013, 2026)), "category": "Commuter", "displacement": 109, "horsepower": 8, "price_base": 1000, "interest": 73},
        
        # Jupiter Series
        {"model": "Jupiter 125", "years": list(range(2013, 2026)), "category": "Scooter", "displacement": 124, "horsepower": 8, "price_base": 1400, "interest": 79},
        {"model": "Jupiter Classic", "years": list(range(2014, 2026)), "category": "Scooter", "displacement": 109, "horsepower": 8, "price_base": 1300, "interest": 76},
        
        # Ntorq Series
        {"model": "Ntorq 125", "years": list(range(2018, 2026)), "category": "Scooter", "displacement": 124, "horsepower": 9, "price_base": 1600, "interest": 81},
        
        # iQube Electric
        {"model": "iQube Electric", "years": list(range(2020, 2026)), "category": "Electric", "displacement": 0, "horsepower": 6, "price_base": 2800, "interest": 77},
        
        # Ronin Series
        {"model": "Ronin", "years": list(range(2022, 2026)), "category": "Cruiser", "displacement": 225, "horsepower": 20, "price_base": 2700, "interest": 83},
    ]

    # ROYAL ENFIELD - Complete Model Range (2000-2025)
    royal_enfield_models = [
        # Classic Series
        {"model": "Classic 350", "years": list(range(2009, 2026)), "category": "Cruiser", "displacement": 346, "horsepower": 20, "price_base": 3500, "interest": 92},
        {"model": "Classic 500", "years": list(range(2009, 2021)), "category": "Cruiser", "displacement": 499, "horsepower": 27, "price_base": 4200, "interest": 89},
        {"model": "Classic 650", "years": list(range(2023, 2026)), "category": "Cruiser", "displacement": 648, "horsepower": 47, "price_base": 5500, "interest": 94},
        
        # Bullet Series
        {"model": "Bullet 350", "years": list(range(2000, 2026)), "category": "Cruiser", "displacement": 346, "horsepower": 19, "price_base": 3200, "interest": 88},
        {"model": "Bullet 500", "years": list(range(2000, 2021)), "category": "Cruiser", "displacement": 499, "horsepower": 27, "price_base": 3800, "interest": 85},
        
        # Hunter Series
        {"model": "Hunter 350", "years": list(range(2022, 2026)), "category": "Roadster", "displacement": 346, "horsepower": 20, "price_base": 3300, "interest": 90},
        
        # Interceptor Series
        {"model": "Interceptor 650", "years": list(range(2018, 2026)), "category": "Roadster", "displacement": 648, "horsepower": 47, "price_base": 5800, "interest": 95},
        
        # Continental GT Series
        {"model": "Continental GT 650", "years": list(range(2018, 2026)), "category": "Sport", "displacement": 648, "horsepower": 47, "price_base": 6200, "interest": 93},
        
        # Himalayan Series
        {"model": "Himalayan", "years": list(range(2016, 2026)), "category": "Adventure", "displacement": 411, "horsepower": 24, "price_base": 4500, "interest": 91},
        {"model": "Himalayan 450", "years": list(range(2023, 2026)), "category": "Adventure", "displacement": 452, "horsepower": 40, "price_base": 5200, "interest": 96},
        
        # Meteor Series
        {"model": "Meteor 350", "years": list(range(2020, 2026)), "category": "Cruiser", "displacement": 346, "horsepower": 20, "price_base": 3700, "interest": 87},
        
        # Thunderbird Series (Discontinued)
        {"model": "Thunderbird 350", "years": list(range(2012, 2020)), "category": "Cruiser", "displacement": 346, "horsepower": 19, "price_base": 3400, "interest": 84},
        {"model": "Thunderbird 500", "years": list(range(2012, 2020)), "category": "Cruiser", "displacement": 499, "horsepower": 27, "price_base": 4000, "interest": 86},
        
        # Scram Series
        {"model": "Scram 411", "years": list(range(2022, 2026)), "category": "Adventure", "displacement": 411, "horsepower": 24, "price_base": 4200, "interest": 88},
    ]

    # KTM - Complete Model Range (2000-2025)
    ktm_models = [
        # Duke Series
        {"model": "Duke 200", "years": list(range(2012, 2026)), "category": "Naked", "displacement": 199, "horsepower": 25, "price_base": 3200, "interest": 88},
        {"model": "Duke 250", "years": list(range(2017, 2026)), "category": "Naked", "displacement": 248, "horsepower": 30, "price_base": 3800, "interest": 87},
        {"model": "Duke 390", "years": list(range(2013, 2026)), "category": "Naked", "displacement": 373, "horsepower": 43, "price_base": 4800, "interest": 92},
        {"model": "Duke 125", "years": list(range(2018, 2026)), "category": "Naked", "displacement": 124, "horsepower": 15, "price_base": 2800, "interest": 85},
        {"model": "Duke 890", "years": list(range(2020, 2026)), "category": "Naked", "displacement": 889, "horsepower": 115, "price_base": 13000, "interest": 89},
        {"model": "Duke 790", "years": list(range(2018, 2023)), "category": "Naked", "displacement": 799, "horsepower": 105, "price_base": 12000, "interest": 86},
        
        # RC Series
        {"model": "RC 200", "years": list(range(2014, 2026)), "category": "Sport", "displacement": 199, "horsepower": 25, "price_base": 3500, "interest": 89},
        {"model": "RC 390", "years": list(range(2014, 2026)), "category": "Sport", "displacement": 373, "horsepower": 43, "price_base": 5200, "interest": 93},
        {"model": "RC 125", "years": list(range(2019, 2026)), "category": "Sport", "displacement": 124, "horsepower": 15, "price_base": 3100, "interest": 86},
        
        # Adventure Series
        {"model": "Adventure 390", "years": list(range(2020, 2026)), "category": "Adventure", "displacement": 373, "horsepower": 43, "price_base": 5800, "interest": 91},
        {"model": "Adventure 250", "years": list(range(2021, 2026)), "category": "Adventure", "displacement": 248, "horsepower": 30, "price_base": 4500, "interest": 88},
        
        # Supermoto Series
        {"model": "SMC R 690", "years": list(range(2019, 2026)), "category": "Supermoto", "displacement": 693, "horsepower": 74, "price_base": 11000, "interest": 87},
        
        # High-End Models
        {"model": "1290 Super Duke R", "years": list(range(2014, 2026)), "category": "Naked", "displacement": 1301, "horsepower": 177, "price_base": 18000, "interest": 94},
        {"model": "1290 Super Adventure", "years": list(range(2015, 2026)), "category": "Adventure", "displacement": 1301, "horsepower": 160, "price_base": 19500, "interest": 90},
    ]

    # HARLEY-DAVIDSON - Complete Model Range (2000-2025)
    harley_models = [
        # Sportster Series
        {"model": "Sportster Iron 883", "years": list(range(2009, 2023)), "category": "Cruiser", "displacement": 883, "horsepower": 50, "price_base": 9000, "interest": 88},
        {"model": "Sportster 1200", "years": list(range(2000, 2023)), "category": "Cruiser", "displacement": 1202, "horsepower": 67, "price_base": 11000, "interest": 89},
        {"model": "Sportster S", "years": list(range(2021, 2026)), "category": "Cruiser", "displacement": 1252, "horsepower": 121, "price_base": 14999, "interest": 92},
        
        # Street Series
        {"model": "Street 750", "years": list(range(2014, 2023)), "category": "Cruiser", "displacement": 749, "horsepower": 47, "price_base": 7500, "interest": 85},
        {"model": "Street Rod 750", "years": list(range(2017, 2020)), "category": "Cruiser", "displacement": 749, "horsepower": 55, "price_base": 8700, "interest": 83},
        
        # Softail Series
        {"model": "Softail Standard", "years": list(range(2020, 2026)), "category": "Cruiser", "displacement": 1746, "horsepower": 86, "price_base": 15000, "interest": 91},
        {"model": "Fat Bob", "years": list(range(2018, 2026)), "category": "Cruiser", "displacement": 1746, "horsepower": 86, "price_base": 17000, "interest": 89},
        {"model": "Low Rider", "years": list(range(2018, 2026)), "category": "Cruiser", "displacement": 1746, "horsepower": 86, "price_base": 16500, "interest": 87},
        
        # Touring Series
        {"model": "Road King", "years": list(range(2000, 2026)), "category": "Touring", "displacement": 1746, "horsepower": 86, "price_base": 20000, "interest": 90},
        {"model": "Street Glide", "years": list(range(2006, 2026)), "category": "Touring", "displacement": 1746, "horsepower": 86, "price_base": 22000, "interest": 92},
        {"model": "Electra Glide", "years": list(range(2000, 2026)), "category": "Touring", "displacement": 1746, "horsepower": 86, "price_base": 24000, "interest": 89},
        
        # Pan America Series
        {"model": "Pan America 1250", "years": list(range(2021, 2026)), "category": "Adventure", "displacement": 1252, "horsepower": 150, "price_base": 17319, "interest": 94},
        
        # LiveWire Series
        {"model": "LiveWire", "years": list(range(2019, 2026)), "category": "Electric", "displacement": 0, "horsepower": 105, "price_base": 29799, "interest": 86},
    ]

    comprehensive_motorcycles = []
    
    # Helper function to generate motorcycle data
    def generate_motorcycles_for_brand(brand_name, models_list, brand_specialisations=None):
        """Generate comprehensive motorcycle data for a brand"""
        brand_motorcycles = []
        
        # Default specialisations for each brand
        if brand_specialisations is None:
            brand_specialisations = {
                "Yamaha": ["Sport Performance", "Reliability", "Advanced Electronics"],
                "Honda": ["Fuel Efficiency", "Reliability", "Innovation"],
                "Kawasaki": ["Raw Power", "Sport Performance", "Track Ready"],
                "Suzuki": ["Value Engineering", "Reliability", "Performance"],
                "Ducati": ["Italian Design", "Racing Heritage", "Premium Performance"],
                "Bajaj": ["Affordability", "Indian Engineering", "Value for Money"],
                "Hero": ["Fuel Efficiency", "Reliability", "Low Maintenance"],
                "TVS": ["Innovation", "Sport Performance", "Value Engineering"],
                "Royal Enfield": ["Classic Design", "Thumper Sound", "Heritage"],
                "KTM": ["Ready to Race", "Lightweight", "Austrian Engineering"],
                "Harley-Davidson": ["American Heritage", "V-Twin Sound", "Cruising Comfort"],
                "CFMOTO": ["Chinese Engineering", "Value", "Modern Design"],
                "Keeway": ["Affordable Sport", "European Style", "Entry Level"],
                "Lifan": ["Budget Friendly", "Basic Transport", "Chinese Manufacturing"],
                "GPX": ["Thai Engineering", "Affordable Performance", "Local Design"],
                "QJ Motor": ["Modern Chinese", "Advanced Features", "Value Pricing"],
                "Vespa": ["Italian Style", "Classic Design", "Urban Mobility"],
                "Runner": ["Bangladeshi Brand", "Local Assembly", "Affordable"],
                "Benelli": ["Italian Heritage", "Performance", "Design"],
                "Mahindra": ["Indian Manufacturing", "Rugged Build", "Value"],
                "Jawa": ["Classic Revival", "Retro Style", "Nostalgia"]
            }.get(brand_name, ["Performance", "Reliability", "Value"])
        
        for model_data in models_list:
            for year in model_data["years"]:
                # Calculate price variation by year and availability
                base_price = model_data["price_base"]
                price_variation = (year - 2000) * (base_price * 0.02)  # 2% increase per year
                final_price = int(base_price + price_variation)
                
                # Determine availability
                if year >= 2023:
                    availability = "Available"
                elif year >= 2020:
                    availability = "Limited Stock"
                elif year >= 2015:
                    availability = "Discontinued"
                else:
                    availability = "Collector Item"
                
                # Select appropriate image based on category with better fallback
                def get_motorcycle_image(category, model_name):
                    """Get appropriate image for motorcycle with fallback to placeholder"""
                    try:
                        if category in ["Sport", "Supersport"]:
                            if len(SPORT_BIKE_IMAGES) > 0:
                                return SPORT_BIKE_IMAGES[hash(model_name) % len(SPORT_BIKE_IMAGES)]
                        elif category in ["Naked", "Roadster"]:
                            if len(NAKED_IMAGES) > 0:
                                return NAKED_IMAGES[0]
                        elif category in ["Cruiser", "Touring", "Bobber"]:
                            if len(CRUISER_IMAGES) > 0:
                                return CRUISER_IMAGES[hash(model_name) % len(CRUISER_IMAGES)]
                        elif category in ["Adventure", "Enduro", "Dual Sport"]:
                            if len(ADVENTURE_IMAGES) > 0:
                                return ADVENTURE_IMAGES[0]
                        elif category in ["Vintage", "Classic"]:
                            if len(VINTAGE_IMAGES) > 0:
                                return VINTAGE_IMAGES[0]
                        
                        # Fallback to placeholder for unknown categories or empty image arrays
                        return PLACEHOLDER_IMAGES[hash(model_name) % len(PLACEHOLDER_IMAGES)]
                        
                    except (IndexError, ZeroDivisionError):
                        # Emergency fallback to first placeholder
                        return PLACEHOLDER_IMAGES[0] if PLACEHOLDER_IMAGES else "https://via.placeholder.com/400x300/666666/ffffff?text=Motorcycle"
                
                image_url = get_motorcycle_image(model_data["category"], model_data["model"])
                
                # Generate detailed technical specifications
                displacement = model_data["displacement"]
                horsepower = model_data["horsepower"]
                
                # Engine configuration based on displacement
                if displacement == 0:  # Electric
                    engine_type = "Electric Motor"
                elif displacement <= 125:
                    engine_type = "Single Cylinder"
                elif displacement <= 400:
                    engine_type = "Single Cylinder" if brand_name in ["KTM", "Bajaj"] else "Parallel Twin"
                elif displacement <= 600:
                    engine_type = "Parallel Twin"
                elif displacement <= 1000:
                    engine_type = "Inline-4" if model_data["category"] == "Sport" else "Parallel Twin"
                else:
                    engine_type = "V-Twin" if brand_name == "Harley-Davidson" else "Inline-4"
                
                motorcycle = {
                    "manufacturer": brand_name,
                    "model": model_data["model"],
                    "year": year,
                    "category": model_data["category"],
                    "engine_type": engine_type,
                    "displacement": displacement,
                    "horsepower": horsepower,
                    "torque": int(horsepower * 0.75) if horsepower > 0 else 25,  # Approximate torque
                    "weight": max(120, 140 + (displacement // 10)),  # Approximate weight
                    "top_speed": int(90 + (horsepower * 1.5)) if horsepower > 0 else 80,
                    "fuel_capacity": max(10.0, 12.0 + (displacement // 150)),
                    "price_usd": final_price,
                    "availability": availability,
                    "description": f"The {brand_name} {model_data['model']} {year} represents {brand_name}'s commitment to excellence in the {model_data['category'].lower()} segment. This model showcases the brand's engineering prowess and dedication to rider satisfaction.",
                    "image_url": image_url,
                    "user_interest_score": model_data["interest"],
                    "specialisations": brand_specialisations[:3],  # Take first 3 specialisations
                    
                    # Detailed technical features
                    "mileage_kmpl": max(15, 45 - (displacement // 20)) if displacement > 0 else 0,  # Electric bikes handled separately
                    "transmission_type": "Manual" if displacement > 125 else "Automatic",
                    "number_of_gears": 6 if displacement > 400 else 5 if displacement > 125 else 1,
                    "ground_clearance_mm": 160 + (20 if model_data["category"] == "Adventure" else 0),
                    "seat_height_mm": 750 + (displacement // 20) + (30 if model_data["category"] == "Adventure" else 0),
                    "abs_available": year >= 2019 and displacement >= 125,
                    "braking_system": "Disc" if displacement >= 125 else "Drum",
                    "suspension_type": "Telescopic" if displacement >= 200 else "Conventional",
                    "tyre_type": "Tubeless" if year >= 2015 and displacement >= 150 else "Tube",
                    "wheel_size_inches": f"{17 if displacement >= 200 else 18}",
                    "headlight_type": "LED" if year >= 2020 else "Halogen",
                    "fuel_type": "Electric" if displacement == 0 else "Petrol"
                }
                
                # Special handling for electric vehicles
                if displacement == 0:
                    motorcycle.update({
                        "mileage_kmpl": 0,  # Not applicable
                        "top_speed": 60,  # Typical electric scooter speed
                        "fuel_capacity": 0,  # Battery capacity instead
                        "transmission_type": "Automatic",
                        "number_of_gears": 1
                    })
                
                brand_motorcycles.append(motorcycle)
        
        return brand_motorcycles
    
    # YAMAHA - Complete Model Range (2000-2025)
    yamaha_models = [
        # YZF-R Series (Sport)
        {"model": "YZF-R1", "years": list(range(2000, 2026)), "category": "Sport", "displacement": 998, "horsepower": 200, "price_base": 18000, "interest": 98},
        {"model": "YZF-R6", "years": list(range(2000, 2026)), "category": "Sport", "displacement": 599, "horsepower": 118, "price_base": 12000, "interest": 95},
        {"model": "YZF-R3", "years": list(range(2015, 2026)), "category": "Sport", "displacement": 321, "horsepower": 42, "price_base": 5300, "interest": 87},
        {"model": "YZF-R7", "years": list(range(2021, 2026)), "category": "Sport", "displacement": 689, "horsepower": 73, "price_base": 8999, "interest": 89},
        {"model": "YZF-R15", "years": list(range(2017, 2026)), "category": "Sport", "displacement": 155, "horsepower": 19, "price_base": 4000, "interest": 78},
        {"model": "YZF-R25", "years": list(range(2014, 2026)), "category": "Sport", "displacement": 249, "horsepower": 36, "price_base": 4500, "interest": 82},
        
        # MT Series (Naked)
        {"model": "MT-09", "years": list(range(2013, 2026)), "category": "Naked", "displacement": 847, "horsepower": 115, "price_base": 9699, "interest": 92},
        {"model": "MT-07", "years": list(range(2014, 2026)), "category": "Naked", "displacement": 689, "horsepower": 73, "price_base": 7699, "interest": 94},
        {"model": "MT-03", "years": list(range(2016, 2026)), "category": "Naked", "displacement": 321, "horsepower": 42, "price_base": 4599, "interest": 85},
        {"model": "MT-10", "years": list(range(2016, 2026)), "category": "Naked", "displacement": 998, "horsepower": 160, "price_base": 13499, "interest": 91},
        {"model": "MT-15", "years": list(range(2019, 2026)), "category": "Naked", "displacement": 155, "horsepower": 19, "price_base": 3500, "interest": 79},
        
        # FZ Series
        {"model": "FZ-09", "years": list(range(2014, 2017)), "category": "Naked", "displacement": 847, "horsepower": 115, "price_base": 8190, "interest": 88},
        {"model": "FZ-07", "years": list(range(2015, 2018)), "category": "Naked", "displacement": 689, "horsepower": 68, "price_base": 6990, "interest": 86},
        {"model": "FZ-06", "years": list(range(2004, 2009)), "category": "Naked", "displacement": 600, "horsepower": 98, "price_base": 6000, "interest": 81},
        
        # Tenere Adventure Series
        {"model": "Tenere 700", "years": list(range(2019, 2026)), "category": "Adventure", "displacement": 689, "horsepower": 72, "price_base": 10199, "interest": 89},
        {"model": "Super Tenere", "years": list(range(2010, 2026)), "category": "Adventure", "displacement": 1199, "horsepower": 113, "price_base": 16399, "interest": 85},
        
        # Cruiser Series
        {"model": "V Star 650", "years": list(range(2000, 2017)), "category": "Cruiser", "displacement": 649, "horsepower": 40, "price_base": 6590, "interest": 73},
        {"model": "V Star 950", "years": list(range(2009, 2017)), "category": "Cruiser", "displacement": 942, "horsepower": 52, "price_base": 8290, "interest": 75},
        {"model": "V Star 1300", "years": list(range(2007, 2017)), "category": "Cruiser", "displacement": 1304, "horsepower": 71, "price_base": 10990, "interest": 77},
        {"model": "Bolt", "years": list(range(2014, 2018)), "category": "Cruiser", "displacement": 942, "horsepower": 52, "price_base": 7990, "interest": 80},
        
        # Touring
        {"model": "FJR1300", "years": list(range(2001, 2026)), "category": "Touring", "displacement": 1298, "horsepower": 145, "price_base": 17999, "interest": 84},
        
        # Scooter
        {"model": "TMAX", "years": list(range(2001, 2026)), "category": "Scooter", "displacement": 530, "horsepower": 47, "price_base": 11199, "interest": 82},
        {"model": "XMAX", "years": list(range(2017, 2026)), "category": "Scooter", "displacement": 292, "horsepower": 27, "price_base": 5699, "interest": 78},
        
        # Off-Road
        {"model": "WR450F", "years": list(range(2003, 2026)), "category": "Enduro", "displacement": 449, "horsepower": 58, "price_base": 9799, "interest": 86},
        {"model": "YZ450F", "years": list(range(2003, 2026)), "category": "Motocross", "displacement": 449, "horsepower": 58, "price_base": 9399, "interest": 84},
    ]
    
    for model_data in yamaha_models:
        for year in model_data["years"]:
            # Calculate price variation by year
            price_variation = (year - 2000) * 200  # Increase price over time
            availability = "Available" if year >= 2020 else "Discontinued" if year >= 2015 else "Collector Item"
            
            # Select appropriate image based on category
            if model_data["category"] == "Sport":
                image_url = SPORT_BIKE_IMAGES[hash(model_data["model"]) % len(SPORT_BIKE_IMAGES)]
            elif model_data["category"] == "Naked":
                image_url = NAKED_IMAGES[0]
            elif model_data["category"] == "Cruiser":
                image_url = CRUISER_IMAGES[hash(model_data["model"]) % len(CRUISER_IMAGES)]
            elif model_data["category"] == "Adventure":
                image_url = ADVENTURE_IMAGES[0]
            else:
                image_url = SPORT_BIKE_IMAGES[0]
            
            motorcycle = {
                "manufacturer": "Yamaha",
                "model": model_data["model"],
                "year": year,
                "category": model_data["category"],
                "engine_type": "Inline-4" if model_data["displacement"] > 600 else "Parallel Twin" if model_data["displacement"] > 300 else "Single",
                "displacement": model_data["displacement"],
                "horsepower": model_data["horsepower"],
                "torque": int(model_data["horsepower"] * 0.75),  # Approximate torque
                "weight": 180 + (model_data["displacement"] // 10),  # Approximate weight
                "top_speed": int(120 + (model_data["horsepower"] * 1.2)),
                "fuel_capacity": 15.0 + (model_data["displacement"] // 100),
                "price_usd": model_data["price_base"] + price_variation,
                "availability": availability,
                "description": f"The Yamaha {model_data['model']} {year} represents Yamaha's commitment to performance and innovation in the {model_data['category'].lower()} category. Known for reliability, advanced engineering, and exceptional ride quality.",
                "image_url": image_url,
                "specialisations": ["Yamaha Reliability", "Advanced Engineering", "Performance Oriented", "Quality Components", "Proven Design"],
                
                # Technical Features
                "mileage_kmpl": 35.0 if model_data["displacement"] < 200 else 25.0 if model_data["displacement"] < 500 else 18.0 if model_data["displacement"] < 1000 else 15.0,
                "transmission_type": "Manual" if model_data["category"] != "Scooter" else "CVT",
                "number_of_gears": 6 if model_data["displacement"] > 400 else 5,
                "ground_clearance_mm": 160 if model_data["category"] == "Sport" else 180 if model_data["category"] in ["Naked", "Standard"] else 200,
                "seat_height_mm": 820 if model_data["category"] == "Sport" else 800 if model_data["category"] in ["Naked", "Standard"] else 780,
                "abs_available": year >= 2015,
                "braking_system": "Disc" if model_data["displacement"] > 150 else "Drum",
                "suspension_type": "USD Fork" if model_data["category"] == "Sport" else "Telescopic",
                "tyre_type": "Tubeless" if year >= 2010 else "Tube",
                "wheel_size_inches": f"{'17' if model_data['displacement'] > 300 else '16'}",
                "headlight_type": "LED" if year >= 2018 else "Halogen",
                "fuel_type": "Petrol",
                
                "user_interest_score": model_data["interest"]
            }
            comprehensive_motorcycles.append(motorcycle)
    
    # HONDA - Complete Model Range (2000-2025)
    honda_models = [
        # CBR Series (Sport)
        {"model": "CBR1000RR", "years": list(range(2004, 2026)), "category": "Sport", "displacement": 999, "horsepower": 189, "price_base": 16499, "interest": 97},
        {"model": "CBR600RR", "years": list(range(2003, 2026)), "category": "Sport", "displacement": 599, "horsepower": 118, "price_base": 11999, "interest": 94},
        {"model": "CBR500R", "years": list(range(2013, 2026)), "category": "Sport", "displacement": 471, "horsepower": 47, "price_base": 6999, "interest": 86},
        {"model": "CBR300R", "years": list(range(2015, 2026)), "category": "Sport", "displacement": 286, "horsepower": 30, "price_base": 4599, "interest": 81},
        {"model": "CBR250R", "years": list(range(2011, 2026)), "category": "Sport", "displacement": 249, "horsepower": 26, "price_base": 4199, "interest": 79},
        {"model": "CBR650R", "years": list(range(2019, 2026)), "category": "Sport", "displacement": 649, "horsepower": 94, "price_base": 9199, "interest": 88},
        
        # CB Series (Naked/Standard)
        {"model": "CB1000R", "years": list(range(2018, 2026)), "category": "Naked", "displacement": 998, "horsepower": 143, "price_base": 12999, "interest": 90},
        {"model": "CB650R", "years": list(range(2019, 2026)), "category": "Naked", "displacement": 649, "horsepower": 94, "price_base": 8699, "interest": 87},
        {"model": "CB500F", "years": list(range(2013, 2026)), "category": "Naked", "displacement": 471, "horsepower": 47, "price_base": 6299, "interest": 84},
        {"model": "CB300R", "years": list(range(2018, 2026)), "category": "Naked", "displacement": 286, "horsepower": 31, "price_base": 4599, "interest": 82},
        {"model": "CB125R", "years": list(range(2018, 2026)), "category": "Naked", "displacement": 125, "horsepower": 15, "price_base": 3999, "interest": 75},
        
        # Classic CB Models
        {"model": "CB750", "years": list(range(2000, 2003)), "category": "Vintage", "displacement": 747, "horsepower": 68, "price_base": 45000, "interest": 92},
        {"model": "CB900F", "years": list(range(2000, 2007)), "category": "Standard", "displacement": 919, "horsepower": 109, "price_base": 8000, "interest": 78},
        {"model": "CB600F", "years": list(range(2000, 2013)), "category": "Standard", "displacement": 599, "horsepower": 102, "price_base": 7000, "interest": 80},
        
        # Adventure Series
        {"model": "Africa Twin", "years": list(range(2016, 2026)), "category": "Adventure", "displacement": 1084, "horsepower": 101, "price_base": 14399, "interest": 91},
        {"model": "CB500X", "years": list(range(2013, 2026)), "category": "Adventure", "displacement": 471, "horsepower": 47, "price_base": 6799, "interest": 85},
        
        # Touring
        {"model": "Gold Wing", "years": list(range(2001, 2026)), "category": "Touring", "displacement": 1833, "horsepower": 125, "price_base": 23800, "interest": 89},
        {"model": "ST1300", "years": list(range(2003, 2012)), "category": "Touring", "displacement": 1261, "horsepower": 125, "price_base": 15000, "interest": 76},
        
        # Cruiser
        {"model": "Shadow 1100", "years": list(range(2000, 2007)), "category": "Cruiser", "displacement": 1099, "horsepower": 60, "price_base": 8000, "interest": 74},
        {"model": "Shadow 750", "years": list(range(2000, 2014)), "category": "Cruiser", "displacement": 745, "horsepower": 45, "price_base": 7000, "interest": 72},
        {"model": "Fury", "years": list(range(2010, 2018)), "category": "Cruiser", "displacement": 1312, "horsepower": 87, "price_base": 11000, "interest": 77},
        {"model": "Rebel 500", "years": list(range(2017, 2026)), "category": "Cruiser", "displacement": 471, "horsepower": 47, "price_base": 6199, "interest": 86},
        {"model": "Rebel 300", "years": list(range(2017, 2026)), "category": "Cruiser", "displacement": 286, "horsepower": 27, "price_base": 4599, "interest": 83},
        {"model": "Rebel 1100", "years": list(range(2021, 2026)), "category": "Cruiser", "displacement": 1084, "horsepower": 87, "price_base": 9299, "interest": 88},
        
        # Scooter
        {"model": "PCX150", "years": list(range(2012, 2026)), "category": "Scooter", "displacement": 149, "horsepower": 14, "price_base": 3699, "interest": 79},
        {"model": "PCX125", "years": list(range(2010, 2026)), "category": "Scooter", "displacement": 125, "horsepower": 12, "price_base": 3599, "interest": 77}
    ]
    
    for model_data in honda_models:
        for year in model_data["years"]:
            price_variation = (year - 2000) * 180
            availability = "Available" if year >= 2020 else "Discontinued" if year >= 2015 else "Collector Item"
            
            if model_data["category"] == "Sport":
                image_url = SPORT_BIKE_IMAGES[hash(model_data["model"]) % len(SPORT_BIKE_IMAGES)]
            elif model_data["category"] == "Naked" or model_data["category"] == "Standard":
                image_url = NAKED_IMAGES[0]
            elif model_data["category"] == "Cruiser":
                image_url = CRUISER_IMAGES[hash(model_data["model"]) % len(CRUISER_IMAGES)]
            elif model_data["category"] == "Adventure":
                image_url = ADVENTURE_IMAGES[0]
            elif model_data["category"] == "Vintage":
                image_url = VINTAGE_IMAGES[0]
            else:
                image_url = SPORT_BIKE_IMAGES[0]
            
            motorcycle = {
                "manufacturer": "Honda",
                "model": model_data["model"],
                "year": year,
                "category": model_data["category"],
                "engine_type": "V4" if "Gold Wing" in model_data["model"] else "Inline-4" if model_data["displacement"] > 600 else "Parallel Twin" if model_data["displacement"] > 250 else "Single",
                "displacement": model_data["displacement"],
                "horsepower": model_data["horsepower"],
                "torque": int(model_data["horsepower"] * 0.8),
                "weight": 175 + (model_data["displacement"] // 10),
                "top_speed": int(115 + (model_data["horsepower"] * 1.3)),
                "fuel_capacity": 16.0 + (model_data["displacement"] // 150),
                "price_usd": model_data["price_base"] + price_variation,
                "availability": availability,
                "description": f"The Honda {model_data['model']} {year} exemplifies Honda's legendary reliability and engineering excellence. A perfect blend of performance, comfort, and dependability in the {model_data['category'].lower()} segment.",
                "image_url": image_url,
                "specialisations": ["Honda Reliability", "VTEC Technology", "Advanced Safety", "Fuel Efficiency", "Build Quality"],
                
                # Technical Features
                "mileage_kmpl": 40.0 if model_data["displacement"] < 200 else 30.0 if model_data["displacement"] < 500 else 22.0 if model_data["displacement"] < 1000 else 16.0,
                "transmission_type": "Manual" if model_data["category"] not in ["Scooter", "Automatic"] else "CVT",
                "number_of_gears": 6 if model_data["displacement"] > 500 else 5,
                "ground_clearance_mm": 155 if model_data["category"] == "Sport" else 175 if model_data["category"] in ["Naked", "Standard"] else 190,
                "seat_height_mm": 810 if model_data["category"] == "Sport" else 795 if model_data["category"] in ["Naked", "Standard"] else 770,
                "abs_available": year >= 2014,
                "braking_system": "Disc" if model_data["displacement"] > 125 else "Drum",
                "suspension_type": "USD Fork" if model_data["category"] == "Sport" and model_data["displacement"] > 600 else "Telescopic",
                "tyre_type": "Tubeless" if year >= 2012 else "Tube",
                "wheel_size_inches": "17" if model_data["displacement"] > 250 else "16",
                "headlight_type": "LED" if year >= 2017 else "Halogen",
                "fuel_type": "Petrol",
                
                "user_interest_score": model_data["interest"]
            }
            comprehensive_motorcycles.append(motorcycle)
    
    # KAWASAKI - Complete Model Range (2000-2025)
    kawasaki_models = [
        # Ninja Series (Sport)
        {"model": "Ninja H2", "years": list(range(2015, 2026)), "category": "Sport", "displacement": 998, "horsepower": 228, "price_base": 33000, "interest": 99},
        {"model": "Ninja ZX-10R", "years": list(range(2004, 2026)), "category": "Sport", "displacement": 998, "horsepower": 203, "price_base": 17399, "interest": 96},
        {"model": "Ninja ZX-6R", "years": list(range(2000, 2026)), "category": "Sport", "displacement": 636, "horsepower": 130, "price_base": 11199, "interest": 93},
        {"model": "Ninja 650", "years": list(range(2006, 2026)), "category": "Sport", "displacement": 649, "horsepower": 67, "price_base": 7399, "interest": 89},
        {"model": "Ninja 400", "years": list(range(2018, 2026)), "category": "Sport", "displacement": 399, "horsepower": 45, "price_base": 5299, "interest": 87},
        {"model": "Ninja 300", "years": list(range(2013, 2026)), "category": "Sport", "displacement": 296, "horsepower": 39, "price_base": 4999, "interest": 85},
        {"model": "Ninja 250", "years": list(range(2008, 2018)), "category": "Sport", "displacement": 249, "horsepower": 32, "price_base": 4199, "interest": 82},
        {"model": "Ninja ZX-14R", "years": list(range(2006, 2026)), "category": "Sport", "displacement": 1441, "horsepower": 208, "price_base": 16599, "interest": 94},
        
        # Z Series (Naked)
        {"model": "Z1000", "years": list(range(2003, 2026)), "category": "Naked", "displacement": 1043, "horsepower": 142, "price_base": 12699, "interest": 91},
        {"model": "Z900", "years": list(range(2017, 2026)), "category": "Naked", "displacement": 948, "horsepower": 125, "price_base": 9699, "interest": 93},
        {"model": "Z650", "years": list(range(2017, 2026)), "category": "Naked", "displacement": 649, "horsepower": 67, "price_base": 7399, "interest": 88},
        {"model": "Z400", "years": list(range(2019, 2026)), "category": "Naked", "displacement": 399, "horsepower": 45, "price_base": 5299, "interest": 86},
        {"model": "Z125", "years": list(range(2017, 2026)), "category": "Naked", "displacement": 125, "horsepower": 9, "price_base": 3199, "interest": 78},
        {"model": "Z800", "years": list(range(2013, 2017)), "category": "Naked", "displacement": 806, "horsepower": 113, "price_base": 8500, "interest": 84},
        
        # Adventure/Touring
        {"model": "Versys 1000", "years": list(range(2012, 2026)), "category": "Adventure", "displacement": 1043, "horsepower": 120, "price_base": 13399, "interest": 87},
        {"model": "Versys 650", "years": list(range(2007, 2026)), "category": "Adventure", "displacement": 649, "horsepower": 67, "price_base": 8599, "interest": 85},
        {"model": "Versys 300", "years": list(range(2017, 2026)), "category": "Adventure", "displacement": 296, "horsepower": 39, "price_base": 5599, "interest": 83},
        {"model": "Concours 14", "years": list(range(2008, 2026)), "category": "Touring", "displacement": 1352, "horsepower": 153, "price_base": 16699, "interest": 81},
        
        # Cruiser
        {"model": "Vulcan S", "years": list(range(2015, 2026)), "category": "Cruiser", "displacement": 649, "horsepower": 61, "price_base": 7399, "interest": 84},
        {"model": "Vulcan 900", "years": list(range(2006, 2017)), "category": "Cruiser", "displacement": 903, "horsepower": 50, "price_base": 8000, "interest": 76},
        {"model": "Vulcan 1700", "years": list(range(2009, 2019)), "category": "Cruiser", "displacement": 1700, "horsepower": 74, "price_base": 15000, "interest": 78},
        
        # Off-Road
        {"model": "KX450F", "years": list(range(2006, 2026)), "category": "Motocross", "displacement": 449, "horsepower": 54, "price_base": 9399, "interest": 85},
        {"model": "KLX300R", "years": list(range(2020, 2026)), "category": "Enduro", "displacement": 292, "horsepower": 30, "price_base": 5599, "interest": 81}
    ]
    
    for model_data in kawasaki_models:
        for year in model_data["years"]:
            price_variation = (year - 2000) * 220
            availability = "Available" if year >= 2020 else "Discontinued" if year >= 2015 else "Collector Item"
            
            if model_data["category"] == "Sport":
                image_url = SPORT_BIKE_IMAGES[hash(model_data["model"]) % len(SPORT_BIKE_IMAGES)]
            elif model_data["category"] == "Naked":
                image_url = NAKED_IMAGES[0]
            elif model_data["category"] == "Cruiser":
                image_url = CRUISER_IMAGES[hash(model_data["model"]) % len(CRUISER_IMAGES)]
            elif model_data["category"] == "Adventure" or model_data["category"] == "Touring":
                image_url = ADVENTURE_IMAGES[0]
            else:
                image_url = SPORT_BIKE_IMAGES[0]
            
            motorcycle = {
                "manufacturer": "Kawasaki",
                "model": model_data["model"],
                "year": year,
                "category": model_data["category"],
                "engine_type": "Supercharged Inline-4" if "H2" in model_data["model"] else "Inline-4" if model_data["displacement"] > 600 else "Parallel Twin" if model_data["displacement"] > 250 else "Single",
                "displacement": model_data["displacement"],
                "horsepower": model_data["horsepower"],
                "torque": int(model_data["horsepower"] * 0.77),
                "weight": 170 + (model_data["displacement"] // 8),
                "top_speed": int(125 + (model_data["horsepower"] * 1.4)),
                "fuel_capacity": 15.0 + (model_data["displacement"] // 120),
                "price_usd": model_data["price_base"] + price_variation,
                "availability": availability,
                "description": f"The Kawasaki {model_data['model']} {year} delivers Kawasaki's signature performance and aggressive styling. Engineered for riders who demand excitement and cutting-edge technology.",
                "image_url": image_url,
                "specialisations": ["Kawasaki Performance", "Aggressive Styling", "Advanced Electronics", "Track Ready", "Precision Engineering"],
                
                # Technical Features
                "mileage_kmpl": 32.0 if model_data["displacement"] < 200 else 20.0 if model_data["displacement"] < 500 else 16.0 if model_data["displacement"] < 1000 else 12.0,
                "transmission_type": "Manual" if model_data["category"] != "Scooter" else "CVT",
                "number_of_gears": 6 if model_data["displacement"] > 400 else 5,
                "ground_clearance_mm": 150 if model_data["category"] == "Sport" else 170 if model_data["category"] in ["Naked", "Standard"] else 195,
                "seat_height_mm": 830 if model_data["category"] == "Sport" else 805 if model_data["category"] in ["Naked", "Standard"] else 785,
                "abs_available": year >= 2013,
                "braking_system": "Disc" if model_data["displacement"] > 150 else "Drum",
                "suspension_type": "USD Fork" if model_data["category"] == "Sport" else "Telescopic",
                "tyre_type": "Tubeless" if year >= 2010 else "Tube",
                "wheel_size_inches": f"{'17' if model_data['displacement'] > 300 else '16'}",
                "headlight_type": "LED" if year >= 2016 else "Halogen",
                "fuel_type": "Petrol",
                
                "user_interest_score": model_data["interest"]
            }
            comprehensive_motorcycles.append(motorcycle)
    
    # SUZUKI - Complete Model Range (2000-2025)
    suzuki_models = [
        # GSX-R Series (Sport)
        {"model": "GSX-R1000", "years": list(range(2001, 2026)), "category": "Sport", "displacement": 999, "horsepower": 199, "price_base": 15799, "interest": 95},
        {"model": "GSX-R750", "years": list(range(2000, 2026)), "category": "Sport", "displacement": 749, "horsepower": 148, "price_base": 13199, "interest": 91},
        {"model": "GSX-R600", "years": list(range(2000, 2026)), "category": "Sport", "displacement": 599, "horsepower": 126, "price_base": 11799, "interest": 89},
        {"model": "GSX-R125", "years": list(range(2017, 2026)), "category": "Sport", "displacement": 124, "horsepower": 15, "price_base": 4399, "interest": 79},
        {"model": "Hayabusa", "years": list(range(1999, 2026)), "category": "Sport", "displacement": 1340, "horsepower": 187, "price_base": 18599, "interest": 97},
        
        # GSX-S Series (Naked)
        {"model": "GSX-S1000", "years": list(range(2015, 2026)), "category": "Naked", "displacement": 999, "horsepower": 152, "price_base": 11799, "interest": 90},
        {"model": "GSX-S750", "years": list(range(2017, 2026)), "category": "Naked", "displacement": 749, "horsepower": 114, "price_base": 8799, "interest": 87},
        {"model": "GSX-S125", "years": list(range(2017, 2026)), "category": "Naked", "displacement": 124, "horsepower": 15, "price_base": 3799, "interest": 76},
        
        # SV Series
        {"model": "SV650", "years": list(range(2000, 2026)), "category": "Standard", "displacement": 645, "horsepower": 75, "price_base": 7299, "interest": 88},
        {"model": "SV1000", "years": list(range(2003, 2007)), "category": "Standard", "displacement": 996, "horsepower": 120, "price_base": 9000, "interest": 82},
        
        # Adventure
        {"model": "V-Strom 1050", "years": list(range(2020, 2026)), "category": "Adventure", "displacement": 1037, "horsepower": 107, "price_base": 14699, "interest": 86},
        {"model": "V-Strom 1000", "years": list(range(2002, 2026)), "category": "Adventure", "displacement": 1037, "horsepower": 101, "price_base": 13199, "interest": 84},
        {"model": "V-Strom 650", "years": list(range(2004, 2026)), "category": "Adventure", "displacement": 645, "horsepower": 69, "price_base": 8799, "interest": 85},
        {"model": "V-Strom 250", "years": list(range(2017, 2026)), "category": "Adventure", "displacement": 248, "horsepower": 25, "price_base": 5499, "interest": 80},
        
        # Cruiser
        {"model": "Boulevard M109R", "years": list(range(2006, 2019)), "category": "Cruiser", "displacement": 1783, "horsepower": 123, "price_base": 14000, "interest": 83},
        {"model": "Boulevard C90", "years": list(range(2005, 2019)), "category": "Cruiser", "displacement": 1462, "horsepower": 72, "price_base": 12000, "interest": 75},
        {"model": "Boulevard C50", "years": list(range(2005, 2019)), "category": "Cruiser", "displacement": 805, "horsepower": 50, "price_base": 8000, "interest": 73}
    ]
    
    for model_data in suzuki_models:
        for year in model_data["years"]:
            price_variation = (year - 2000) * 190
            availability = "Available" if year >= 2020 else "Discontinued" if year >= 2015 else "Collector Item"
            
            if model_data["category"] == "Sport":
                image_url = SPORT_BIKE_IMAGES[hash(model_data["model"]) % len(SPORT_BIKE_IMAGES)]
            elif model_data["category"] == "Naked" or model_data["category"] == "Standard":
                image_url = NAKED_IMAGES[0]
            elif model_data["category"] == "Cruiser":
                image_url = CRUISER_IMAGES[hash(model_data["model"]) % len(CRUISER_IMAGES)]
            elif model_data["category"] == "Adventure":
                image_url = ADVENTURE_IMAGES[0]
            else:
                image_url = SPORT_BIKE_IMAGES[0]
            
            motorcycle = {
                "manufacturer": "Suzuki",
                "model": model_data["model"],
                "year": year,
                "category": model_data["category"],
                "engine_type": "Inline-4" if model_data["displacement"] > 700 else "V-Twin" if model_data["displacement"] > 600 else "Parallel Twin" if model_data["displacement"] > 200 else "Single",
                "displacement": model_data["displacement"],
                "horsepower": model_data["horsepower"],
                "torque": int(model_data["horsepower"] * 0.73),
                "weight": 165 + (model_data["displacement"] // 7),
                "top_speed": int(130 + (model_data["horsepower"] * 1.5)),
                "fuel_capacity": 16.0 + (model_data["displacement"] // 100),
                "price_usd": model_data["price_base"] + price_variation,
                "availability": availability,
                "description": f"The Suzuki {model_data['model']} {year} represents Suzuki's passion for performance and innovation. Known for exceptional handling, power delivery, and advanced technology.",
                "image_url": image_url,
                "specialisations": ["Suzuki Performance", "Lightweight Design", "Advanced Suspension", "Precise Handling", "Racing Heritage"],
                
                # Technical Features
                "mileage_kmpl": 34.0 if model_data["displacement"] < 200 else 22.0 if model_data["displacement"] < 500 else 17.0 if model_data["displacement"] < 1000 else 13.0,
                "transmission_type": "Manual" if model_data["category"] != "Scooter" else "CVT",
                "number_of_gears": 6 if model_data["displacement"] > 500 else 5,
                "ground_clearance_mm": 145 if model_data["category"] == "Sport" else 165 if model_data["category"] in ["Naked", "Standard"] else 185,
                "seat_height_mm": 825 if model_data["category"] == "Sport" else 800 if model_data["category"] in ["Naked", "Standard"] else 775,
                "abs_available": year >= 2014,
                "braking_system": "Disc" if model_data["displacement"] > 125 else "Drum",
                "suspension_type": "USD Fork" if model_data["category"] == "Sport" and model_data["displacement"] > 650 else "Telescopic",
                "tyre_type": "Tubeless" if year >= 2011 else "Tube",
                "wheel_size_inches": "17" if model_data["displacement"] > 250 else "16",
                "headlight_type": "LED" if year >= 2017 else "Halogen",
                "fuel_type": "Petrol",
                
                "user_interest_score": model_data["interest"]
            }
            comprehensive_motorcycles.append(motorcycle)
    
    # DUCATI - Complete Model Range (2000-2025)
    ducati_models = [
        # Panigale Series (Sport)
        {"model": "Panigale V4", "years": list(range(2018, 2026)), "category": "Sport", "displacement": 1103, "horsepower": 214, "price_base": 25995, "interest": 98},
        {"model": "Panigale V2", "years": list(range(2020, 2026)), "category": "Sport", "displacement": 955, "horsepower": 155, "price_base": 17295, "interest": 94},
        {"model": "Panigale 1299", "years": list(range(2015, 2018)), "category": "Sport", "displacement": 1285, "horsepower": 205, "price_base": 19000, "interest": 92},
        {"model": "Panigale 1199", "years": list(range(2012, 2015)), "category": "Sport", "displacement": 1198, "horsepower": 195, "price_base": 17500, "interest": 90},
        {"model": "Panigale 899", "years": list(range(2014, 2015)), "category": "Sport", "displacement": 898, "horsepower": 148, "price_base": 15000, "interest": 88},
        {"model": "Panigale 959", "years": list(range(2016, 2019)), "category": "Sport", "displacement": 955, "horsepower": 157, "price_base": 15500, "interest": 89},
        
        # SuperSport Series
        {"model": "SuperSport 950", "years": list(range(2021, 2026)), "category": "Sport", "displacement": 937, "horsepower": 110, "price_base": 13995, "interest": 85},
        {"model": "SuperSport", "years": list(range(2017, 2026)), "category": "Sport", "displacement": 937, "horsepower": 113, "price_base": 12995, "interest": 87},
        
        # Monster Series (Naked)
        {"model": "Monster 1200", "years": list(range(2014, 2021)), "category": "Naked", "displacement": 1198, "horsepower": 147, "price_base": 16000, "interest": 89},
        {"model": "Monster 821", "years": list(range(2014, 2020)), "category": "Naked", "displacement": 821, "horsepower": 109, "price_base": 12000, "interest": 86},
        {"model": "Monster 797", "years": list(range(2017, 2019)), "category": "Naked", "displacement": 803, "horsepower": 73, "price_base": 9500, "interest": 82},
        {"model": "Monster 696", "years": list(range(2008, 2014)), "category": "Naked", "displacement": 696, "horsepower": 80, "price_base": 8500, "interest": 80},
        {"model": "Monster 659", "years": list(range(2012, 2015)), "category": "Naked", "displacement": 659, "horsepower": 69, "price_base": 8000, "interest": 78},
        {"model": "Monster 1100", "years": list(range(2009, 2013)), "category": "Naked", "displacement": 1078, "horsepower": 100, "price_base": 12000, "interest": 84},
        {"model": "Monster+", "years": list(range(2021, 2026)), "category": "Naked", "displacement": 937, "horsepower": 111, "price_base": 11795, "interest": 91},
        
        # Streetfighter Series
        {"model": "Streetfighter V4", "years": list(range(2020, 2026)), "category": "Naked", "displacement": 1103, "horsepower": 208, "price_base": 20995, "interest": 95},
        {"model": "Streetfighter 848", "years": list(range(2012, 2015)), "category": "Naked", "displacement": 848, "horsepower": 132, "price_base": 14000, "interest": 87},
        
        # Multistrada Series (Adventure)
        {"model": "Multistrada V4", "years": list(range(2021, 2026)), "category": "Adventure", "displacement": 1158, "horsepower": 170, "price_base": 22995, "interest": 92},
        {"model": "Multistrada 1260", "years": list(range(2018, 2021)), "category": "Adventure", "displacement": 1262, "horsepower": 158, "price_base": 19000, "interest": 88},
        {"model": "Multistrada 950", "years": list(range(2017, 2021)), "category": "Adventure", "displacement": 937, "horsepower": 113, "price_base": 15000, "interest": 85},
        {"model": "Multistrada 1200", "years": list(range(2010, 2017)), "category": "Adventure", "displacement": 1198, "horsepower": 150, "price_base": 17000, "interest": 86},
        
        # Classic Models
        {"model": "748", "years": list(range(2000, 2003)), "category": "Sport", "displacement": 748, "horsepower": 103, "price_base": 35000, "interest": 85},
        {"model": "916", "years": list(range(2000, 2002)), "category": "Vintage", "displacement": 916, "horsepower": 114, "price_base": 45000, "interest": 93},
        {"model": "996", "years": list(range(2000, 2002)), "category": "Vintage", "displacement": 996, "horsepower": 123, "price_base": 40000, "interest": 91},
        {"model": "998", "years": list(range(2002, 2004)), "category": "Vintage", "displacement": 998, "horsepower": 136, "price_base": 42000, "interest": 92}
    ]
    
    for model_data in ducati_models:
        for year in model_data["years"]:
            price_variation = (year - 2000) * 300  # Ducati prices increase more
            availability = "Available" if year >= 2020 else "Discontinued" if year >= 2015 else "Collector Item"
            
            if model_data["category"] == "Sport":
                image_url = SPORT_BIKE_IMAGES[hash(model_data["model"]) % len(SPORT_BIKE_IMAGES)]
            elif model_data["category"] == "Naked":
                image_url = NAKED_IMAGES[0]
            elif model_data["category"] == "Adventure":
                image_url = ADVENTURE_IMAGES[0]
            elif model_data["category"] == "Vintage":
                image_url = VINTAGE_IMAGES[0]
            else:
                image_url = SPORT_BIKE_IMAGES[0]
            
            motorcycle = {
                "manufacturer": "Ducati",
                "model": model_data["model"],
                "year": year,
                "category": model_data["category"],
                "engine_type": "V4" if "V4" in model_data["model"] else "L-Twin" if model_data["displacement"] > 600 else "Single",
                "displacement": model_data["displacement"],
                "horsepower": model_data["horsepower"],
                "torque": int(model_data["horsepower"] * 0.85),
                "weight": 180 + (model_data["displacement"] // 12),
                "top_speed": int(140 + (model_data["horsepower"] * 1.3)),
                "fuel_capacity": 17.0 + (model_data["displacement"] // 150),
                "price_usd": model_data["price_base"] + price_variation,
                "availability": availability,
                "description": f"The Ducati {model_data['model']} {year} embodies Italian passion and engineering excellence. Features Ducati's signature L-Twin power delivery and racing-inspired design.",
                "image_url": image_url,
                "specialisations": ["Ducati Performance", "Italian Design", "L-Twin Power", "Racing Heritage", "Premium Components"],
                
                # Technical Features
                "mileage_kmpl": 28.0 if model_data["displacement"] < 200 else 18.0 if model_data["displacement"] < 500 else 14.0 if model_data["displacement"] < 1000 else 11.0,
                "transmission_type": "Manual" if model_data["category"] != "Scooter" else "CVT",
                "number_of_gears": 6 if model_data["displacement"] > 400 else 5,
                "ground_clearance_mm": 140 if model_data["category"] == "Sport" else 160 if model_data["category"] in ["Naked", "Standard"] else 180,
                "seat_height_mm": 840 if model_data["category"] == "Sport" else 815 if model_data["category"] in ["Naked", "Standard"] else 790,
                "abs_available": year >= 2012,
                "braking_system": "Disc" if model_data["displacement"] > 150 else "Drum",
                "suspension_type": "USD Fork" if model_data["category"] == "Sport" else "Telescopic",
                "tyre_type": "Tubeless" if year >= 2008 else "Tube",
                "wheel_size_inches": f"{'17' if model_data['displacement'] > 300 else '16'}",
                "headlight_type": "LED" if year >= 2015 else "Halogen",
                "fuel_type": "Petrol",
                
                "user_interest_score": model_data["interest"]
            }
            comprehensive_motorcycles.append(motorcycle)
    
    # Generate motorcycles for all new brands
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Bajaj", bajaj_models))
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Hero", hero_models))
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("TVS", tvs_models))
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Royal Enfield", royal_enfield_models))
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("KTM", ktm_models))
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Harley-Davidson", harley_models))
    
    # Add some additional missing manufacturers with sample models
    # CFMOTO
    cfmoto_models = [
        {"model": "300NK", "years": list(range(2018, 2026)), "category": "Naked", "displacement": 292, "horsepower": 29, "price_base": 4500, "interest": 82},
        {"model": "650NK", "years": list(range(2017, 2026)), "category": "Naked", "displacement": 649, "horsepower": 61, "price_base": 7200, "interest": 85},
        {"model": "300SR", "years": list(range(2019, 2026)), "category": "Sport", "displacement": 292, "horsepower": 29, "price_base": 5200, "interest": 84},
    ]
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("CFMOTO", cfmoto_models))
    
    # Keeway
    keeway_models = [
        {"model": "K-Light 202", "years": list(range(2020, 2026)), "category": "Naked", "displacement": 202, "horsepower": 20, "price_base": 3200, "interest": 78},
        {"model": "RKF 125", "years": list(range(2021, 2026)), "category": "Sport", "displacement": 124, "horsepower": 15, "price_base": 2800, "interest": 76},
    ]
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Keeway", keeway_models))
    
    # Lifan
    lifan_models = [
        {"model": "KP150", "years": list(range(2017, 2026)), "category": "Naked", "displacement": 150, "horsepower": 14, "price_base": 2200, "interest": 72},
        {"model": "KPR 200", "years": list(range(2018, 2026)), "category": "Sport", "displacement": 200, "horsepower": 22, "price_base": 2800, "interest": 75},
    ]
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Lifan", lifan_models))
    
    # GPX
    gpx_models = [
        {"model": "Demon 150", "years": list(range(2019, 2026)), "category": "Naked", "displacement": 150, "horsepower": 16, "price_base": 2500, "interest": 79},
        {"model": "Legend 250", "years": list(range(2020, 2026)), "category": "Cruiser", "displacement": 250, "horsepower": 25, "price_base": 3200, "interest": 81},
    ]
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("GPX", gpx_models))
    
    # QJ Motor
    qj_models = [
        {"model": "SRK 400", "years": list(range(2021, 2026)), "category": "Naked", "displacement": 400, "horsepower": 40, "price_base": 4800, "interest": 83},
        {"model": "SRV 300", "years": list(range(2020, 2026)), "category": "Adventure", "displacement": 300, "horsepower": 30, "price_base": 4200, "interest": 80},
    ]
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("QJ Motor", qj_models))
    
    # Vespa
    vespa_models = [
        {"model": "Primavera 150", "years": list(range(2014, 2026)), "category": "Scooter", "displacement": 150, "horsepower": 12, "price_base": 4500, "interest": 85},
        {"model": "GTS 300", "years": list(range(2008, 2026)), "category": "Scooter", "displacement": 278, "horsepower": 22, "price_base": 6500, "interest": 87},
        {"model": "Sprint 150", "years": list(range(2018, 2026)), "category": "Scooter", "displacement": 150, "horsepower": 12, "price_base": 4200, "interest": 82},
    ]
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Vespa", vespa_models))
    
    # Runner
    runner_models = [
        {"model": "Bullet 100", "years": list(range(2015, 2026)), "category": "Commuter", "displacement": 100, "horsepower": 8, "price_base": 1200, "interest": 70},
        {"model": "Knight Rider 165", "years": list(range(2018, 2026)), "category": "Naked", "displacement": 165, "horsepower": 15, "price_base": 1800, "interest": 74},
    ]
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Runner", runner_models))
    
    # Benelli
    benelli_models = [
        {"model": "302R", "years": list(range(2017, 2026)), "category": "Sport", "displacement": 300, "horsepower": 38, "price_base": 4800, "interest": 86},
        {"model": "TNT 300", "years": list(range(2015, 2026)), "category": "Naked", "displacement": 300, "horsepower": 38, "price_base": 4500, "interest": 84},
        {"model": "TRK 502", "years": list(range(2018, 2026)), "category": "Adventure", "displacement": 500, "horsepower": 47, "price_base": 6200, "interest": 88},
    ]
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Benelli", benelli_models))
    
    # Mahindra
    mahindra_models = [
        {"model": "Mojo", "years": list(range(2015, 2020)), "category": "Touring", "displacement": 295, "horsepower": 27, "price_base": 3800, "interest": 77},
        {"model": "Centuro", "years": list(range(2013, 2018)), "category": "Commuter", "displacement": 106, "horsepower": 8, "price_base": 1400, "interest": 69},
    ]
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Mahindra", mahindra_models))
    
    # Jawa
    jawa_models = [
        {"model": "Classic 300", "years": list(range(2018, 2026)), "category": "Cruiser", "displacement": 293, "horsepower": 27, "price_base": 3500, "interest": 89},
        {"model": "Forty Two", "years": list(range(2019, 2026)), "category": "Cruiser", "displacement": 293, "horsepower": 27, "price_base": 3300, "interest": 87},
        {"model": "Perak", "years": list(range(2020, 2026)), "category": "Bobber", "displacement": 334, "horsepower": 30, "price_base": 4200, "interest": 91},
    ]
    comprehensive_motorcycles.extend(generate_motorcycles_for_brand("Jawa", jawa_models))
    
    return comprehensive_motorcycles