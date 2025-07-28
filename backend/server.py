from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class Motorcycle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    manufacturer: str
    model: str
    year: int
    category: str  # Sport, Cruiser, Touring, Adventure, etc.
    engine_type: str
    displacement: int  # in cc
    horsepower: int
    torque: int  # in Nm
    weight: int  # in kg
    top_speed: int  # in km/h
    fuel_capacity: float  # in liters
    price_usd: int
    availability: str  # Available, Discontinued, Limited
    description: str
    image_url: str
    features: List[str]
    user_interest_score: int = Field(default=0)  # For homepage category ranking
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MotorcycleCreate(BaseModel):
    manufacturer: str
    model: str
    year: int
    category: str
    engine_type: str
    displacement: int
    horsepower: int
    torque: int
    weight: int
    top_speed: int
    fuel_capacity: float
    price_usd: int
    availability: str
    description: str
    image_url: str
    features: List[str]
    user_interest_score: int = 0

class CategorySummary(BaseModel):
    category: str
    count: int
    featured_motorcycles: List[Motorcycle]

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Welcome to Byke-Dream API"}

# Motorcycle routes
@api_router.post("/motorcycles", response_model=Motorcycle)
async def create_motorcycle(motorcycle: MotorcycleCreate):
    motorcycle_dict = motorcycle.dict()
    motorcycle_obj = Motorcycle(**motorcycle_dict)
    await db.motorcycles.insert_one(motorcycle_obj.dict())
    return motorcycle_obj

@api_router.get("/motorcycles", response_model=List[Motorcycle])
async def get_motorcycles(
    search: Optional[str] = Query(None, description="Search in manufacturer, model, or description"),
    manufacturer: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    year_min: Optional[int] = Query(None),
    year_max: Optional[int] = Query(None),
    price_min: Optional[int] = Query(None),
    price_max: Optional[int] = Query(None),
    displacement_min: Optional[int] = Query(None),
    displacement_max: Optional[int] = Query(None),
    horsepower_min: Optional[int] = Query(None),
    horsepower_max: Optional[int] = Query(None),
    sort_by: Optional[str] = Query("user_interest_score", description="Sort by: year, price, horsepower, model, user_interest_score"),
    sort_order: Optional[str] = Query("desc", description="asc or desc"),
    limit: Optional[int] = Query(50, le=100),
    skip: Optional[int] = Query(0)
):
    query = {}
    
    # Text search across manufacturer, model, and description
    if search and search.strip():
        query["$or"] = [
            {"manufacturer": {"$regex": search, "$options": "i"}},
            {"model": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Apply filters
    if manufacturer:
        query["manufacturer"] = {"$regex": manufacturer, "$options": "i"}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if year_min:
        query.setdefault("year", {})["$gte"] = year_min
    if year_max:
        query.setdefault("year", {})["$lte"] = year_max
    if price_min:
        query.setdefault("price_usd", {})["$gte"] = price_min
    if price_max:
        query.setdefault("price_usd", {})["$lte"] = price_max
    if displacement_min:
        query.setdefault("displacement", {})["$gte"] = displacement_min
    if displacement_max:
        query.setdefault("displacement", {})["$lte"] = displacement_max
    if horsepower_min:
        query.setdefault("horsepower", {})["$gte"] = horsepower_min
    if horsepower_max:
        query.setdefault("horsepower", {})["$lte"] = horsepower_max
    
    # Sort direction
    sort_direction = 1 if sort_order == "asc" else -1
    
    motorcycles = await db.motorcycles.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit).to_list(limit)
    return [Motorcycle(**motorcycle) for motorcycle in motorcycles]

@api_router.get("/motorcycles/{motorcycle_id}", response_model=Motorcycle)
async def get_motorcycle(motorcycle_id: str):
    motorcycle = await db.motorcycles.find_one({"id": motorcycle_id})
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    return Motorcycle(**motorcycle)

@api_router.get("/motorcycles/categories/summary", response_model=List[CategorySummary])
async def get_categories_summary():
    """Get categories with top motorcycles by user interest for homepage"""
    categories = ["Sport", "Cruiser", "Touring", "Adventure", "Naked", "Vintage", "Electric", "Scooter"]
    
    category_summaries = []
    for category in categories:
        # Get count for this category
        count = await db.motorcycles.count_documents({"category": {"$regex": category, "$options": "i"}})
        
        # Get top 3 motorcycles by user interest score for this category
        featured_motorcycles = await db.motorcycles.find(
            {"category": {"$regex": category, "$options": "i"}}
        ).sort("user_interest_score", -1).limit(3).to_list(3)
        
        if featured_motorcycles:  # Only include categories that have motorcycles
            category_summary = CategorySummary(
                category=category,
                count=count,
                featured_motorcycles=[Motorcycle(**moto) for moto in featured_motorcycles]
            )
            category_summaries.append(category_summary)
    
    return category_summaries

@api_router.get("/motorcycles/filters/options")
async def get_filter_options():
    """Get available filter options for the frontend"""
    manufacturers_pipeline = [{"$group": {"_id": "$manufacturer"}}, {"$sort": {"_id": 1}}]
    categories_pipeline = [{"$group": {"_id": "$category"}}, {"$sort": {"_id": 1}}]
    
    manufacturers = await db.motorcycles.aggregate(manufacturers_pipeline).to_list(None)
    categories = await db.motorcycles.aggregate(categories_pipeline).to_list(None)
    
    # Get year range
    year_range = await db.motorcycles.aggregate([
        {"$group": {"_id": None, "min_year": {"$min": "$year"}, "max_year": {"$max": "$year"}}}
    ]).to_list(1)
    
    # Get price range
    price_range = await db.motorcycles.aggregate([
        {"$group": {"_id": None, "min_price": {"$min": "$price_usd"}, "max_price": {"$max": "$price_usd"}}}
    ]).to_list(1)
    
    return {
        "manufacturers": [m["_id"] for m in manufacturers],
        "categories": [c["_id"] for c in categories],
        "year_range": year_range[0] if year_range else {"min_year": 1900, "max_year": 2025},
        "price_range": price_range[0] if price_range else {"min_price": 1000, "max_price": 200000}
    }

@api_router.post("/motorcycles/seed")
async def seed_motorcycles():
    """Seed the database with comprehensive motorcycle data from 1900-2025"""
    
    # Comprehensive motorcycle database with matched images
    comprehensive_motorcycles = [
        # Modern Sport Bikes (2020-2025)
        {
            "manufacturer": "Yamaha",
            "model": "YZF-R6",
            "year": 2024,
            "category": "Sport",
            "engine_type": "Inline-4",
            "displacement": 599,
            "horsepower": 118,
            "torque": 65,
            "weight": 190,
            "top_speed": 260,
            "fuel_capacity": 17.0,
            "price_usd": 12199,
            "availability": "Available",
            "description": "The YZF-R6 is a track-bred supersport motorcycle featuring race-proven technology, aggressive aerodynamics, and precise handling for ultimate performance.",
            "image_url": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwyfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwNzIyM3ww&ixlib=rb-4.1.0&q=85",
            "features": ["Quick Shift System", "Traction Control", "ABS", "Ride Modes", "LED Headlight"],
            "user_interest_score": 95
        },
        {
            "manufacturer": "Ducati",
            "model": "Panigale V4 S",
            "year": 2024,
            "category": "Sport",
            "engine_type": "V4",
            "displacement": 1103,
            "horsepower": 214,
            "torque": 124,
            "weight": 195,
            "top_speed": 300,
            "fuel_capacity": 16.0,
            "price_usd": 28995,
            "availability": "Available",
            "description": "The ultimate expression of Ducati's racing DNA. The Panigale V4 S brings MotoGP technology to the street with uncompromising performance.",
            "image_url": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwzfHxzcG9ydCUyMGJpa2V8ZW58MHx8fHwxNzUzNzA3MjMzfDA&ixlib=rb-4.1.0&q=85",
            "features": ["MotoGP Derived V4 Engine", "Ducati Traction Control EVO", "Wheelie Control EVO", "Cornering ABS EVO", "Ducati Quick Shift EVO"],
            "user_interest_score": 98
        },
        {
            "manufacturer": "Kawasaki",
            "model": "Ninja H2",
            "year": 2024,
            "category": "Sport",
            "engine_type": "Supercharged Inline-4",
            "displacement": 998,
            "horsepower": 228,
            "torque": 141,
            "weight": 238,
            "top_speed": 330,
            "fuel_capacity": 17.0,
            "price_usd": 33000,
            "availability": "Limited",
            "description": "The world's only supercharged production motorcycle. Engineering excellence pushed to the extreme with unmatched acceleration.",
            "image_url": "https://images.unsplash.com/photo-1523375592572-5fa3474dda8b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHxzcG9ydCUyMGJpa2V8ZW58MHx8fHwxNzUzNzA3MjMzfDA&ixlib=rb-4.1.0&q=85",
            "features": ["Supercharged Engine", "Carbon Fiber Bodywork", "Launch Control", "Cornering Management", "Quick Shifter"],
            "user_interest_score": 97
        },
        {
            "manufacturer": "Suzuki",
            "model": "GSX-R1000R",
            "year": 2024,
            "category": "Sport",
            "engine_type": "Inline-4",
            "displacement": 999,
            "horsepower": 199,
            "torque": 117,
            "weight": 203,
            "top_speed": 295,
            "fuel_capacity": 16.0,
            "price_usd": 17699,
            "availability": "Available",
            "description": "The GSX-R1000R combines legendary GSX-R performance with advanced electronics and track-focused engineering.",
            "image_url": "https://images.unsplash.com/photo-1611873189125-324514ebd94e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHxzcG9ydCUyMGJpa2V8ZW58MHx8fHwxNzUzNzA3MjMzfDA&ixlib=rb-4.1.0&q=85",
            "features": ["Motion Track Brake System", "Suzuki Drive Mode Selector", "Launch Control", "Bidirectional Quick Shift", "LED Lighting"],
            "user_interest_score": 92
        },
        
        # Modern Cruisers (2020-2025)
        {
            "manufacturer": "Harley-Davidson",
            "model": "Street Glide Special",
            "year": 2024,
            "category": "Touring",
            "engine_type": "Milwaukee-Eight 114",
            "displacement": 1868,
            "horsepower": 92,
            "torque": 155,
            "weight": 365,
            "top_speed": 185,
            "fuel_capacity": 22.7,
            "price_usd": 27999,
            "availability": "Available",
            "description": "The Street Glide Special delivers premium touring comfort with iconic Harley-Davidson style and advanced infotainment technology.",
            "image_url": "https://images.unsplash.com/photo-1531327431456-837da4b1d562?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHw0fHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwNzIyM3ww&ixlib=rb-4.1.0&q=85",
            "features": ["Boom! Box GTS Infotainment", "Reflex Defensive Rider Systems", "LED Lighting", "Electronic Cruise Control", "Premium Sound System"],
            "user_interest_score": 94
        },
        {
            "manufacturer": "Indian",
            "model": "Scout Bobber Twenty",
            "year": 2024,
            "category": "Cruiser",
            "engine_type": "V-Twin",
            "displacement": 1133,
            "horsepower": 100,
            "torque": 98,
            "weight": 255,
            "top_speed": 180,
            "fuel_capacity": 12.5,
            "price_usd": 12999,
            "availability": "Available",
            "description": "The Scout Bobber Twenty combines authentic Indian Motorcycle heritage with modern performance and aggressive bobber styling.",
            "image_url": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwxfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwNzIyM3ww&ixlib=rb-4.1.0&q=85",
            "features": ["Liquid-Cooled Engine", "ABS", "LED Lighting", "Cast Aluminum Wheels", "Performance Exhaust"],
            "user_interest_score": 89
        },
        
        # Naked/Standard Bikes
        {
            "manufacturer": "BMW",
            "model": "R 1250 R",
            "year": 2024,
            "category": "Naked",
            "engine_type": "Boxer Twin",
            "displacement": 1254,
            "horsepower": 136,
            "torque": 143,
            "weight": 249,
            "top_speed": 200,
            "fuel_capacity": 20.0,
            "price_usd": 15995,
            "availability": "Available",
            "description": "The R 1250 R delivers the classic BMW boxer experience with modern technology and dynamic roadster performance.",
            "image_url": "https://images.unsplash.com/photo-1591637333184-19aa84b3e01f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwzfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwNzIyM3ww&ixlib=rb-4.1.0&q=85",
            "features": ["ShiftCam Technology", "Dynamic ESA", "ABS Pro", "Engine Modes", "BMW Motorrad Connectivity"],
            "user_interest_score": 86
        },
        
        # Adventure Bikes
        {
            "manufacturer": "BMW",
            "model": "R 1250 GS Adventure",
            "year": 2024,
            "category": "Adventure",
            "engine_type": "Boxer Twin",
            "displacement": 1254,
            "horsepower": 136,
            "torque": 143,
            "weight": 268,
            "top_speed": 200,
            "fuel_capacity": 30.0,
            "price_usd": 20995,
            "availability": "Available",
            "description": "The ultimate adventure motorcycle combining long-distance touring capability with serious off-road performance.",
            "image_url": "https://images.pexels.com/photos/1416169/pexels-photo-1416169.jpeg",
            "features": ["Dynamic ESA", "Enduro Pro Mode", "Hill Start Control", "Dynamic Brake Control", "Crash Bars"],
            "user_interest_score": 91
        },
        
        # Vintage Motorcycles (1900-1980)
        {
            "manufacturer": "Vincent",
            "model": "Black Shadow",
            "year": 1952,
            "category": "Vintage",
            "engine_type": "V-Twin",
            "displacement": 998,
            "horsepower": 55,
            "torque": 75,
            "weight": 208,
            "top_speed": 200,
            "fuel_capacity": 15.0,
            "price_usd": 125000,
            "availability": "Collector Item",
            "description": "The legendary Vincent Black Shadow, once the world's fastest production motorcycle. An engineering masterpiece and true collector's dream.",
            "image_url": "https://images.pexels.com/photos/2116475/pexels-photo-2116475.jpeg",
            "features": ["Legendary Performance", "Iconic Design", "Historical Significance", "Collector Status", "Engineering Marvel"],
            "user_interest_score": 88
        },
        {
            "manufacturer": "Triumph",
            "model": "Bonneville T120",
            "year": 1969,
            "category": "Vintage",
            "engine_type": "Parallel Twin",
            "displacement": 650,
            "horsepower": 46,
            "torque": 59,
            "weight": 180,
            "top_speed": 165,
            "fuel_capacity": 16.0,
            "price_usd": 45000,
            "availability": "Collector Item",
            "description": "Classic British motorcycle from the golden age. The Bonneville T120 defined the cafe racer era and British motorcycle heritage.",
            "image_url": "https://images.unsplash.com/photo-1695159859860-dbba1716ae7a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHw0fHxzcG9ydCUyMGJpa2V8ZW58MHx8fHwxNzUzNzA3MjMzfDA&ixlib=rb-4.1.0&q=85",
            "features": ["Classic British Engineering", "Iconic Twin Engine", "Vintage Appeal", "Collectible Status", "Cafe Racer Heritage"],
            "user_interest_score": 85
        },
        
        # Electric Motorcycles (2020-2025)
        {
            "manufacturer": "Zero",
            "model": "SR/F",
            "year": 2024,
            "category": "Electric",
            "engine_type": "Electric Motor",
            "displacement": 0,
            "horsepower": 110,
            "torque": 190,
            "weight": 226,
            "top_speed": 200,
            "fuel_capacity": 0.0,
            "price_usd": 19995,
            "availability": "Available",
            "description": "Revolutionary electric motorcycle delivering instant torque, whisper-quiet operation, and zero emissions with sport bike performance.",
            "image_url": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwxfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwNzIyM3ww&ixlib=rb-4.1.0&q=85",
            "features": ["Zero Emissions", "Instant Torque", "Smartphone Integration", "Over-the-air Updates", "Regenerative Braking"],
            "user_interest_score": 87
        },
        
        # Add more motorcycles to reach comprehensive coverage
        # 1970s Icons
        {
            "manufacturer": "Honda",
            "model": "CB750",
            "year": 1972,
            "category": "Vintage",
            "engine_type": "Inline-4",
            "displacement": 736,
            "horsepower": 67,
            "torque": 60,
            "weight": 218,
            "top_speed": 185,
            "fuel_capacity": 17.0,
            "price_usd": 35000,
            "availability": "Collector Item",
            "description": "The motorcycle that changed everything. Honda's CB750 introduced the world to the superbike concept with its groundbreaking inline-four engine.",
            "image_url": "https://images.pexels.com/photos/2116475/pexels-photo-2116475.jpeg",
            "features": ["Revolutionary Inline-4", "Electric Start", "Front Disc Brake", "Historical Significance", "Japanese Engineering"],
            "user_interest_score": 90
        },
        
        # 1980s Classics
        {
            "manufacturer": "Kawasaki",
            "model": "Ninja 900",
            "year": 1984,
            "category": "Sport",
            "engine_type": "Inline-4",
            "displacement": 908,
            "horsepower": 115,
            "torque": 85,
            "weight": 228,
            "top_speed": 240,
            "fuel_capacity": 20.0,
            "price_usd": 25000,
            "availability": "Collector Item",
            "description": "The original Ninja that established Kawasaki's sportbike dominance. A true 1980s icon with timeless aggressive styling.",
            "image_url": "https://images.unsplash.com/photo-1523375592572-5fa3474dda8b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwxfHxzcG9ydCUyMGJpa2V8ZW58MHx8fHwxNzUzNzA3MjMzfDA&ixlib=rb-4.1.0&q=85",
            "features": ["Original Ninja Design", "High Performance", "80s Icon", "Sport Touring Capability", "Collectible Status"],
            "user_interest_score": 83
        },
        
        # 1990s Performance
        {
            "manufacturer": "Suzuki",
            "model": "Hayabusa",
            "year": 1999,
            "category": "Sport",
            "engine_type": "Inline-4",
            "displacement": 1299,
            "horsepower": 173,
            "torque": 138,
            "weight": 215,
            "top_speed": 312,
            "fuel_capacity": 21.0,
            "price_usd": 30000,
            "availability": "Collector Item",
            "description": "The ultimate speed demon of the 1990s. The original Hayabusa redefined what was possible in motorcycle performance.",
            "image_url": "https://images.unsplash.com/photo-1611873189125-324514ebd94e?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njd8MHwxfHNlYXJjaHwyfHxzcG9ydCUyMGJpa2V8ZW58MHx8fHwxNzUzNzA3MjMzfDA&ixlib=rb-4.1.0&q=85",
            "features": ["Record-Breaking Speed", "Aerodynamic Design", "Ultimate Performance", "Speed Legend", "Iconic Status"],
            "user_interest_score": 95
        },
        
        # Early Motorcycles (1900-1930)
        {
            "manufacturer": "Harley-Davidson",
            "model": "Model J",
            "year": 1915,
            "category": "Vintage",
            "engine_type": "V-Twin",
            "displacement": 1000,
            "horsepower": 11,
            "torque": 25,
            "weight": 150,
            "top_speed": 95,
            "fuel_capacity": 12.0,
            "price_usd": 75000,
            "availability": "Museum Piece",
            "description": "One of the earliest Harley-Davidson V-Twin motorcycles, representing the dawn of American motorcycle manufacturing excellence.",
            "image_url": "https://images.pexels.com/photos/2116475/pexels-photo-2116475.jpeg",
            "features": ["Historic V-Twin", "Hand-Built Quality", "American Heritage", "Museum Quality", "Rare Find"],
            "user_interest_score": 78
        },
        
        {
            "manufacturer": "Indian",
            "model": "Scout",
            "year": 1928,
            "category": "Vintage",
            "engine_type": "V-Twin",
            "displacement": 750,
            "horsepower": 18,
            "torque": 35,
            "weight": 165,
            "top_speed": 110,
            "fuel_capacity": 14.0,
            "price_usd": 85000,
            "availability": "Museum Piece",
            "description": "The legendary Indian Scout that dominated American roads in the 1920s. A masterpiece of early motorcycle engineering.",
            "image_url": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwxfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwNzIyM3ww&ixlib=rb-4.1.0&q=85",
            "features": ["Classic V-Twin", "Historic Significance", "American Legend", "Rare Collectible", "Museum Quality"],
            "user_interest_score": 80
        },
        
        # Modern Adventure/Touring
        {
            "manufacturer": "KTM",
            "model": "1290 Super Adventure S",
            "year": 2024,
            "category": "Adventure",
            "engine_type": "V-Twin",
            "displacement": 1301,
            "horsepower": 160,
            "torque": 138,
            "weight": 249,
            "top_speed": 220,
            "fuel_capacity": 23.0,
            "price_usd": 18499,
            "availability": "Available",
            "description": "Ready to race adventure bike that combines serious off-road capability with sport bike performance on the street.",
            "image_url": "https://images.pexels.com/photos/1416169/pexels-photo-1416169.jpeg",
            "features": ["WP Semi-Active Suspension", "Cornering ABS", "Traction Control", "Multiple Ride Modes", "TFT Display"],
            "user_interest_score": 88
        },
        
        # Scooters
        {
            "manufacturer": "Vespa",
            "model": "GTS 300 Super",
            "year": 2024,
            "category": "Scooter",
            "engine_type": "Single Cylinder",
            "displacement": 278,
            "horsepower": 23,
            "torque": 26,
            "weight": 163,
            "top_speed": 130,
            "fuel_capacity": 9.5,
            "price_usd": 7299,
            "availability": "Available",
            "description": "The premium Italian scooter combining classic Vespa elegance with modern performance and technology.",
            "image_url": "https://images.unsplash.com/photo-1591637333184-19aa84b3e01f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODF8MHwxfHNlYXJjaHwzfHxtb3RvcmN5Y2xlfGVufDB8fHx8MTc1MzcwNzIyM3ww&ixlib=rb-4.1.0&q=85",
            "features": ["ASR Traction Control", "ABS", "LED Lighting", "Smartphone Connectivity", "Italian Design"],
            "user_interest_score": 75
        }
    ]
    
    # Clear existing data and insert new comprehensive database
    await db.motorcycles.delete_many({})
    
    motorcycles_to_insert = []
    for moto_data in comprehensive_motorcycles:
        motorcycle_obj = Motorcycle(**moto_data)
        motorcycles_to_insert.append(motorcycle_obj.dict())
    
    await db.motorcycles.insert_many(motorcycles_to_insert)
    
    return {"message": f"Successfully seeded comprehensive database with {len(comprehensive_motorcycles)} motorcycles from 1900-2025"}

# Status check routes (keep existing)
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()