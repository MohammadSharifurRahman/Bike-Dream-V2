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

    comprehensive_motorcycles = []
    
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
                "top_speed": 120 + (model_data["horsepower"] * 1.2),
                "fuel_capacity": 15.0 + (model_data["displacement"] // 100),
                "price_usd": model_data["price_base"] + price_variation,
                "availability": availability,
                "description": f"The Yamaha {model_data['model']} {year} represents Yamaha's commitment to performance and innovation in the {model_data['category'].lower()} category. Known for reliability, advanced engineering, and exceptional ride quality.",
                "image_url": image_url,
                "features": ["Yamaha Reliability", "Advanced Engineering", "Performance Oriented", "Quality Components", "Proven Design"],
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
                "top_speed": 115 + (model_data["horsepower"] * 1.3),
                "fuel_capacity": 16.0 + (model_data["displacement"] // 150),
                "price_usd": model_data["price_base"] + price_variation,
                "availability": availability,
                "description": f"The Honda {model_data['model']} {year} exemplifies Honda's legendary reliability and engineering excellence. A perfect blend of performance, comfort, and dependability in the {model_data['category'].lower()} segment.",
                "image_url": image_url,
                "features": ["Honda Reliability", "VTEC Technology", "Advanced Safety", "Fuel Efficiency", "Build Quality"],
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
                "top_speed": 125 + (model_data["horsepower"] * 1.4),
                "fuel_capacity": 15.0 + (model_data["displacement"] // 120),
                "price_usd": model_data["price_base"] + price_variation,
                "availability": availability,
                "description": f"The Kawasaki {model_data['model']} {year} delivers Kawasaki's signature performance and aggressive styling. Engineered for riders who demand excitement and cutting-edge technology.",
                "image_url": image_url,
                "features": ["Kawasaki Performance", "Aggressive Styling", "Advanced Electronics", "Track Ready", "Precision Engineering"],
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
                "top_speed": 130 + (model_data["horsepower"] * 1.5),
                "fuel_capacity": 16.0 + (model_data["displacement"] // 100),
                "price_usd": model_data["price_base"] + price_variation,
                "availability": availability,
                "description": f"The Suzuki {model_data['model']} {year} represents Suzuki's passion for performance and innovation. Known for exceptional handling, power delivery, and advanced technology.",
                "image_url": image_url,
                "features": ["Suzuki Performance", "Lightweight Design", "Advanced Suspension", "Precise Handling", "Racing Heritage"],
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
                "top_speed": 140 + (model_data["horsepower"] * 1.3),
                "fuel_capacity": 17.0 + (model_data["displacement"] // 150),
                "price_usd": model_data["price_base"] + price_variation,
                "availability": availability,
                "description": f"The Ducati {model_data['model']} {year} embodies Italian passion and engineering excellence. Features Ducati's signature L-Twin power delivery and racing-inspired design.",
                "image_url": image_url,
                "features": ["Ducati Performance", "Italian Design", "L-Twin Power", "Racing Heritage", "Premium Components"],
                "user_interest_score": model_data["interest"]
            }
            comprehensive_motorcycles.append(motorcycle)
    
    return comprehensive_motorcycles