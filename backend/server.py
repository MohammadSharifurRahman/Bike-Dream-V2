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

class SearchFilters(BaseModel):
    manufacturer: Optional[str] = None
    category: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    displacement_min: Optional[int] = None
    displacement_max: Optional[int] = None
    horsepower_min: Optional[int] = None
    horsepower_max: Optional[int] = None

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
    sort_by: Optional[str] = Query("year", description="Sort by: year, price, horsepower, model"),
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
        "price_range": price_range[0] if price_range else {"min_price": 1000, "max_price": 100000}
    }

@api_router.post("/motorcycles/seed")
async def seed_motorcycles():
    """Seed the database with sample motorcycle data"""
    sample_motorcycles = [
        {
            "manufacturer": "Harley-Davidson",
            "model": "Street Glide",
            "year": 2024,
            "category": "Touring",
            "engine_type": "V-Twin",
            "displacement": 1746,
            "horsepower": 87,
            "torque": 150,
            "weight": 365,
            "top_speed": 185,
            "fuel_capacity": 22.7,
            "price_usd": 22999,
            "availability": "Available",
            "description": "The Street Glide motorcycle is a modern classic with vintage soul. Features the iconic batwing fairing and premium touring amenities.",
            "image_url": "https://images.unsplash.com/photo-1479909013849-e16a7dd14323?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxtb3RvcmN5Y2xlc3xlbnwwfHx8fDE3NTM3MDYwODl8MA&ixlib=rb-4.1.0&q=85",
            "features": ["Batwing Fairing", "Premium Audio", "LED Lighting", "Cruise Control", "Anti-lock Braking System"]
        },
        {
            "manufacturer": "Yamaha",
            "model": "YZF-R6",
            "year": 2023,
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
            "description": "The YZF-R6 is a track-bred supersport motorcycle with race-proven technology and aggressive styling.",
            "image_url": "https://images.unsplash.com/photo-1609630875171-b1321377ee65?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxtb3RvcmN5Y2xlc3xlbnwwfHx8fDE3NTM3MDYwODl8MA&ixlib=rb-4.1.0&q=85",
            "features": ["Quick Shift System", "Traction Control", "ABS", "Ride Modes", "LED Headlight"]
        },
        {
            "manufacturer": "Royal Enfield",
            "model": "Continental GT 650",
            "year": 2024,
            "category": "Cafe Racer",
            "engine_type": "Parallel Twin",
            "displacement": 648,
            "horsepower": 47,
            "torque": 52,
            "weight": 198,
            "top_speed": 160,
            "fuel_capacity": 12.5,
            "price_usd": 5999,
            "availability": "Available",
            "description": "A modern classic cafe racer that pays homage to the golden era of motorcycling with contemporary reliability.",
            "image_url": "https://images.unsplash.com/photo-1645021081547-d7f3364ad974?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHw0fHxtb3RvcmN5Y2xlc3xlbnwwfHx8fDE3NTM3MDYwODl8MA&ixlib=rb-4.1.0&q=85",
            "features": ["Cafe Racer Styling", "Twin Cylinder Engine", "Dual Channel ABS", "USD Forks", "Classic Speedometer"]
        },
        {
            "manufacturer": "Indian",
            "model": "Scout Bobber",
            "year": 2024,
            "category": "Cruiser",
            "engine_type": "V-Twin",
            "displacement": 1133,
            "horsepower": 100,
            "torque": 98,
            "weight": 255,
            "top_speed": 180,
            "fuel_capacity": 12.5,
            "price_usd": 11999,
            "availability": "Available",
            "description": "The Scout Bobber combines authentic Indian Motorcycle style with modern performance and reliability.",
            "image_url": "https://images.pexels.com/photos/1413412/pexels-photo-1413412.jpeg",
            "features": ["Liquid-Cooled Engine", "ABS", "LED Lighting", "Keyless Ignition", "Ride Modes"]
        },
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
            "price_usd": 85000,
            "availability": "Collector Item",
            "description": "The legendary Vincent Black Shadow, once the world's fastest production motorcycle. A true collector's dream.",
            "image_url": "https://images.unsplash.com/photo-1634744632463-0da0f461fef7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwxfHx2aW50YWdlJTIwbW90b3JjeWNsZXxlbnwwfHx8fDE3NTM3MDYwOTd8MA&ixlib=rb-4.1.0&q=85",
            "features": ["Legendary Performance", "Iconic Design", "Historical Significance", "Collector Status", "Rare Find"]
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
            "price_usd": 35000,
            "availability": "Collector Item",
            "description": "Classic British motorcycle from the golden age. The Bonneville T120 defined the cafe racer era.",
            "image_url": "https://images.unsplash.com/photo-1611182150972-4094e06cba79?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwyfHx2aW50YWdlJTIwbW90b3JjeWNsZXxlbnwwfHx8fDE3NTM3MDYwOTd8MA&ixlib=rb-4.1.0&q=85",
            "features": ["Classic British Engineering", "Iconic Styling", "Vintage Appeal", "Collectible", "Cafe Racer Heritage"]
        },
        {
            "manufacturer": "BMW",
            "model": "R nineT",
            "year": 2023,
            "category": "Retro",
            "engine_type": "Boxer Twin",
            "displacement": 1170,
            "horsepower": 109,
            "torque": 116,
            "weight": 222,
            "top_speed": 200,
            "fuel_capacity": 17.0,
            "price_usd": 15695,
            "availability": "Available",
            "description": "The BMW R nineT blends classic BMW styling with modern technology and performance.",
            "image_url": "https://images.unsplash.com/photo-1592310294836-f654307931a4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Njl8MHwxfHNlYXJjaHwzfHx2aW50YWdlJTIwbW90b3JjeWNsZXxlbnwwfHx8fDE3NTM3MDYwOTd8MA&ixlib=rb-4.1.0&q=85",
            "features": ["Boxer Engine", "Retro Styling", "Modern Electronics", "ABS", "Premium Components"]
        },
        {
            "manufacturer": "Ducati",
            "model": "Panigale V4",
            "year": 2024,
            "category": "Sport",
            "engine_type": "V4",
            "displacement": 1103,
            "horsepower": 214,
            "torque": 124,
            "weight": 195,
            "top_speed": 300,
            "fuel_capacity": 16.0,
            "price_usd": 25995,
            "availability": "Available",
            "description": "The ultimate expression of Ducati's racing DNA. The Panigale V4 brings MotoGP technology to the street.",
            "image_url": "https://images.pexels.com/photos/1416169/pexels-photo-1416169.jpeg",
            "features": ["MotoGP Derived V4 Engine", "Ducati Traction Control", "Wheelie Control", "Cornering ABS", "Quick Shift"]
        },
        {
            "manufacturer": "Honda",
            "model": "CBR1000RR-R",
            "year": 2024,
            "category": "Sport",
            "engine_type": "Inline-4",
            "displacement": 999,
            "horsepower": 214,
            "torque": 113,
            "weight": 201,
            "top_speed": 299,
            "fuel_capacity": 16.1,
            "price_usd": 28500,
            "availability": "Available",
            "description": "Honda's most powerful and advanced superbike, developed with direct input from the HRC racing team.",
            "image_url": "https://images.unsplash.com/photo-1479909013849-e16a7dd14323?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxtb3RvcmN5Y2xlc3xlbnwwfHx8fDE3NTM3MDYwODl8MA&ixlib=rb-4.1.0&q=85",
            "features": ["Race-Derived Engine", "Ohlins Suspension", "Brembo Brakes", "Honda Selectable Torque Control", "Launch Control"]
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
            "description": "The world's only supercharged production motorcycle. Engineering excellence pushed to the extreme.",
            "image_url": "https://images.unsplash.com/photo-1609630875171-b1321377ee65?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwyfHxtb3RvcmN5Y2xlc3xlbnwwfHx8fDE3NTM3MDYwODl8MA&ixlib=rb-4.1.0&q=85",
            "features": ["Supercharged Engine", "Carbon Fiber Bodywork", "Launch Control", "Cornering Management", "Quick Shifter"]
        }
    ]
    
    # Clear existing data and insert new
    await db.motorcycles.delete_many({})
    
    motorcycles_to_insert = []
    for moto_data in sample_motorcycles:
        motorcycle_obj = Motorcycle(**moto_data)
        motorcycles_to_insert.append(motorcycle_obj.dict())
    
    await db.motorcycles.insert_many(motorcycles_to_insert)
    
    return {"message": f"Successfully seeded {len(sample_motorcycles)} motorcycles"}

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