import bcrypt
from fastapi import FastAPI, APIRouter, HTTPException, Query, BackgroundTasks, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from comprehensive_motorcycles import get_comprehensive_motorcycle_data
from daily_update_bot import run_daily_update_job
from vendor_pricing import vendor_pricing
import asyncio
import aiohttp
import schedule
import threading
import time
import random


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

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    picture: str = Field(default="")
    session_token: Optional[str] = None
    password_hash: Optional[str] = None  # For email/password auth
    google_id: Optional[str] = None      # For Google OAuth
    auth_method: str = Field(default="password")  # "password" or "google" or "emergent"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    favorite_motorcycles: List[str] = Field(default_factory=list)

class UserCreate(BaseModel):
    email: str
    name: str
    picture: str
    session_token: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleOAuthData(BaseModel):
    email: str
    name: str
    picture: str
    google_id: str

class Rating(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    motorcycle_id: str
    rating: int = Field(ge=1, le=5)  # 1-5 stars
    review_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RatingCreate(BaseModel):
    motorcycle_id: str
    rating: int = Field(ge=1, le=5)
    review_text: Optional[str] = None

class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    motorcycle_id: str
    user_id: str
    user_name: str
    user_picture: str = Field(default="")
    content: str
    parent_comment_id: Optional[str] = None  # For replies
    is_flagged: bool = Field(default=False)
    likes_count: int = Field(default=0)
    replies_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class CommentCreate(BaseModel):
    motorcycle_id: str
    content: str
    parent_comment_id: Optional[str] = None

class CommentLike(BaseModel):
    comment_id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommentWithUser(BaseModel):
    id: str
    user_id: str
    user_name: str
    user_picture: str
    motorcycle_id: str
    comment_text: str
    parent_comment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    likes: int
    replies: List['CommentWithUser'] = Field(default_factory=list)

class VendorPrice(BaseModel):
    vendor_name: str
    price: float
    currency: str
    price_usd: float
    availability: str
    special_offer: Optional[str] = None
    rating: float
    reviews_count: int
    shipping: str
    estimated_delivery: str
    website_url: str
    phone: Optional[str] = None

class MotorcycleFeatures(BaseModel):
    # Technical Features
    engine_capacity_cc: int = Field(alias="displacement")  # Engine capacity (cc)
    mileage_kmpl: float  # Mileage (kmpl)
    top_speed_kmh: int = Field(alias="top_speed")  # Top speed (km/h)
    engine_type: str  # Engine type
    torque_nm: int = Field(alias="torque")  # Torque (Nm)
    horsepower_bhp: int = Field(alias="horsepower")  # Horsepower (bhp)
    fuel_tank_capacity_l: float = Field(alias="fuel_capacity")  # Fuel tank capacity (L)
    transmission_type: str  # Manual/Automatic/CVT
    number_of_gears: int  # Number of gears
    weight_kg: int = Field(alias="weight")  # Weight (kg)
    ground_clearance_mm: int  # Ground clearance (mm)
    seat_height_mm: int  # Seat height (mm)
    abs_available: bool  # ABS (Anti-lock Braking System)
    braking_system: str  # Disc/Drum/Combination
    suspension_type: str  # Telescopic/USD/Mono-shock
    tyre_type: str  # Tubeless/Tube
    wheel_size_inches: str  # Wheel size (inches)
    headlight_type: str  # LED/Halogen
    fuel_type: str  # Petrol/Electric/Hybrid

class Motorcycle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    manufacturer: str
    model: str
    year: int
    category: str  # Sport, Cruiser, Touring, Adventure, etc.
    engine_type: str
    displacement: int  # in cc (same as engine_capacity_cc)
    horsepower: int
    torque: int  # in Nm
    weight: int  # in kg
    top_speed: int  # in km/h
    fuel_capacity: float  # in liters
    price_usd: int
    availability: str  # Available, Discontinued, Limited
    description: str
    image_url: str
    specialisations: List[str] = Field(default_factory=list)  # Renamed from features
    
    # Technical Features
    mileage_kmpl: float = Field(default=25.0)
    transmission_type: str = Field(default="Manual")
    number_of_gears: int = Field(default=6)
    ground_clearance_mm: int = Field(default=180)
    seat_height_mm: int = Field(default=800)
    abs_available: bool = Field(default=True)
    braking_system: str = Field(default="Disc")
    suspension_type: str = Field(default="Telescopic")
    tyre_type: str = Field(default="Tubeless")
    wheel_size_inches: str = Field(default="17")
    headlight_type: str = Field(default="LED")
    fuel_type: str = Field(default="Petrol")
    
    user_interest_score: int = Field(default=0)  # For homepage category ranking
    average_rating: float = Field(default=0.0)
    total_ratings: int = Field(default=0)
    total_comments: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MotorcycleWithPricing(BaseModel):
    id: str
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
    specialisations: List[str] = Field(default_factory=list)
    
    # Technical Features
    mileage_kmpl: float = 25.0
    transmission_type: str = "Manual"
    number_of_gears: int = 6
    ground_clearance_mm: int = 180
    seat_height_mm: int = 800
    abs_available: bool = True
    braking_system: str = "Disc"
    suspension_type: str = "Telescopic"
    tyre_type: str = "Tubeless"
    wheel_size_inches: str = "17"
    headlight_type: str = "LED"
    fuel_type: str = "Petrol"
    
    user_interest_score: int = 0
    average_rating: float = 0.0
    total_ratings: int = 0
    total_comments: int = 0
    created_at: datetime
    vendor_prices: List[VendorPrice] = Field(default_factory=list)

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
    specialisations: List[str] = Field(default_factory=list)
    
    # Technical Features
    mileage_kmpl: float = 25.0
    transmission_type: str = "Manual"
    number_of_gears: int = 6
    ground_clearance_mm: int = 180
    seat_height_mm: int = 800
    abs_available: bool = True
    braking_system: str = "Disc"
    suspension_type: str = "Telescopic"
    tyre_type: str = "Tubeless"
    wheel_size_inches: str = "17"
    headlight_type: str = "LED"
    fuel_type: str = "Petrol"
    
    user_interest_score: int = 0

class CategorySummary(BaseModel):
    category: str
    count: int
    featured_motorcycles: List[Motorcycle]

class DatabaseStats(BaseModel):
    total_motorcycles: int
    manufacturers: List[str]
    categories: List[str]
    year_range: dict
    latest_update: datetime

class UpdateJobStatus(BaseModel):
    job_id: str
    status: str
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    stats: Optional[dict] = None

# User Request Models
class UserRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    request_type: str  # "feature_request", "bug_report", "motorcycle_addition", "general_feedback"
    priority: str = "medium"  # "low", "medium", "high", "critical"
    status: str = "pending"  # "pending", "in_progress", "resolved", "rejected"
    category: Optional[str] = None  # Additional categorization
    motorcycle_related: Optional[str] = None  # Motorcycle ID if related to specific bike
    admin_response: Optional[str] = None
    admin_user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

class UserRequestCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    request_type: str = Field(pattern="^(feature_request|bug_report|motorcycle_addition|general_feedback)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    category: Optional[str] = Field(max_length=100)
    motorcycle_related: Optional[str] = None

class UserRequestUpdate(BaseModel):
    status: Optional[str] = Field(pattern="^(pending|in_progress|resolved|rejected)$")
    admin_response: Optional[str] = Field(max_length=1000)
    priority: Optional[str] = Field(pattern="^(low|medium|high|critical)$")

# Virtual Garage Models
class GarageItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    motorcycle_id: str
    status: str  # "owned", "wishlist", "previously_owned", "test_ridden"
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    current_mileage: Optional[int] = None
    modifications: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    images: List[str] = Field(default_factory=list)  # URLs to user uploaded images
    is_public: bool = True  # Whether to show in public garage
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class GarageItemCreate(BaseModel):
    motorcycle_id: str
    status: str = Field(pattern="^(owned|wishlist|previously_owned|test_ridden)$")
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = Field(None, ge=0)
    current_mileage: Optional[int] = Field(None, ge=0)
    modifications: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=1000)
    is_public: bool = True

class GarageItemUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(owned|wishlist|previously_owned|test_ridden)$")
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = Field(None, ge=0)
    current_mileage: Optional[int] = Field(None, ge=0)
    modifications: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=1000)
    is_public: Optional[bool] = None

# Price Alert Models
class PriceAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    motorcycle_id: str
    target_price: float
    condition: str  # "below", "above", "equal"
    is_active: bool = True
    region: str = "US"
    triggered_count: int = 0
    last_triggered: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class PriceAlertCreate(BaseModel):
    motorcycle_id: str
    target_price: float = Field(gt=0)
    condition: str = Field(pattern="^(below|above|equal)$")
    region: str = "US"

# Rider Group Models
class RiderGroup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    location: Optional[str] = None
    group_type: str  # "location", "brand", "riding_style", "general"
    is_public: bool = True
    max_members: Optional[int] = None
    creator_id: str
    admin_ids: List[str] = Field(default_factory=list)
    member_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class RiderGroupCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10, max_length=1000)
    location: Optional[str] = Field(None, max_length=200)
    group_type: str = Field(pattern="^(location|brand|riding_style|general)$")
    is_public: bool = True
    max_members: Optional[int] = Field(None, ge=2, le=1000)

# Achievement Models
class Achievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: str  # emoji or icon class
    category: str  # "social", "collection", "activity", "milestone"
    requirement_type: str  # "count", "streak", "specific"
    requirement_value: int
    requirement_field: str  # what to count (e.g., "favorites", "ratings", "comments")
    points: int = 10
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserAchievement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    achievement_id: str
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    progress: int = 0  # current progress towards achievement
    is_completed: bool = False

# Daily Update Scheduler
class DailyUpdateScheduler:
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
    
    async def run_daily_updates(self):
        """Run comprehensive daily updates"""
        try:
            print(f"🔄 Starting daily updates at {datetime.now(timezone.utc)} GMT")
            
            # 1. Update motorcycle pricing
            await self.update_vendor_pricing()
            
            # 2. Check for new motorcycles/models
            await self.check_new_motorcycles()
            
            # 3. Update availability status
            await self.update_availability_status()
            
            # 4. Log update completion
            update_log = {
                "timestamp": datetime.now(timezone.utc),
                "type": "scheduled_daily_update",
                "status": "completed",
                "updates_applied": ["pricing", "availability", "new_models"],
                "next_update": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            }
            
            await db.update_logs.insert_one(update_log)
            print("✅ Daily updates completed successfully")
            
        except Exception as e:
            print(f"❌ Daily update failed: {str(e)}")
            # Log the error
            error_log = {
                "timestamp": datetime.now(timezone.utc),
                "type": "scheduled_daily_update",
                "status": "failed",
                "error": str(e)
            }
            await db.update_logs.insert_one(error_log)
    
    async def update_vendor_pricing(self):
        """Update vendor pricing for all motorcycles"""
        print("💰 Updating vendor pricing...")
        
        # Get all motorcycles
        motorcycles = await db.motorcycles.find({}).to_list(None)
        updated_count = 0
        
        for motorcycle in motorcycles:
            try:
                # Simulate price fluctuations (±5%)
                current_price = motorcycle.get("price_usd", 10000)
                price_change = random.uniform(-0.05, 0.05)
                new_price = max(500, int(current_price * (1 + price_change)))  # Minimum $500
                
                # Update the motorcycle price
                await db.motorcycles.update_one(
                    {"id": motorcycle["id"]},
                    {"$set": {
                        "price_usd": new_price,
                        "last_price_update": datetime.now(timezone.utc)
                    }}
                )
                updated_count += 1
                
            except Exception as e:
                print(f"Error updating pricing for {motorcycle.get('id', 'unknown')}: {str(e)}")
        
        print(f"📊 Updated pricing for {updated_count} motorcycles")
    
    async def check_new_motorcycles(self):
        """Check for new motorcycle models and add them"""
        print("🔍 Checking for new motorcycle models...")
        
        # This would typically connect to manufacturer APIs
        # For demo, we'll simulate adding a few new models
        current_year = datetime.now().year
        
        new_models = [
            {
                "manufacturer": "Yamaha",
                "model": f"YZF-R125 {current_year}",
                "year": current_year,
                "category": "Sport",
                "displacement": 125,
                "horsepower": 15,
                "price_usd": 4500,
                "availability": "Pre-order",
                "is_new_model": True
            },
            {
                "manufacturer": "Honda",
                "model": f"CB300R {current_year}",
                "year": current_year,
                "category": "Naked",
                "displacement": 286,
                "horsepower": 31,
                "price_usd": 4700,
                "availability": "Coming Soon",
                "is_new_model": True
            }
        ]
        
        added_count = 0
        for model_data in new_models:
            # Check if model already exists
            existing = await db.motorcycles.find_one({
                "manufacturer": model_data["manufacturer"],
                "model": model_data["model"],
                "year": model_data["year"]
            })
            
            if not existing:
                # Add the new model with full specifications
                motorcycle = self.generate_full_motorcycle_spec(model_data)
                await db.motorcycles.insert_one(motorcycle)
                added_count += 1
        
        print(f"🆕 Added {added_count} new motorcycle models")
    
    async def update_availability_status(self):
        """Update availability status based on age and stock"""
        print("📦 Updating availability status...")
        
        current_year = datetime.now().year
        updated_count = 0
        
        # Update availability based on motorcycle age
        motorcycles = await db.motorcycles.find({}).to_list(None)
        
        for motorcycle in motorcycles:
            try:
                year = motorcycle.get("year", current_year)
                current_availability = motorcycle.get("availability", "Available")
                new_availability = current_availability
                
                # Update availability logic
                if year < current_year - 8:
                    new_availability = "Collector Item"
                elif year < current_year - 3:
                    new_availability = "Discontinued"
                elif year < current_year - 1:
                    new_availability = "Limited Stock"
                else:
                    new_availability = "Available"
                
                # Only update if availability changed
                if new_availability != current_availability:
                    await db.motorcycles.update_one(
                        {"id": motorcycle["id"]},
                        {"$set": {
                            "availability": new_availability,
                            "availability_updated": datetime.now(timezone.utc)
                        }}
                    )
                    updated_count += 1
                    
            except Exception as e:
                print(f"Error updating availability for {motorcycle.get('id', 'unknown')}: {str(e)}")
        
        print(f"📊 Updated availability for {updated_count} motorcycles")
    
    def generate_full_motorcycle_spec(self, model_data):
        """Generate full motorcycle specification from basic data"""
        return {
            "id": str(uuid.uuid4()),
            "manufacturer": model_data["manufacturer"],
            "model": model_data["model"],
            "year": model_data["year"],
            "category": model_data["category"],
            "engine_type": "Single Cylinder" if model_data["displacement"] <= 200 else "Parallel Twin",
            "displacement": model_data["displacement"],
            "horsepower": model_data["horsepower"],
            "torque": int(model_data["horsepower"] * 0.75),
            "weight": 140 + (model_data["displacement"] // 10),
            "top_speed": int(90 + (model_data["horsepower"] * 1.5)),
            "fuel_capacity": 12.0 + (model_data["displacement"] // 150),
            "price_usd": model_data["price_usd"],
            "availability": model_data["availability"],
            "description": f"The latest {model_data['manufacturer']} {model_data['model']} represents cutting-edge technology and performance in the {model_data['category'].lower()} segment.",
            "image_url": "https://images.unsplash.com/photo-1558980664-2cd663cf8dde?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxtb3RvcmN5Y2xlfGVufDB8fHxibGFja19hbmRfd2hpdGV8MTc1MzgxMDQyNXww&ixlib=rb-4.1.0&q=85",
            "user_interest_score": 95,
            "specialisations": ["Latest Technology", "Performance", "Innovation"],
            "mileage_kmpl": max(15, 45 - (model_data["displacement"] // 20)),
            "transmission_type": "Manual",
            "number_of_gears": 6 if model_data["displacement"] > 200 else 5,
            "ground_clearance_mm": 160,
            "seat_height_mm": 750 + (model_data["displacement"] // 20),
            "abs_available": True,
            "braking_system": "Disc",
            "suspension_type": "Telescopic",
            "tyre_type": "Tubeless",
            "wheel_size_inches": "17",
            "headlight_type": "LED",
            "fuel_type": "Petrol",
            "created_at": datetime.now(timezone.utc),
            "is_new_model": model_data.get("is_new_model", False)
        }
    
    def start_scheduler(self):
        """Start the daily update scheduler"""
        if self.is_running:
            return
        
        def run_scheduler():
            # Schedule daily updates at 00:00 GMT
            schedule.every().day.at("00:00").do(lambda: asyncio.create_task(self.run_daily_updates()))
            
            print("📅 Daily update scheduler started - Updates at 00:00 GMT")
            
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the daily update scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        schedule.clear()
        print("🛑 Daily update scheduler stopped")

# Global scheduler instance
daily_scheduler = DailyUpdateScheduler()

# Authentication constants and helpers
JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key-here")
JWT_ALGORITHM = "HS256"

def create_jwt_token(user_id: str) -> str:
    """Create JWT token for user"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow().timestamp() + (24 * 60 * 60)  # 24 hours
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Optional[str]:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("exp", 0) < datetime.utcnow().timestamp():
            return None
        return payload.get("user_id")
    except jwt.InvalidTokenError:
        return None

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Authentication helper
async def get_current_user(x_session_id: str = Header(None), authorization: str = Header(None)):
    """Get current user from session ID or JWT token"""
    user = None
    
    # First try JWT token from Authorization header
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user_id = verify_jwt_token(token)
        if user_id:
            user_doc = await db.users.find_one({"id": user_id})
            if user_doc:
                user = User(**user_doc)
    
    # Fall back to session ID (for Emergent auth)
    if not user and x_session_id:
        user_doc = await db.users.find_one({"session_token": x_session_id})
        if user_doc:
            user = User(**user_doc)
    
    return user

async def require_auth(x_session_id: str = Header(None), authorization: str = Header(None)):
    """Require authentication"""
    user = await get_current_user(x_session_id, authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Welcome to Bike-Dream API - Comprehensive Motorcycle Database with User Community"}

# Vendor pricing routes
@api_router.get("/motorcycles/{motorcycle_id}/pricing")
async def get_motorcycle_pricing(motorcycle_id: str, region: str = Query("US")):
    """Get vendor pricing for a motorcycle in a specific region"""
    motorcycle = await db.motorcycles.find_one({"id": motorcycle_id})
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    vendor_prices = vendor_pricing.get_vendor_prices(motorcycle, region)
    
    return {
        "motorcycle_id": motorcycle_id,
        "region": region,
        "currency": vendor_pricing.regional_currencies.get(region, "USD"),
        "vendor_prices": vendor_prices,
        "last_updated": datetime.utcnow()
    }

@api_router.get("/pricing/regions")
async def get_supported_regions():
    """Get list of supported regions for pricing"""
    return {
        "regions": vendor_pricing.get_supported_regions(),
        "default_region": "US"
    }

# Enhanced motorcycle routes with specialisation and features filtering
@api_router.get("/motorcycles/filters/specialisations")
async def get_available_specialisations():
    """Get all available motorcycle specialisations for filtering"""
    # Get all unique specialisations from the database
    specialisations_pipeline = [
        {"$unwind": "$specialisations"},
        {"$group": {"_id": "$specialisations"}},
        {"$sort": {"_id": 1}}
    ]
    
    specialisations = await db.motorcycles.aggregate(specialisations_pipeline).to_list(None)
    specialisation_list = [s["_id"] for s in specialisations]
    
    return {
        "specialisations": specialisation_list,
        "count": len(specialisation_list)
    }

@api_router.get("/motorcycles/filters/features")
async def get_available_features():
    """Get all available technical features for filtering"""
    # Get distinct values for each technical feature
    transmission_types = await db.motorcycles.distinct("transmission_type")
    engine_types = await db.motorcycles.distinct("engine_type")
    braking_systems = await db.motorcycles.distinct("braking_system")
    suspension_types = await db.motorcycles.distinct("suspension_type")
    tyre_types = await db.motorcycles.distinct("tyre_type")
    headlight_types = await db.motorcycles.distinct("headlight_type")
    fuel_types = await db.motorcycles.distinct("fuel_type")
    
    # Get ranges for numeric features
    mileage_range = await db.motorcycles.aggregate([
        {"$group": {"_id": None, "min_mileage": {"$min": "$mileage_kmpl"}, "max_mileage": {"$max": "$mileage_kmpl"}}}
    ]).to_list(1)
    
    ground_clearance_range = await db.motorcycles.aggregate([
        {"$group": {"_id": None, "min_gc": {"$min": "$ground_clearance_mm"}, "max_gc": {"$max": "$ground_clearance_mm"}}}
    ]).to_list(1)
    
    seat_height_range = await db.motorcycles.aggregate([
        {"$group": {"_id": None, "min_sh": {"$min": "$seat_height_mm"}, "max_sh": {"$max": "$seat_height_mm"}}}
    ]).to_list(1)
    
    return {
        "transmission_types": transmission_types,
        "engine_types": engine_types,
        "braking_systems": braking_systems,
        "suspension_types": suspension_types,
        "tyre_types": tyre_types,
        "headlight_types": headlight_types,
        "fuel_types": fuel_types,
        "mileage_range": mileage_range[0] if mileage_range else {"min_mileage": 15, "max_mileage": 50},
        "ground_clearance_range": ground_clearance_range[0] if ground_clearance_range else {"min_gc": 150, "max_gc": 250},
        "seat_height_range": seat_height_range[0] if seat_height_range else {"min_sh": 700, "max_sh": 900}
    }

# Authentication routes
@api_router.post("/auth/register")
async def register_user(user_data: UserRegister):
    """Register a new user with email and password"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Hash password and create user
        password_hash = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash,
            auth_method="password",
            picture=f"https://ui-avatars.com/api/?name={user_data.name}&background=0D8ABC&color=fff"
        )
        
        await db.users.insert_one(user.dict())
        
        # Create JWT token
        token = create_jwt_token(user.id)
        
        return {
            "message": "Registration successful",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "picture": user.picture
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@api_router.post("/auth/login")
async def login_user(user_data: UserLogin):
    """Login user with email and password"""
    try:
        # Find user by email
        user_doc = await db.users.find_one({"email": user_data.email})
        if not user_doc:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user = User(**user_doc)
        
        # Verify password
        if not user.password_hash or not verify_password(user_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create JWT token
        token = create_jwt_token(user.id)
        
        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "picture": user.picture
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")

@api_router.post("/auth/google/callback")
async def google_oauth_callback(callback_data: dict):
    """Handle Google OAuth callback with authorization code"""
    try:
        code = callback_data.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not provided")
        
        # Exchange authorization code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", "your-google-client-id"),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", "your-google-client-secret"),
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback")
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=token_data) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
                token_response = await response.json()
        
        access_token = token_response.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Get user info from Google
        user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(user_info_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to get user info from Google")
                user_info = await response.json()
        
        # Create or update user
        google_data = GoogleOAuthData(
            email=user_info["email"],
            name=user_info["name"],
            picture=user_info.get("picture", ""),
            google_id=user_info["id"]
        )
        
        return await google_oauth(google_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google OAuth callback failed: {str(e)}")

@api_router.post("/auth/google")
async def google_oauth(oauth_data: GoogleOAuthData):
    """Authenticate user with Google OAuth"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": oauth_data.email})
        
        if existing_user:
            # Update Google ID if not set and auth method
            user = User(**existing_user)
            if not user.google_id:
                await db.users.update_one(
                    {"email": oauth_data.email},
                    {"$set": {
                        "google_id": oauth_data.google_id,
                        "auth_method": "google",
                        "picture": oauth_data.picture
                    }}
                )
                user.google_id = oauth_data.google_id
                user.auth_method = "google"
                user.picture = oauth_data.picture
        else:
            # Create new user
            user = User(
                email=oauth_data.email,
                name=oauth_data.name,
                picture=oauth_data.picture,
                google_id=oauth_data.google_id,
                auth_method="google"
            )
            await db.users.insert_one(user.dict())
        
        # Create JWT token
        token = create_jwt_token(user.id)
        
        return {
            "message": "Google authentication successful",
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "picture": user.picture
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google authentication failed: {str(e)}")

@api_router.post("/auth/profile")
async def authenticate_user(user_data: dict):
    """Authenticate user with Emergent session data (legacy support)"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data["email"]})
        
        if existing_user:
            # Update session token for existing user
            await db.users.update_one(
                {"email": user_data["email"]},
                {"$set": {"session_token": user_data["session_token"]}}
            )
            user = User(**existing_user)
            user.session_token = user_data["session_token"]
        else:
            # Create new user
            user_create = UserCreate(**user_data)
            user = User(**user_create.dict(), auth_method="emergent")
            await db.users.insert_one(user.dict())
        
        return {
            "message": "Authentication successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "picture": user.picture
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@api_router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(require_auth)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "picture": current_user.picture,
        "favorite_count": len(current_user.favorite_motorcycles)
    }

# Favorites routes
@api_router.post("/motorcycles/{motorcycle_id}/favorite")
async def add_to_favorites(motorcycle_id: str, current_user: User = Depends(require_auth)):
    """Add motorcycle to user's favorites"""
    if motorcycle_id not in current_user.favorite_motorcycles:
        await db.users.update_one(
            {"id": current_user.id},
            {"$push": {"favorite_motorcycles": motorcycle_id}}
        )
        return {"message": "Added to favorites", "favorited": True}
    else:
        return {"message": "Already in favorites", "favorited": True}

@api_router.delete("/motorcycles/{motorcycle_id}/favorite")
async def remove_from_favorites(motorcycle_id: str, current_user: User = Depends(require_auth)):
    """Remove motorcycle from user's favorites"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"favorite_motorcycles": motorcycle_id}}
    )
    return {"message": "Removed from favorites", "favorited": False}

@api_router.get("/motorcycles/favorites")
async def get_favorite_motorcycles(current_user: User = Depends(require_auth)):
    """Get user's favorite motorcycles"""
    favorites = await db.motorcycles.find(
        {"id": {"$in": current_user.favorite_motorcycles}}
    ).to_list(None)
    
    return [Motorcycle(**moto) for moto in favorites]

# Rating routes
@api_router.post("/motorcycles/{motorcycle_id}/rate")
async def rate_motorcycle(motorcycle_id: str, rating_data: RatingCreate, current_user: User = Depends(require_auth)):
    """Rate a motorcycle"""
    # Check if motorcycle exists
    motorcycle = await db.motorcycles.find_one({"id": motorcycle_id})
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    # Check if user already rated this motorcycle
    existing_rating = await db.ratings.find_one({
        "user_id": current_user.id,
        "motorcycle_id": motorcycle_id
    })
    
    if existing_rating:
        # Update existing rating
        await db.ratings.update_one(
            {"id": existing_rating["id"]},
            {
                "$set": {
                    "rating": rating_data.rating,
                    "review_text": rating_data.review_text,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        message = "Rating updated"
    else:
        # Create new rating
        rating = Rating(
            user_id=current_user.id,
            motorcycle_id=motorcycle_id,
            rating=rating_data.rating,
            review_text=rating_data.review_text
        )
        await db.ratings.insert_one(rating.dict())
        message = "Rating submitted"
    
    # Update motorcycle average rating
    await update_motorcycle_rating_stats(motorcycle_id)
    
    return {"message": message}

@api_router.get("/motorcycles/{motorcycle_id}/ratings")
async def get_motorcycle_ratings(motorcycle_id: str, limit: int = Query(10, le=50)):
    """Get ratings for a motorcycle"""
    ratings_pipeline = [
        {"$match": {"motorcycle_id": motorcycle_id}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user"
        }},
        {"$unwind": "$user"},
        {"$sort": {"created_at": -1}},
        {"$limit": limit},
        {"$project": {
            "id": 1,
            "rating": 1,
            "review_text": 1,
            "created_at": 1,
            "user_name": "$user.name",
            "user_picture": "$user.picture"
        }}
    ]
    
    ratings = await db.ratings.aggregate(ratings_pipeline).to_list(limit)
    
    # Convert ObjectIds to strings for JSON serialization
    for rating in ratings:
        if "_id" in rating:
            rating["_id"] = str(rating["_id"])
    
    return ratings

async def update_motorcycle_rating_stats(motorcycle_id: str):
    """Update motorcycle rating statistics"""
    stats_pipeline = [
        {"$match": {"motorcycle_id": motorcycle_id}},
        {"$group": {
            "_id": "$motorcycle_id",
            "average_rating": {"$avg": "$rating"},
            "total_ratings": {"$sum": 1}
        }}
    ]
    
    stats = await db.ratings.aggregate(stats_pipeline).to_list(1)
    if stats:
        stat = stats[0]
        await db.motorcycles.update_one(
            {"id": motorcycle_id},
            {
                "$set": {
                    "average_rating": round(stat["average_rating"], 1),
                    "total_ratings": stat["total_ratings"]
                }
            }
        )

# Comment routes
@api_router.post("/motorcycles/{motorcycle_id}/comment")
async def add_comment(motorcycle_id: str, comment_data: CommentCreate, user: User = Depends(require_auth)):
    """Add a comment to a motorcycle with support for replies"""
    try:
        # Verify motorcycle exists
        motorcycle = await db.motorcycles.find_one({"id": motorcycle_id})
        if not motorcycle:
            raise HTTPException(status_code=404, detail="Motorcycle not found")
        
        # If this is a reply, verify parent comment exists
        if comment_data.parent_comment_id:
            parent_comment = await db.comments.find_one({"id": comment_data.parent_comment_id})
            if not parent_comment:
                raise HTTPException(status_code=404, detail="Parent comment not found")
            
            # Increment replies count for parent comment
            await db.comments.update_one(
                {"id": comment_data.parent_comment_id},
                {"$inc": {"replies_count": 1}}
            )
        
        # Create comment
        comment = Comment(
            motorcycle_id=motorcycle_id,
            user_id=user.id,
            user_name=user.name,
            user_picture=user.picture,
            content=comment_data.content,
            parent_comment_id=comment_data.parent_comment_id
        )
        
        await db.comments.insert_one(comment.dict())
        return {"message": "Comment added successfully", "comment": comment}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add comment: {str(e)}")

@api_router.get("/motorcycles/{motorcycle_id}/comments")
async def get_comments(motorcycle_id: str, include_replies: bool = True):
    """Get comments for a motorcycle with optional replies"""
    try:
        # Get all comments for this motorcycle
        if include_replies:
            # Get all comments (both top-level and replies)
            all_comments = await db.comments.find({"motorcycle_id": motorcycle_id}).sort("created_at", 1).to_list(None)
            
            # Organize comments in a threaded structure
            comments_dict = {}
            top_level_comments = []
            
            # First pass: create comment objects and organize by ID
            for comment_data in all_comments:
                comment = Comment(**comment_data)
                comments_dict[comment.id] = {
                    **comment.dict(),
                    "replies": []
                }
                
                if not comment.parent_comment_id:
                    top_level_comments.append(comment.id)
            
            # Second pass: nest replies under their parent comments
            for comment_data in all_comments:
                comment = Comment(**comment_data)
                if comment.parent_comment_id and comment.parent_comment_id in comments_dict:
                    comments_dict[comment.parent_comment_id]["replies"].append(
                        comments_dict[comment.id]
                    )
            
            # Return only top-level comments with nested replies
            result = [comments_dict[comment_id] for comment_id in top_level_comments if comment_id in comments_dict]
            
        else:
            # Get only top-level comments (no replies)
            top_level_comments = await db.comments.find({
                "motorcycle_id": motorcycle_id,
                "parent_comment_id": None
            }).sort("created_at", -1).to_list(None)
            
            result = [Comment(**comment).dict() for comment in top_level_comments]
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get comments: {str(e)}")

@api_router.post("/comments/{comment_id}/like")
async def toggle_comment_like(comment_id: str, user: User = Depends(require_auth)):
    """Toggle like on a comment"""
    try:
        # Check if comment exists
        comment = await db.comments.find_one({"id": comment_id})
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Check if user already liked this comment
        existing_like = await db.comment_likes.find_one({
            "comment_id": comment_id,
            "user_id": user.id
        })
        
        if existing_like:
            # Unlike: remove like and decrement count
            await db.comment_likes.delete_one({
                "comment_id": comment_id,
                "user_id": user.id
            })
            await db.comments.update_one(
                {"id": comment_id},
                {"$inc": {"likes_count": -1}}
            )
            return {"message": "Comment unliked", "liked": False}
        else:
            # Like: add like and increment count
            like = CommentLike(comment_id=comment_id, user_id=user.id)
            await db.comment_likes.insert_one(like.dict())
            await db.comments.update_one(
                {"id": comment_id},
                {"$inc": {"likes_count": 1}}
            )
            return {"message": "Comment liked", "liked": True}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to toggle like: {str(e)}")

@api_router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, user: User = Depends(require_auth)):
    """Delete a comment (only by the author)"""
    try:
        # Check if comment exists and user is the author
        comment = await db.comments.find_one({"id": comment_id})
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment["user_id"] != user.id:
            raise HTTPException(status_code=403, detail="You can only delete your own comments")
        
        # Delete the comment and all associated likes
        await db.comments.delete_one({"id": comment_id})
        await db.comment_likes.delete_many({"comment_id": comment_id})
        
        # If this comment had replies, also delete them
        await db.comments.delete_many({"parent_comment_id": comment_id})
        
        # If this was a reply, decrement parent's reply count
        if comment.get("parent_comment_id"):
            await db.comments.update_one(
                {"id": comment["parent_comment_id"]},
                {"$inc": {"replies_count": -1}}
            )
        
        return {"message": "Comment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete comment: {str(e)}")

@api_router.get("/users/{user_id}/activity-stats")
async def get_user_activity_stats(user_id: str, user: User = Depends(require_auth)):
    """Get comprehensive user activity statistics"""
    try:
        # Ensure user can only access their own stats or admin can access any
        if user.id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get favorites count
        favorites_count = await db.users.aggregate([
            {"$match": {"id": user_id}},
            {"$project": {"favorites_count": {"$size": {"$ifNull": ["$favorite_motorcycles", []]}}}}
        ]).to_list(1)
        
        favorites_count = favorites_count[0]["favorites_count"] if favorites_count else 0
        
        # Get ratings count
        ratings_count = await db.ratings.count_documents({"user_id": user_id})
        
        # Get comments count (both top-level and replies)
        comments_count = await db.comments.count_documents({"user_id": user_id})
        
        # Get discussion threads count (top-level comments only)
        threads_count = await db.comments.count_documents({
            "user_id": user_id,
            "parent_comment_id": None
        })
        
        # Get recent activity (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        recent_comments = await db.comments.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": thirty_days_ago}
        })
        
        recent_ratings = await db.ratings.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": thirty_days_ago}
        })
        
        # Get favorite manufacturers (from user's favorite motorcycles)
        user_data = await db.users.find_one({"id": user_id})
        favorite_motorcycles = user_data.get("favorite_motorcycles", []) if user_data else []
        
        manufacturer_stats = {}
        if favorite_motorcycles:
            for motorcycle_id in favorite_motorcycles:
                motorcycle = await db.motorcycles.find_one({"id": motorcycle_id})
                if motorcycle:
                    manufacturer = motorcycle.get("manufacturer", "Unknown")
                    manufacturer_stats[manufacturer] = manufacturer_stats.get(manufacturer, 0) + 1
        
        # Sort manufacturers by count
        top_manufacturers = sorted(manufacturer_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get user's rating distribution
        rating_distribution = {}
        user_ratings = await db.ratings.find({"user_id": user_id}).to_list(None)
        for rating in user_ratings:
            star_rating = rating.get("rating", 0)
            rating_distribution[star_rating] = rating_distribution.get(star_rating, 0) + 1
        
        # Calculate engagement score (0-100)
        engagement_score = min(100, (
            (favorites_count * 2) +
            (ratings_count * 3) +
            (comments_count * 4) +
            (threads_count * 5)
        ) / 2)
        
        return {
            "user_id": user_id,
            "total_stats": {
                "favorites_count": favorites_count,
                "ratings_given": ratings_count,
                "comments_posted": comments_count,
                "discussion_threads": threads_count,
                "engagement_score": round(engagement_score, 1)
            },
            "recent_activity": {
                "comments_last_30_days": recent_comments,
                "ratings_last_30_days": recent_ratings
            },
            "preferences": {
                "top_manufacturers": top_manufacturers,
                "rating_distribution": rating_distribution
            },
            "achievements": generate_user_achievements(favorites_count, ratings_count, comments_count, threads_count)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get user activity stats: {str(e)}")

def generate_user_achievements(favorites, ratings, comments, threads):
    """Generate user achievements based on activity"""
    achievements = []
    
    # Favorites achievements
    if favorites >= 1:
        achievements.append({"title": "First Favorite", "description": "Added your first motorcycle to favorites", "icon": "⭐"})
    if favorites >= 10:
        achievements.append({"title": "Motorcycle Enthusiast", "description": "Favorited 10+ motorcycles", "icon": "🏍️"})
    if favorites >= 50:
        achievements.append({"title": "Collector", "description": "Favorited 50+ motorcycles", "icon": "🏆"})
    
    # Rating achievements
    if ratings >= 1:
        achievements.append({"title": "First Review", "description": "Rated your first motorcycle", "icon": "⭐"})
    if ratings >= 25:
        achievements.append({"title": "Reviewer", "description": "Rated 25+ motorcycles", "icon": "📝"})
    if ratings >= 100:
        achievements.append({"title": "Expert Reviewer", "description": "Rated 100+ motorcycles", "icon": "🎯"})
    
    # Comment achievements
    if comments >= 1:
        achievements.append({"title": "Voice Heard", "description": "Posted your first comment", "icon": "💬"})
    if comments >= 20:
        achievements.append({"title": "Active Contributor", "description": "Posted 20+ comments", "icon": "🗣️"})
    if comments >= 100:
        achievements.append({"title": "Community Leader", "description": "Posted 100+ comments", "icon": "👑"})
    
    # Thread achievements
    if threads >= 5:
        achievements.append({"title": "Discussion Starter", "description": "Started 5+ discussions", "icon": "🚀"})
    if threads >= 20:
        achievements.append({"title": "Community Builder", "description": "Started 20+ discussions", "icon": "🏗️"})
    
    return achievements
async def flag_comment(comment_id: str, user: User = Depends(require_auth)):
    """Flag a comment for moderation"""
    try:
        # Check if comment exists
        comment = await db.comments.find_one({"id": comment_id})
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Flag the comment
        await db.comments.update_one(
            {"id": comment_id},
            {"$set": {"is_flagged": True}}
        )
        
        # Log the flag action for admin review
        flag_log = {
            "comment_id": comment_id,
            "flagged_by": user.id,
            "flagged_at": datetime.now(timezone.utc),
            "comment_content": comment["content"],
            "comment_author": comment["user_id"]
        }
        await db.flagged_comments.insert_one(flag_log)
        
        return {"message": "Comment flagged for review"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to flag comment: {str(e)}")

async def update_motorcycle_comment_count(motorcycle_id: str):
    """Update motorcycle comment count"""
    count = await db.comments.count_documents({"motorcycle_id": motorcycle_id})
    await db.motorcycles.update_one(
        {"id": motorcycle_id},
        {"$set": {"total_comments": count}}
    )

# Database statistics
@api_router.get("/stats", response_model=DatabaseStats)
async def get_database_stats():
    """Get comprehensive database statistics"""
    total = await db.motorcycles.count_documents({})
    
    manufacturers_pipeline = [{"$group": {"_id": "$manufacturer"}}, {"$sort": {"_id": 1}}]
    categories_pipeline = [{"$group": {"_id": "$category"}}, {"$sort": {"_id": 1}}]
    
    manufacturers = await db.motorcycles.aggregate(manufacturers_pipeline).to_list(None)
    categories = await db.motorcycles.aggregate(categories_pipeline).to_list(None)
    
    # Get year range
    year_range = await db.motorcycles.aggregate([
        {"$group": {"_id": None, "min_year": {"$min": "$year"}, "max_year": {"$max": "$year"}}}
    ]).to_list(1)
    
    return DatabaseStats(
        total_motorcycles=total,
        manufacturers=[m["_id"] for m in manufacturers],
        categories=[c["_id"] for c in categories],
        year_range=year_range[0] if year_range else {"min_year": 1900, "max_year": 2025},
        latest_update=datetime.utcnow()
    )

# Daily Update System APIs (existing)
@api_router.post("/update-system/run-daily-update")
async def trigger_daily_update(background_tasks: BackgroundTasks):
    """Manually trigger daily update process (normally runs at GMT 00:00)"""
    job_id = str(uuid.uuid4())
    
    # Store initial job status
    job_status = {
        "job_id": job_id,
        "status": "running",
        "message": "Daily update process started",
        "started_at": datetime.now(timezone.utc),
        "completed_at": None,
        "stats": None
    }
    
    await db.update_jobs.insert_one(job_status)
    
    # Run update in background
    async def run_update():
        try:
            result = await run_daily_update_job(mongo_url, os.environ['DB_NAME'])
            
            # Update job status
            await db.update_jobs.update_one(
                {"job_id": job_id},
                {
                    "$set": {
                        "status": "completed",
                        "message": result.get("message", "Update completed"),
                        "completed_at": datetime.now(timezone.utc),
                        "stats": result.get("stats", {})
                    }
                }
            )
        except Exception as e:
            await db.update_jobs.update_one(
                {"job_id": job_id},
                {
                    "$set": {
                        "status": "failed",
                        "message": f"Update failed: {str(e)}",
                        "completed_at": datetime.now(timezone.utc)
                    }
                }
            )
    
    # Start background task
    background_tasks.add_task(run_update)
    
    return {
        "job_id": job_id,
        "status": "initiated",
        "message": "Daily update process has been started in the background",
        "check_status_url": f"/api/update-system/job-status/{job_id}"
    }

@api_router.get("/update-system/job-status/{job_id}")
async def get_update_job_status(job_id: str):
    """Get status of a daily update job"""
    job = await db.update_jobs.find_one({"job_id": job_id})
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "message": job["message"],
        "started_at": job["started_at"],
        "completed_at": job.get("completed_at"),
        "stats": job.get("stats"),
        "duration_seconds": (
            (job["completed_at"] - job["started_at"]).total_seconds() 
            if job.get("completed_at") else None
        )
    }

@api_router.get("/update-system/update-history")
async def get_update_history(limit: int = Query(10, le=50)):
    """Get history of daily updates"""
    history = await db.daily_update_logs.find().sort("start_time", -1).limit(limit).to_list(limit)
    
    # Convert ObjectIds to strings for JSON serialization
    for record in history:
        if "_id" in record:
            record["_id"] = str(record["_id"])
    
    return {
        "update_history": history,
        "count": len(history)
    }

@api_router.get("/update-system/regional-customizations")
async def get_regional_customizations(region: Optional[str] = Query(None)):
    """Get regional customizations for motorcycles"""
    query = {}
    if region:
        query["region"] = region
    
    customizations = await db.regional_customizations.find(query).to_list(100)
    
    # Convert ObjectIds to strings for JSON serialization
    for customization in customizations:
        if "_id" in customization:
            customization["_id"] = str(customization["_id"])
    
    available_regions = await db.regional_customizations.distinct("region")
    
    return {
        "customizations": customizations,
        "available_regions": available_regions
    }

# Enhanced motorcycle routes with specialisation and features filtering
@api_router.post("/motorcycles", response_model=Motorcycle)
async def create_motorcycle(motorcycle: MotorcycleCreate):
    motorcycle_dict = motorcycle.dict()
    motorcycle_obj = Motorcycle(**motorcycle_dict)
    await db.motorcycles.insert_one(motorcycle_obj.dict())
    return motorcycle_obj

@api_router.get("/motorcycles", response_model=dict)
async def get_motorcycles(
    search: Optional[str] = Query(None, description="Search in manufacturer, model, or description"),
    manufacturer: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    specialisations: Optional[str] = Query(None, description="Comma-separated list of required specialisations"),
    
    # Technical Features Filters
    transmission_type: Optional[str] = Query(None),
    engine_type: Optional[str] = Query(None),
    braking_system: Optional[str] = Query(None),
    suspension_type: Optional[str] = Query(None),
    tyre_type: Optional[str] = Query(None),
    headlight_type: Optional[str] = Query(None),
    fuel_type: Optional[str] = Query(None),
    abs_available: Optional[bool] = Query(None),
    
    # Numeric Features Filters
    mileage_min: Optional[float] = Query(None),
    mileage_max: Optional[float] = Query(None),
    ground_clearance_min: Optional[int] = Query(None),
    ground_clearance_max: Optional[int] = Query(None),
    seat_height_min: Optional[int] = Query(None),
    seat_height_max: Optional[int] = Query(None),
    
    year_min: Optional[int] = Query(None),
    year_max: Optional[int] = Query(None),
    price_min: Optional[int] = Query(None),
    price_max: Optional[int] = Query(None),
    displacement_min: Optional[int] = Query(None),
    displacement_max: Optional[int] = Query(None),
    horsepower_min: Optional[int] = Query(None),
    horsepower_max: Optional[int] = Query(None),
    sort_by: Optional[str] = Query("default", description="Sort by: default (year desc, price asc), year, price, horsepower, model, user_interest_score, mileage_kmpl, top_speed, weight"),
    sort_order: Optional[str] = Query("desc", description="asc or desc"),
    limit: Optional[int] = Query(25, le=100),  # Changed default to 25 for pagination
    skip: Optional[int] = Query(0),
    page: Optional[int] = Query(1, ge=1),  # Added page parameter
    region: Optional[str] = Query("US", description="Region for pricing")
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
    
    # Specialisations filtering
    if specialisations and specialisations.strip():
        specialisation_list = [s.strip() for s in specialisations.split(",") if s.strip()]
        if specialisation_list:
            query["specialisations"] = {"$in": specialisation_list}
    
    # Technical Features filtering
    if transmission_type:
        query["transmission_type"] = transmission_type
    if engine_type:
        query["engine_type"] = {"$regex": engine_type, "$options": "i"}
    if braking_system:
        query["braking_system"] = braking_system
    if suspension_type:
        query["suspension_type"] = suspension_type
    if tyre_type:
        query["tyre_type"] = tyre_type
    if headlight_type:
        query["headlight_type"] = headlight_type
    if fuel_type:
        query["fuel_type"] = fuel_type
    if abs_available is not None:
        query["abs_available"] = abs_available
    
    # Numeric features filtering
    if mileage_min:
        query.setdefault("mileage_kmpl", {})["$gte"] = mileage_min
    if mileage_max:
        query.setdefault("mileage_kmpl", {})["$lte"] = mileage_max
    if ground_clearance_min:
        query.setdefault("ground_clearance_mm", {})["$gte"] = ground_clearance_min
    if ground_clearance_max:
        query.setdefault("ground_clearance_mm", {})["$lte"] = ground_clearance_max
    if seat_height_min:
        query.setdefault("seat_height_mm", {})["$gte"] = seat_height_min
    if seat_height_max:
        query.setdefault("seat_height_mm", {})["$lte"] = seat_height_max
    
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
    
    # Calculate pagination parameters
    if page > 1:
        skip = (page - 1) * limit
    
    # Get total count for pagination
    total_count = await db.motorcycles.count_documents(query)
    
    # Sort direction
    sort_direction = 1 if sort_order == "asc" else -1
    
    # Implement dual-level sorting: new bikes to old bikes (year desc), then low to high price (price asc)
    if sort_by == "default" or sort_by == "user_interest_score":
        # Default sorting: year descending (new to old), then price ascending (low to high)
        motorcycles = await db.motorcycles.find(query).sort([("year", -1), ("price_usd", 1)]).skip(skip).limit(limit).to_list(limit)
    else:
        # Single field sorting with custom sort direction
        motorcycles = await db.motorcycles.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit).to_list(limit)
    
    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
    has_next = page < total_pages
    has_previous = page > 1
    
    return {
        "motorcycles": [Motorcycle(**motorcycle) for motorcycle in motorcycles],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    }

@api_router.get("/motorcycles/{motorcycle_id}", response_model=MotorcycleWithPricing)
async def get_motorcycle(motorcycle_id: str, region: str = Query("US")):
    motorcycle = await db.motorcycles.find_one({"id": motorcycle_id})
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    # Get vendor pricing for this region
    vendor_prices = vendor_pricing.get_vendor_prices(motorcycle, region)
    
    motorcycle_data = Motorcycle(**motorcycle)
    motorcycle_with_pricing = MotorcycleWithPricing(
        **motorcycle_data.dict(),
        vendor_prices=vendor_prices
    )
    
    return motorcycle_with_pricing

@api_router.get("/motorcycles/categories/summary", response_model=List[CategorySummary])
async def get_categories_summary():
    """Get categories with top motorcycles by user interest for homepage"""
    categories = ["Sport", "Cruiser", "Touring", "Adventure", "Naked", "Vintage", "Electric", "Scooter", "Standard", "Enduro", "Motocross"]
    
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
    """Seed the database with comprehensive motorcycle data (1000+ motorcycles)"""
    
    try:
        # Get comprehensive motorcycle data
        comprehensive_motorcycles = get_comprehensive_motorcycle_data()
        
        # Clear existing data
        await db.motorcycles.delete_many({})
        
        # Insert in batches for better performance
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(comprehensive_motorcycles), batch_size):
            batch = comprehensive_motorcycles[i:i + batch_size]
            motorcycles_to_insert = []
            
            for moto_data in batch:
                motorcycle_obj = Motorcycle(**moto_data)
                motorcycles_to_insert.append(motorcycle_obj.dict())
            
            await db.motorcycles.insert_many(motorcycles_to_insert)
            total_inserted += len(motorcycles_to_insert)
        
        # Get final statistics
        stats = await get_database_stats()
        
        # Add sample ratings to make the site more engaging
        try:
            # Sample users for ratings
            sample_users = [
                {"id": "user1", "name": "Alex Johnson", "picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex"},
                {"id": "user2", "name": "Sarah Chen", "picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah"},
                {"id": "user3", "name": "Mike Rodriguez", "picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike"},
                {"id": "user4", "name": "Emma Wilson", "picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=Emma"},
                {"id": "user5", "name": "David Park", "picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=David"},
                {"id": "user6", "name": "Lisa Thompson", "picture": "https://api.dicebear.com/7.x/avataaars/svg?seed=Lisa"},
            ]
            
            # Sample reviews for different types of motorcycles
            sample_reviews = {
                "Sport": [
                    "Incredible performance on the track! The power delivery is smooth and the handling is razor sharp.",
                    "Perfect for weekend rides and occasional track days. Love the aggressive styling.",
                    "Fast and fun, but can be a bit harsh on longer rides. Great for enthusiasts!",
                    "Amazing acceleration and braking. The electronics package is top-notch.",
                    "Beautiful bike with excellent build quality. Worth every penny!"
                ],
                "Cruiser": [
                    "Comfortable for long highway cruises. The engine has that perfect rumble.",
                    "Classic styling meets modern reliability. Perfect for touring.",
                    "Smooth ride with plenty of torque. Great for both city and highway riding.",
                    "Love the low seat height and relaxed riding position. Very confidence-inspiring.",
                    "Beautiful chrome details and solid build quality. A real head-turner!"
                ],
                "Naked": [
                    "Perfect balance of performance and practicality. Great for daily commuting.",
                    "Upright riding position is comfortable and the bike is very manageable.",
                    "Excellent value for money. Reliable and fun to ride in all conditions.",
                    "Great first big bike! Not too intimidating but still plenty of fun.",
                    "Love the minimalist design and direct connection to the road."
                ],
                "Adventure": [
                    "Perfect for both on-road touring and light off-road adventures.",
                    "Comfortable for long distances with excellent wind protection.",
                    "Capable and versatile. Can handle anything from city streets to mountain trails.",
                    "Great for exploring new places. The large fuel tank gives excellent range.",
                    "Excellent build quality and reliability. Built to go anywhere!"
                ]
            }
            
            # Clear existing ratings
            await db.ratings.delete_many({})
            
            # Get a sample of motorcycles to add ratings to
            motorcycles_sample = await db.motorcycles.find({}).limit(500).to_list(500)
            
            # Add ratings to roughly 40% of motorcycles
            import random
            ratings_added = 0
            
            for motorcycle in motorcycles_sample:
                if random.random() < 0.4:  # 40% chance to get ratings
                    category = motorcycle.get('category', 'Sport')
                    
                    # Generate 1-4 ratings for this motorcycle
                    num_ratings = random.randint(1, 4)
                    total_rating = 0
                    
                    for i in range(num_ratings):
                        # Generate rating (biased towards higher ratings)
                        rating = random.choices([3, 4, 5], weights=[1, 3, 4])[0]
                        total_rating += rating
                        
                        # Select random user and review
                        user = random.choice(sample_users)
                        review_texts = sample_reviews.get(category, sample_reviews['Sport'])
                        review_text = random.choice(review_texts)
                        
                        # Create rating document
                        rating_doc = {
                            "id": str(uuid.uuid4()),
                            "user_id": user["id"],
                            "user_name": user["name"],
                            "user_picture": user["picture"],
                            "motorcycle_id": motorcycle["id"],
                            "rating": rating,
                            "review_text": review_text,
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                        
                        # Insert rating
                        await db.ratings.insert_one(rating_doc)
                    
                    # Update motorcycle with average rating
                    average_rating = total_rating / num_ratings
                    await db.motorcycles.update_one(
                        {"id": motorcycle["id"]},
                        {
                            "$set": {
                                "average_rating": round(average_rating, 1),
                                "total_ratings": num_ratings
                            }
                        }
                    )
                    ratings_added += 1
            
            print(f"Added sample ratings to {ratings_added} motorcycles")
        except Exception as e:
            print(f"Error adding sample ratings: {str(e)}")  # Non-critical error
        
        return {
            "message": f"Successfully seeded comprehensive database with {total_inserted} motorcycles and sample ratings",
            "total_motorcycles": stats.total_motorcycles,
            "manufacturers": len(stats.manufacturers),
            "categories": len(stats.categories),
            "year_range": stats.year_range,
            "status": "Database expansion complete with sample ratings - Ready for global motorcycle enthusiasts!",
            "daily_updates": "Automated daily update system is now active and ready for GMT 00:00 schedule"
        }
        
    except Exception as e:
        logging.error(f"Error seeding database: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database seeding failed: {str(e)}")

# Status check routes (keep existing)
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

# ==================== USER REQUESTS API ENDPOINTS ====================

@api_router.post("/requests")
async def create_user_request(request_data: UserRequestCreate, current_user: User = Depends(require_auth)):
    """Submit a new user request"""
    # Create the user request
    user_request = UserRequest(
        user_id=current_user.id,
        **request_data.dict()
    )
    
    # Insert into database
    await db.user_requests.insert_one(user_request.dict())
    
    return {
        "message": "Request submitted successfully",
        "request_id": user_request.id,
        "status": "pending"
    }

@api_router.get("/requests")
async def get_user_requests(
    current_user: User = Depends(require_auth),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    status: Optional[str] = Query(None),
    request_type: Optional[str] = Query(None)
):
    """Get user's submitted requests"""
    # Build query for user's requests
    query = {"user_id": current_user.id}
    
    if status:
        query["status"] = status
    if request_type:
        query["request_type"] = request_type
    
    # Calculate pagination
    skip = (page - 1) * limit
    total_count = await db.user_requests.count_documents(query)
    
    # Get requests
    requests = await db.user_requests.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit
    has_next = page < total_pages
    has_previous = page > 1
    
    return {
        "requests": [UserRequest(**request) for request in requests],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    }

@api_router.get("/requests/stats")
async def get_request_stats(current_user: User = Depends(require_auth)):
    """Get user's request statistics"""
    # Aggregate user's request stats
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    
    status_counts = await db.user_requests.aggregate(pipeline).to_list(None)
    
    # Format the results
    stats = {
        "pending": 0,
        "in_progress": 0,
        "resolved": 0,
        "rejected": 0
    }
    
    for status_count in status_counts:
        stats[status_count["_id"]] = status_count["count"]
    
    # Get total count
    total_requests = sum(stats.values())
    
    return {
        "total_requests": total_requests,
        "by_status": stats,
        "response_rate": round((stats["resolved"] + stats["rejected"]) / total_requests * 100, 1) if total_requests > 0 else 0
    }

@api_router.get("/requests/{request_id}")
async def get_user_request(request_id: str, current_user: User = Depends(require_auth)):
    """Get a specific user request"""
    request = await db.user_requests.find_one({"id": request_id, "user_id": current_user.id})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return UserRequest(**request)

# Admin endpoints for managing user requests
@api_router.get("/admin/requests")
async def get_all_user_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    status: Optional[str] = Query(None),
    request_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None)
):
    """Get all user requests (admin only - would need admin authentication in production)"""
    
    # Build query
    query = {}
    if status:
        query["status"] = status
    if request_type:
        query["request_type"] = request_type
    if priority:
        query["priority"] = priority
    
    # Calculate pagination
    skip = (page - 1) * limit
    total_count = await db.user_requests.count_documents(query)
    
    # Get requests with user information
    pipeline = [
        {"$match": query},
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user_info"
        }},
        {"$addFields": {
            "user_name": {"$arrayElemAt": ["$user_info.name", 0]},
            "user_email": {"$arrayElemAt": ["$user_info.email", 0]}
        }},
        {"$unset": "user_info"}
    ]
    
    requests = await db.user_requests.aggregate(pipeline).to_list(limit)
    
    # Convert ObjectIds to strings for JSON serialization
    for request in requests:
        if "_id" in request:
            request["_id"] = str(request["_id"])
    
    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit
    has_next = page < total_pages
    has_previous = page > 1
    
    return {
        "requests": requests,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    }

@api_router.put("/admin/requests/{request_id}")
async def update_user_request(request_id: str, update_data: UserRequestUpdate):
    """Update a user request (admin only - would need admin authentication in production)"""
    
    request = await db.user_requests.find_one({"id": request_id})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Prepare update data
    update_fields = {}
    for field, value in update_data.dict(exclude_unset=True).items():
        if value is not None:
            update_fields[field] = value
    
    update_fields["updated_at"] = datetime.utcnow()
    
    # If status is being changed to resolved, set resolved_at
    if update_fields.get("status") == "resolved":
        update_fields["resolved_at"] = datetime.utcnow()
    
    # Update the request
    await db.user_requests.update_one(
        {"id": request_id},
        {"$set": update_fields}
    )
    
    return {"message": "Request updated successfully"}

# ==================== VIRTUAL GARAGE API ENDPOINTS ====================

@api_router.post("/garage")
async def add_to_garage(garage_data: GarageItemCreate, current_user: User = Depends(require_auth)):
    """Add motorcycle to user's virtual garage"""
    # Check if motorcycle exists
    motorcycle = await db.motorcycles.find_one({"id": garage_data.motorcycle_id})
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    # Check if already in garage
    existing = await db.garage_items.find_one({
        "user_id": current_user.id,
        "motorcycle_id": garage_data.motorcycle_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Motorcycle already in garage")
    
    # Create garage item
    garage_item = GarageItem(
        user_id=current_user.id,
        **garage_data.dict()
    )
    
    await db.garage_items.insert_one(garage_item.dict())
    return {"message": "Added to garage successfully", "id": garage_item.id}

@api_router.get("/garage")
async def get_user_garage(
    current_user: User = Depends(require_auth),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get user's virtual garage"""
    query = {"user_id": current_user.id}
    if status:
        query["status"] = status
    
    # Calculate pagination
    skip = (page - 1) * limit
    total_count = await db.garage_items.count_documents(query)
    
    # Get garage items with motorcycle details
    pipeline = [
        {"$match": query},
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": limit}
    ]
    
    garage_items_raw = await db.garage_items.aggregate(pipeline).to_list(limit)
    
    # Manually lookup motorcycle details
    garage_items = []
    for item in garage_items_raw:
        # Convert ObjectId to string if it exists
        if "_id" in item:
            item["_id"] = str(item["_id"])
        
        # Get motorcycle details
        motorcycle = await db.motorcycles.find_one({"id": item["motorcycle_id"]})
        if motorcycle:
            # Convert ObjectId to string if it exists
            if "_id" in motorcycle:
                motorcycle["_id"] = str(motorcycle["_id"])
            item["motorcycle"] = motorcycle
        
        garage_items.append(item)
    
    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit
    has_next = page < total_pages
    has_previous = page > 1
    
    return {
        "garage_items": garage_items,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    }

@api_router.put("/garage/{item_id}")
async def update_garage_item(item_id: str, update_data: GarageItemUpdate, current_user: User = Depends(require_auth)):
    """Update garage item"""
    # Check if item exists and belongs to user
    item = await db.garage_items.find_one({"id": item_id, "user_id": current_user.id})
    if not item:
        raise HTTPException(status_code=404, detail="Garage item not found")
    
    # Prepare update data
    update_fields = {}
    for field, value in update_data.dict(exclude_unset=True).items():
        if value is not None:
            update_fields[field] = value
    
    update_fields["updated_at"] = datetime.utcnow()
    
    # Update the item
    await db.garage_items.update_one(
        {"id": item_id},
        {"$set": update_fields}
    )
    
    return {"message": "Garage item updated successfully"}

@api_router.delete("/garage/{item_id}")
async def remove_from_garage(item_id: str, current_user: User = Depends(require_auth)):
    """Remove motorcycle from garage"""
    # Check if item exists and belongs to user
    result = await db.garage_items.delete_one({"id": item_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Garage item not found")
    
    return {"message": "Removed from garage successfully"}

@api_router.get("/garage/stats")
async def get_garage_stats(current_user: User = Depends(require_auth)):
    """Get user's garage statistics"""
    # Aggregate garage stats
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1}
        }}
    ]
    
    status_counts = await db.garage_items.aggregate(pipeline).to_list(None)
    
    # Format the results
    stats = {
        "owned": 0,
        "wishlist": 0,
        "previously_owned": 0,
        "test_ridden": 0
    }
    
    for status_count in status_counts:
        if status_count["_id"] in stats:
            stats[status_count["_id"]] = status_count["count"]
    
    # Get total value (for owned bikes with purchase price)
    value_pipeline = [
        {"$match": {"user_id": current_user.id, "status": "owned", "purchase_price": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": None,
            "total_value": {"$sum": "$purchase_price"}
        }}
    ]
    
    value_result = await db.garage_items.aggregate(value_pipeline).to_list(1)
    total_value = value_result[0]["total_value"] if value_result else 0
    
    return {
        "total_items": sum(stats.values()),
        "by_status": stats,
        "estimated_value": total_value
    }

# ==================== PRICE ALERTS API ENDPOINTS ====================

@api_router.post("/price-alerts")
async def create_price_alert(alert_data: PriceAlertCreate, current_user: User = Depends(require_auth)):
    """Create a price alert for a motorcycle"""
    # Check if motorcycle exists
    motorcycle = await db.motorcycles.find_one({"id": alert_data.motorcycle_id})
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    # Check if user already has an alert for this motorcycle
    existing = await db.price_alerts.find_one({
        "user_id": current_user.id,
        "motorcycle_id": alert_data.motorcycle_id,
        "is_active": True
    })
    if existing:
        raise HTTPException(status_code=400, detail="Price alert already exists for this motorcycle")
    
    # Create price alert
    price_alert = PriceAlert(
        user_id=current_user.id,
        **alert_data.dict()
    )
    
    await db.price_alerts.insert_one(price_alert.dict())
    return {"message": "Price alert created successfully", "id": price_alert.id}

@api_router.get("/price-alerts")
async def get_user_price_alerts(current_user: User = Depends(require_auth)):
    """Get user's price alerts"""
    # Get active price alerts with motorcycle details
    alerts_raw = await db.price_alerts.find({"user_id": current_user.id, "is_active": True}).sort("created_at", -1).to_list(None)
    
    # Manually lookup motorcycle details
    alerts = []
    for alert in alerts_raw:
        # Convert ObjectId to string if it exists
        if "_id" in alert:
            alert["_id"] = str(alert["_id"])
        
        # Get motorcycle details
        motorcycle = await db.motorcycles.find_one({"id": alert["motorcycle_id"]})
        if motorcycle:
            # Convert ObjectId to string if it exists
            if "_id" in motorcycle:
                motorcycle["_id"] = str(motorcycle["_id"])
            alert["motorcycle"] = motorcycle
        
        alerts.append(alert)
    return {"price_alerts": alerts}

@api_router.delete("/price-alerts/{alert_id}")
async def delete_price_alert(alert_id: str, current_user: User = Depends(require_auth)):
    """Delete a price alert"""
    result = await db.price_alerts.update_one(
        {"id": alert_id, "user_id": current_user.id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Price alert not found")
    
    return {"message": "Price alert deleted successfully"}

# ==================== RIDER GROUPS API ENDPOINTS ====================

@api_router.post("/rider-groups")
async def create_rider_group(group_data: RiderGroupCreate, current_user: User = Depends(require_auth)):
    """Create a new rider group"""
    # Create rider group
    rider_group = RiderGroup(
        creator_id=current_user.id,
        admin_ids=[current_user.id],  # Creator is automatically an admin
        member_ids=[current_user.id],  # Creator is automatically a member
        **group_data.dict()
    )
    
    await db.rider_groups.insert_one(rider_group.dict())
    return {"message": "Rider group created successfully", "id": rider_group.id}

@api_router.get("/rider-groups")
async def get_rider_groups(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    group_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get public rider groups with filtering"""
    query = {"is_public": True}
    
    if group_type:
        query["group_type"] = group_type
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Calculate pagination
    skip = (page - 1) * limit
    total_count = await db.rider_groups.count_documents(query)
    
    # Get groups with member counts
    pipeline = [
        {"$match": query},
        {"$sort": {"created_at": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {"$addFields": {
            "member_count": {"$size": "$member_ids"}
        }}
    ]
    
    groups_raw = await db.rider_groups.aggregate(pipeline).to_list(limit)
    
    # Convert ObjectIds to strings
    groups = []
    for group in groups_raw:
        if "_id" in group:
            group["_id"] = str(group["_id"])
        groups.append(group)
    
    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit
    has_next = page < total_pages
    has_previous = page > 1
    
    return {
        "rider_groups": groups,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous
        }
    }

@api_router.get("/rider-groups/{group_id}")
async def get_rider_group(group_id: str):
    """Get specific rider group details"""
    group = await db.rider_groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Rider group not found")
    
    # Convert ObjectId to string
    if "_id" in group:
        group["_id"] = str(group["_id"])
    
    # Add member count
    group["member_count"] = len(group.get("member_ids", []))
    
    return group

@api_router.post("/rider-groups/{group_id}/join")
async def join_rider_group(group_id: str, current_user: User = Depends(require_auth)):
    """Join a rider group"""
    group = await db.rider_groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Rider group not found")
    
    # Check if already a member
    if current_user.id in group.get("member_ids", []):
        raise HTTPException(status_code=400, detail="Already a member of this group")
    
    # Check if group is full
    max_members = group.get("max_members")
    current_members = len(group.get("member_ids", []))
    if max_members and current_members >= max_members:
        raise HTTPException(status_code=400, detail="Group is full")
    
    # Add user to group
    await db.rider_groups.update_one(
        {"id": group_id},
        {
            "$push": {"member_ids": current_user.id},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": "Successfully joined the rider group"}

@api_router.post("/rider-groups/{group_id}/leave")
async def leave_rider_group(group_id: str, current_user: User = Depends(require_auth)):
    """Leave a rider group"""
    group = await db.rider_groups.find_one({"id": group_id})
    if not group:
        raise HTTPException(status_code=404, detail="Rider group not found")
    
    # Check if user is a member
    if current_user.id not in group.get("member_ids", []):
        raise HTTPException(status_code=400, detail="Not a member of this group")
    
    # Don't allow creator to leave (they must transfer ownership first)
    if current_user.id == group.get("creator_id"):
        raise HTTPException(status_code=400, detail="Group creator cannot leave without transferring ownership")
    
    # Remove user from group
    await db.rider_groups.update_one(
        {"id": group_id},
        {
            "$pull": {
                "member_ids": current_user.id,
                "admin_ids": current_user.id  # Remove from admins too if they were one
            },
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": "Successfully left the rider group"}

@api_router.get("/users/me/rider-groups")
async def get_my_rider_groups(current_user: User = Depends(require_auth)):
    """Get current user's rider groups (member of)"""
    groups = await db.rider_groups.find({"member_ids": current_user.id}).to_list(None)
    
    # Convert ObjectIds and add member counts
    formatted_groups = []
    for group in groups:
        if "_id" in group:
            group["_id"] = str(group["_id"])
        group["member_count"] = len(group.get("member_ids", []))
        group["user_role"] = "admin" if current_user.id in group.get("admin_ids", []) else "member"
        group["is_creator"] = current_user.id == group.get("creator_id")
        formatted_groups.append(group)
    
    return {"rider_groups": formatted_groups}

# ==================== ACHIEVEMENT SYSTEM API ENDPOINTS ====================

@api_router.get("/achievements")
async def get_achievements():
    """Get all available achievements"""
    achievements = await db.achievements.find({"is_active": True}).to_list(None)
    
    # Convert ObjectIds to strings
    formatted_achievements = []
    for achievement in achievements:
        if "_id" in achievement:
            achievement["_id"] = str(achievement["_id"])
        formatted_achievements.append(achievement)
    
    return {"achievements": formatted_achievements}

@api_router.get("/users/me/achievements")
async def get_user_achievements(current_user: User = Depends(require_auth)):
    """Get current user's achievements and progress"""
    # Get user's completed achievements
    user_achievements = await db.user_achievements.find({"user_id": current_user.id}).to_list(None)
    completed_achievement_ids = [ua["achievement_id"] for ua in user_achievements if ua.get("is_completed")]
    
    # Get all achievements
    all_achievements = await db.achievements.find({"is_active": True}).to_list(None)
    
    # Calculate progress for each achievement
    achievements_with_progress = []
    for achievement in all_achievements:
        if "_id" in achievement:
            achievement["_id"] = str(achievement["_id"])
        
        # Check if user has completed this achievement
        user_achievement = next((ua for ua in user_achievements if ua["achievement_id"] == achievement["id"]), None)
        
        if user_achievement:
            achievement["completed"] = user_achievement.get("is_completed", False)
            achievement["progress"] = user_achievement.get("progress", 0)
            achievement["earned_at"] = user_achievement.get("earned_at")
        else:
            achievement["completed"] = False
            achievement["progress"] = 0
            
            # Calculate current progress based on achievement type
            progress = await calculate_user_achievement_progress(current_user.id, achievement)
            achievement["progress"] = progress
        
        achievements_with_progress.append(achievement)
    
    # Calculate user stats
    total_achievements = len(all_achievements)
    completed_count = len(completed_achievement_ids)
    total_points = sum(ua.get("points", 10) for ua in user_achievements if ua.get("is_completed"))
    
    return {
        "achievements": achievements_with_progress,
        "stats": {
            "total_achievements": total_achievements,
            "completed_count": completed_count,
            "completion_rate": round(completed_count / total_achievements * 100, 1) if total_achievements > 0 else 0,
            "total_points": total_points
        }
    }

async def calculate_user_achievement_progress(user_id: str, achievement: dict) -> int:
    """Calculate user's current progress towards an achievement"""
    requirement_type = achievement.get("requirement_type")
    requirement_field = achievement.get("requirement_field")
    requirement_value = achievement.get("requirement_value", 1)
    
    try:
        if requirement_field == "favorites":
            count = await db.favorites.count_documents({"user_id": user_id})
        elif requirement_field == "ratings":
            count = await db.ratings.count_documents({"user_id": user_id})
        elif requirement_field == "comments":
            count = await db.comments.count_documents({"user_id": user_id})
        elif requirement_field == "garage_items":
            count = await db.garage_items.count_documents({"user_id": user_id})
        elif requirement_field == "rider_groups":
            count = await db.rider_groups.count_documents({"member_ids": user_id})
        else:
            count = 0
        
        # For "count" type achievements, return current count (capped at requirement_value)
        if requirement_type == "count":
            return min(count, requirement_value)
        
        return count
    except Exception:
        return 0

@api_router.post("/achievements/check")
async def check_user_achievements(current_user: User = Depends(require_auth)):
    """Check and award new achievements for user"""
    new_achievements = []
    
    # Get all active achievements
    achievements = await db.achievements.find({"is_active": True}).to_list(None)
    
    # Get user's existing achievements
    user_achievements = await db.user_achievements.find({"user_id": current_user.id}).to_list(None)
    completed_achievement_ids = [ua["achievement_id"] for ua in user_achievements if ua.get("is_completed")]
    
    for achievement in achievements:
        # Skip if already completed
        if achievement["id"] in completed_achievement_ids:
            continue
        
        # Calculate current progress
        progress = await calculate_user_achievement_progress(current_user.id, achievement)
        requirement_value = achievement.get("requirement_value", 1)
        
        # Check if achievement should be awarded
        if progress >= requirement_value:
            # Award achievement
            user_achievement = UserAchievement(
                user_id=current_user.id,
                achievement_id=achievement["id"],
                progress=progress,
                is_completed=True
            )
            
            await db.user_achievements.insert_one(user_achievement.dict())
            new_achievements.append({
                "id": achievement["id"],
                "name": achievement["name"],
                "description": achievement["description"],
                "icon": achievement["icon"],
                "points": achievement.get("points", 10)
            })
        else:
            # Update progress if exists
            existing_ua = next((ua for ua in user_achievements if ua["achievement_id"] == achievement["id"]), None)
            if existing_ua and existing_ua.get("progress", 0) != progress:
                await db.user_achievements.update_one(
                    {"user_id": current_user.id, "achievement_id": achievement["id"]},
                    {"$set": {"progress": progress}}
                )
    
    return {
        "message": f"Checked achievements, awarded {len(new_achievements)} new achievements",
        "new_achievements": new_achievements
    }

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

async def initialize_achievements():
    """Initialize default achievements in the database"""
    try:
        # Check if achievements already exist
        existing_count = await db.achievements.count_documents({})
        if existing_count > 0:
            print(f"✅ Achievements already initialized ({existing_count} achievements)")
            return

        default_achievements = [
            # Social Achievements
            {
                "id": str(uuid.uuid4()),
                "name": "First Steps",
                "description": "Create your first favorite motorcycle",
                "icon": "⭐",
                "category": "social",
                "requirement_type": "count",
                "requirement_value": 1,
                "requirement_field": "favorites",
                "points": 10
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Motorcycle Enthusiast",
                "description": "Add 5 motorcycles to your favorites",
                "icon": "🏍️",
                "category": "social",
                "requirement_type": "count",
                "requirement_value": 5,
                "requirement_field": "favorites",
                "points": 25
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Bike Collector",
                "description": "Add 20 motorcycles to your favorites",
                "icon": "🏆",
                "category": "social",
                "requirement_type": "count",
                "requirement_value": 20,
                "requirement_field": "favorites",
                "points": 100
            },
            
            # Collection Achievements  
            {
                "id": str(uuid.uuid4()),
                "name": "Garage Owner",
                "description": "Add your first motorcycle to your virtual garage",
                "icon": "🏠",
                "category": "collection",
                "requirement_type": "count",
                "requirement_value": 1,
                "requirement_field": "garage_items",
                "points": 15
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Motorcycle Collector",
                "description": "Add 5 motorcycles to your virtual garage",
                "icon": "🚗",
                "category": "collection",
                "requirement_type": "count",
                "requirement_value": 5,
                "requirement_field": "garage_items",
                "points": 50
            },
            
            # Activity Achievements
            {
                "id": str(uuid.uuid4()),
                "name": "Reviewer",
                "description": "Rate your first motorcycle",
                "icon": "📝",
                "category": "activity",
                "requirement_type": "count",
                "requirement_value": 1,
                "requirement_field": "ratings",
                "points": 10
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Expert Reviewer",
                "description": "Rate 10 motorcycles",
                "icon": "👨‍💼",
                "category": "activity",
                "requirement_type": "count",
                "requirement_value": 10,
                "requirement_field": "ratings",
                "points": 75
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Conversationalist",
                "description": "Post your first comment",
                "icon": "💬",
                "category": "activity",
                "requirement_type": "count",
                "requirement_value": 1,
                "requirement_field": "comments",
                "points": 10
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Community Voice",
                "description": "Post 25 comments",
                "icon": "📢",
                "category": "activity",
                "requirement_type": "count",
                "requirement_value": 25,
                "requirement_field": "comments",
                "points": 150
            },
            
            # Community Achievements
            {
                "id": str(uuid.uuid4()),
                "name": "Group Joiner",
                "description": "Join your first rider group",
                "icon": "👥",
                "category": "social",
                "requirement_type": "count",
                "requirement_value": 1,
                "requirement_field": "rider_groups",
                "points": 20
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Social Rider",
                "description": "Join 3 rider groups",
                "icon": "🤝",
                "category": "social",
                "requirement_type": "count",
                "requirement_value": 3,
                "requirement_field": "rider_groups",
                "points": 75
            }
        ]

        # Add created_at and is_active to each achievement
        for achievement in default_achievements:
            achievement["created_at"] = datetime.utcnow()
            achievement["is_active"] = True

        # Insert achievements
        await db.achievements.insert_many(default_achievements)
        print(f"✅ Initialized {len(default_achievements)} default achievements")

    except Exception as e:
        print(f"⚠️ Error initializing achievements: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Initialize achievements
        await initialize_achievements()
        
        # Start the daily update scheduler
        daily_scheduler.start_scheduler()
        print("🚀 Application startup completed with daily scheduler and achievements")
    except Exception as e:
        print(f"⚠️ Startup warning: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        # Stop the daily update scheduler
        daily_scheduler.stop_scheduler()
        print("🛑 Application shutdown completed")
    except Exception as e:
        print(f"⚠️ Shutdown warning: {str(e)}")
    
    # Close database connection
    client.close()

# Test endpoint for manual daily updates
@api_router.post("/admin/run-daily-update")
async def trigger_daily_update():
    """Manually trigger daily updates (for testing)"""
    try:
        await daily_scheduler.run_daily_updates()
        return {"message": "Daily update completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Daily update failed: {str(e)}")

# Get daily update logs
@api_router.get("/admin/update-logs")
async def get_update_logs(limit: int = 10):
    """Get recent daily update logs"""
    try:
        logs = await db.update_logs.find({}).sort("timestamp", -1).limit(limit).to_list(limit)
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch update logs: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)