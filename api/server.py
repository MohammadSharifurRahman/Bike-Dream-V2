import bcrypt
from fastapi import FastAPI, APIRouter, HTTPException, Query, BackgroundTasks, Depends, Header, Request, Body
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
    role: str = Field(default="User")  # "Admin", "Moderator", or "User"
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

# Phase 3: Scrolling Banner Models
class Banner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str = Field(min_length=1, max_length=500)
    is_active: bool = Field(default=True)
    priority: int = Field(default=0)  # Higher priority banners show first
    created_by: str  # Admin user ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    starts_at: Optional[datetime] = None  # Optional scheduled start
    ends_at: Optional[datetime] = None    # Optional scheduled end

class BannerCreate(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    priority: int = Field(default=0, ge=0, le=100)
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None

class BannerUpdate(BaseModel):
    message: Optional[str] = Field(None, min_length=1, max_length=500)
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0, le=100)
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None

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
    user_id: Optional[str] = None  # If user is logged in
    user_email: Optional[str] = None  # If provided
    request_type: str  # "add_vendor", "add_manufacturer", "regional_availability", "feature_request", "bug_report", "other"
    category: Optional[str] = None  # For categorization
    title: str  # Brief title/summary
    content: str  # Detailed request content
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    status: str = "pending"  # "pending", "reviewed", "in_progress", "completed", "rejected"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    admin_notes: Optional[str] = None  # For admin use

class UserRequestCreate(BaseModel):
    user_email: Optional[EmailStr] = None
    request_type: str = Field(pattern="^(add_vendor|add_manufacturer|regional_availability|feature_request|bug_report|other)$")
    category: Optional[str] = None
    title: str = Field(min_length=5, max_length=200)
    content: str = Field(min_length=10, max_length=2000)
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")

class UserRequestUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|reviewed|in_progress|completed|rejected)$")
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    admin_notes: Optional[str] = Field(None, max_length=1000)

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

# Search Analytics Models for User Engagement Tracking
class SearchAnalytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None  # None for anonymous users
    session_id: Optional[str] = None
    search_term: str
    search_type: str = "general"  # "general", "manufacturer", "category", "price_range"
    filters_applied: dict = Field(default_factory=dict)
    results_count: int = 0
    user_location: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    clicked_results: List[str] = Field(default_factory=list)  # motorcycle IDs that were clicked

class UserEngagement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: str
    page_view: str  # page visited
    time_spent: Optional[int] = None  # seconds spent on page
    actions: List[dict] = Field(default_factory=list)  # user actions like clicks, favorites, etc.
    referrer: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

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

# Phase 3: Role-Based Access Control (RBAC) helpers
async def require_admin(current_user: User = Depends(require_auth)):
    """Require Admin role"""
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def require_admin_or_moderator(current_user: User = Depends(require_auth)):
    """Require Admin or Moderator role"""
    if current_user.role not in ["Admin", "Moderator"]:
        raise HTTPException(status_code=403, detail="Admin or Moderator access required")
    return current_user

async def get_user_role(current_user: User = Depends(get_current_user)):
    """Get user role (returns 'User' for unauthenticated users)"""
    return current_user.role if current_user else "User"

# Helper function for optional auth
async def get_current_user_optional(request: Request) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        return await get_current_user(authorization=auth_header)
    except:
        return None

# Helper function for admin auth
async def get_current_admin_user(authorization: str = Header(None)) -> User:
    """Get current admin user"""
    user = await get_current_user(authorization=authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    if user.role != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@api_router.post("/admin/requests/cleanup")
async def cleanup_old_requests(
    days: int = Query(90, description="Keep requests newer than this many days"),
    current_user: User = Depends(get_current_admin_user)
):
    """Clean up old requests (Admin only) - maintains 90-day rolling archive"""
    try:
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Count requests to be deleted
        delete_query = {"created_at": {"$lt": cutoff_date}}
        count_to_delete = await db.user_requests.count_documents(delete_query)
        
        # Delete old requests
        result = await db.user_requests.delete_many(delete_query)
        
        return {
            "message": f"Cleanup completed successfully",
            "requests_deleted": result.deleted_count,
            "archive_days": days,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup old requests")

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

# Phase 3: Scrolling Text Banner Management API
@api_router.get("/banners")
async def get_active_banners():
    """Get all active banners for public display (no authentication required)"""
    try:
        current_time = datetime.utcnow()
        
        # Query for active banners with optional time filtering
        query = {
            "is_active": True,
            "$or": [
                {"starts_at": None},
                {"starts_at": {"$lte": current_time}}
            ],
            "$or": [  
                {"ends_at": None},
                {"ends_at": {"$gte": current_time}}
            ]
        }
        
        banners_cursor = db.banners.find(query).sort("priority", -1).limit(10)
        banners = await banners_cursor.to_list(10)
        
        # Format banners for frontend
        formatted_banners = []
        for banner in banners:
            formatted_banners.append({
                "id": banner["id"],
                "message": banner["message"],
                "priority": banner["priority"],
                "created_at": banner["created_at"].isoformat() if banner.get("created_at") else None
            })
        
        return {
            "banners": formatted_banners,
            "total_count": len(formatted_banners),
            "last_updated": current_time.isoformat()
        }
        
    except Exception as e:
        print(f"Error fetching active banners: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch banners: {str(e)}")

@api_router.get("/admin/banners")
async def get_all_banners(admin_user: User = Depends(require_admin_or_moderator)):
    """Get all banners for admin management (Admin/Moderator only)"""
    try:
        banners_cursor = db.banners.find({}).sort("created_at", -1)
        banners = await banners_cursor.to_list(100)
        
        # Format banners for JSON serialization
        formatted_banners = []
        for banner in banners:
            formatted_banners.append({
                "id": banner["id"],
                "message": banner["message"],
                "is_active": banner["is_active"],
                "priority": banner["priority"],
                "created_by": banner["created_by"],
                "created_at": banner["created_at"].isoformat() if banner.get("created_at") else None,
                "updated_at": banner["updated_at"].isoformat() if banner.get("updated_at") else None,
                "starts_at": banner["starts_at"].isoformat() if banner.get("starts_at") else None,
                "ends_at": banner["ends_at"].isoformat() if banner.get("ends_at") else None
            })
        
        return {
            "banners": formatted_banners,
            "total_count": len(formatted_banners)
        }
        
    except Exception as e:
        print(f"Error fetching admin banners: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch admin banners: {str(e)}")

@api_router.post("/admin/banners")
async def create_banner(banner_data: BannerCreate, admin_user: User = Depends(require_admin_or_moderator)):
    """Create new banner (Admin/Moderator only)"""
    try:
        # Validate time ranges
        if banner_data.starts_at and banner_data.ends_at:
            if banner_data.starts_at >= banner_data.ends_at:
                raise HTTPException(status_code=400, detail="Start time must be before end time")
        
        # Create banner
        banner = Banner(
            **banner_data.dict(),
            created_by=admin_user.id
        )
        
        banner_dict = banner.dict()
        await db.banners.insert_one(banner_dict)
        
        # Format response banner for JSON serialization
        response_banner = {
            "id": banner.id,
            "message": banner.message,
            "is_active": banner.is_active,
            "priority": banner.priority,
            "created_by": banner.created_by,
            "created_at": banner.created_at.isoformat() if banner.created_at else None,
            "updated_at": banner.updated_at.isoformat() if banner.updated_at else None,
            "starts_at": banner.starts_at.isoformat() if banner.starts_at else None,
            "ends_at": banner.ends_at.isoformat() if banner.ends_at else None
        }
        
        return {
            "message": "Banner created successfully",
            "banner": response_banner
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating banner: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create banner: {str(e)}")

@api_router.put("/admin/banners/{banner_id}")
async def update_banner(banner_id: str, banner_update: BannerUpdate, admin_user: User = Depends(require_admin_or_moderator)):
    """Update banner (Admin/Moderator only)"""
    try:
        # Check if banner exists
        banner = await db.banners.find_one({"id": banner_id})
        if not banner:
            raise HTTPException(status_code=404, detail="Banner not found")
        
        # Prepare update data
        update_data = {}
        if banner_update.message is not None:
            update_data["message"] = banner_update.message
        if banner_update.is_active is not None:
            update_data["is_active"] = banner_update.is_active
        if banner_update.priority is not None:
            update_data["priority"] = banner_update.priority
        if banner_update.starts_at is not None:
            update_data["starts_at"] = banner_update.starts_at
        if banner_update.ends_at is not None:
            update_data["ends_at"] = banner_update.ends_at
        
        # Validate time ranges if both are being updated
        if "starts_at" in update_data and "ends_at" in update_data:
            if update_data["starts_at"] and update_data["ends_at"]:
                if update_data["starts_at"] >= update_data["ends_at"]:
                    raise HTTPException(status_code=400, detail="Start time must be before end time")
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update banner
        result = await db.banners.update_one(
            {"id": banner_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Banner not found")
        
        # Return updated banner
        updated_banner = await db.banners.find_one({"id": banner_id})
        
        # Format updated banner for JSON serialization
        response_banner = {
            "id": updated_banner["id"],
            "message": updated_banner["message"],
            "is_active": updated_banner["is_active"],
            "priority": updated_banner["priority"],
            "created_by": updated_banner["created_by"],
            "created_at": updated_banner["created_at"].isoformat() if updated_banner.get("created_at") else None,
            "updated_at": updated_banner["updated_at"].isoformat() if updated_banner.get("updated_at") else None,
            "starts_at": updated_banner["starts_at"].isoformat() if updated_banner.get("starts_at") else None,
            "ends_at": updated_banner["ends_at"].isoformat() if updated_banner.get("ends_at") else None
        }
        
        return {
            "message": "Banner updated successfully",
            "banner": response_banner
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating banner: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update banner: {str(e)}")

@api_router.delete("/admin/banners/{banner_id}")
async def delete_banner(banner_id: str, admin_user: User = Depends(require_admin_or_moderator)):
    """Delete banner (Admin/Moderator only)"""
    try:
        result = await db.banners.delete_one({"id": banner_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Banner not found")
        
        return {
            "message": "Banner deleted successfully",
            "banner_id": banner_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting banner: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete banner: {str(e)}")

# Test endpoint for making a user admin (for testing purposes only)
@api_router.post("/test/make-admin")
async def make_user_admin(request: dict):
    """Test endpoint to make a user admin (for testing purposes only)"""
    try:
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Update user role to Admin
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": {"role": "Admin"}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User role updated to Admin successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")

# Test endpoint for deleting users (for testing purposes only)
@api_router.delete("/test/delete-user")
async def delete_test_user(request: dict):
    """Test endpoint to delete a user (for testing purposes only)"""
    try:
        email = request.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="email is required")
        
        # Delete user
        result = await db.users.delete_one({"email": email})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

# Phase 3: Admin Dashboard APIs
@api_router.get("/admin/users")
async def get_all_users(admin_user: User = Depends(require_admin)):
    """Get all users for admin management (Admin only)"""
    try:
        users_cursor = db.users.find({}).sort("created_at", -1)
        users = await users_cursor.to_list(1000)
        
        # Remove sensitive information
        safe_users = []
        for user in users:
            safe_user = {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user.get("role", "User"),
                "auth_method": user.get("auth_method", "password"),
                "created_at": user["created_at"],
                "favorite_count": len(user.get("favorite_motorcycles", []))
            }
            safe_users.append(safe_user)
        
        return {
            "users": safe_users,
            "total_count": len(safe_users)
        }
        
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@api_router.put("/admin/users/{user_id}/role")
async def update_user_role(user_id: str, new_role: str, admin_user: User = Depends(require_admin)):
    """Update user role (Admin only)"""
    try:
        if new_role not in ["Admin", "Moderator", "User"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be Admin, Moderator, or User")
        
        # Prevent admin from demoting themselves
        if user_id == admin_user.id and new_role != "Admin":
            raise HTTPException(status_code=400, detail="Cannot change your own admin role")
        
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": {"role": new_role, "updated_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "message": f"User role updated to {new_role}",
            "user_id": user_id,
            "new_role": new_role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating user role: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")

@api_router.get("/admin/stats")
async def get_admin_stats(admin_user: User = Depends(require_admin_or_moderator)):
    """Get admin dashboard statistics (Admin/Moderator only)"""
    try:
        # Get various counts
        total_users = await db.users.count_documents({})
        total_motorcycles = await db.motorcycles.count_documents({})
        total_comments = await db.comments.count_documents({})
        total_ratings = await db.ratings.count_documents({})
        total_banners = await db.banners.count_documents({})
        active_banners = await db.banners.count_documents({"is_active": True})
        
        # Get user role distribution
        role_pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        role_cursor = db.users.aggregate(role_pipeline)
        role_distribution = await role_cursor.to_list(10)
        
        # Get recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_users = await db.users.count_documents({"created_at": {"$gte": seven_days_ago}})
        recent_comments = await db.comments.count_documents({"created_at": {"$gte": seven_days_ago}})
        recent_ratings = await db.ratings.count_documents({"created_at": {"$gte": seven_days_ago}})
        
        return {
            "total_stats": {
                "total_users": total_users,
                "total_motorcycles": total_motorcycles,
                "total_comments": total_comments,
                "total_ratings": total_ratings,
                "total_banners": total_banners,
                "active_banners": active_banners
            },
            "role_distribution": {item["_id"]: item["count"] for item in role_distribution},
            "recent_activity": {
                "new_users_7d": recent_users,
                "new_comments_7d": recent_comments,
                "new_ratings_7d": recent_ratings
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating admin stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate admin stats: {str(e)}")

# Search Auto-suggestions API endpoint
@api_router.get("/motorcycles/search/suggestions")
async def get_search_suggestions(q: str = Query(..., min_length=1, description="Search query"), limit: int = Query(10, le=20)):
    """Get autocomplete suggestions for motorcycle search - searches both motorcycle names and brand names"""
    try:
        if not q or len(q.strip()) < 1:
            return {"suggestions": []}
        
        search_term = q.strip().lower()
        
        # Create regex pattern for case-insensitive search
        regex_pattern = {"$regex": search_term, "$options": "i"}
        
        # Search across motorcycle model names and manufacturers
        search_pipeline = [
            {
                "$match": {
                    "$or": [
                        {"model": regex_pattern},
                        {"manufacturer": regex_pattern}
                    ]
                }
            },
            {
                "$group": {
                    "_id": {
                        "type": {
                            "$cond": [
                                {"$regexMatch": {"input": "$manufacturer", "regex": search_term, "options": "i"}},
                                "manufacturer",
                                "model"
                            ]
                        },
                        "value": {
                            "$cond": [
                                {"$regexMatch": {"input": "$manufacturer", "regex": search_term, "options": "i"}},
                                "$manufacturer",
                                "$model"
                            ]
                        }
                    },
                    "count": {"$sum": 1},
                    "sample_model": {"$first": "$model"},
                    "sample_manufacturer": {"$first": "$manufacturer"}
                }
            },
            {
                "$project": {
                    "type": "$_id.type",
                    "value": "$_id.value",
                    "count": 1,
                    "display_text": {
                        "$cond": [
                            {"$eq": ["$_id.type", "manufacturer"]},
                            {"$concat": ["$_id.value", " (", {"$toString": "$count"}, " models)"]},
                            {"$concat": ["$_id.value", " (", "$sample_manufacturer", ")"]}
                        ]
                    },
                    "_id": 0
                }
            },
            {"$sort": {"count": -1, "value": 1}},
            {"$limit": limit}
        ]
        
        suggestions_cursor = db.motorcycles.aggregate(search_pipeline)
        suggestions = await suggestions_cursor.to_list(limit)
        
        # Format suggestions for frontend
        formatted_suggestions = []
        for suggestion in suggestions:
            formatted_suggestions.append({
                "value": suggestion["value"],
                "type": suggestion["type"],  # "manufacturer" or "model"
                "display_text": suggestion["display_text"],
                "count": suggestion["count"]
            })
        
        return {
            "query": q,
            "suggestions": formatted_suggestions,
            "total": len(formatted_suggestions)
        }
        
    except Exception as e:
        print(f"Error in search suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch search suggestions: {str(e)}")

# Motorcycle Comparison API endpoint
@api_router.post("/motorcycles/compare")
async def compare_motorcycles(motorcycle_ids: list[str] = Body(..., description="List of motorcycle IDs to compare (max 3)")):
    """Compare up to 3 motorcycles side-by-side with detailed specs, pricing, and ratings"""
    try:
        # Validate input
        if not motorcycle_ids or len(motorcycle_ids) == 0:
            raise HTTPException(status_code=400, detail="At least one motorcycle ID is required")
        
        if len(motorcycle_ids) > 3:
            raise HTTPException(status_code=400, detail="Maximum 3 motorcycles can be compared at once")
        
        # Remove duplicates while preserving order
        unique_ids = []
        seen = set()
        for id in motorcycle_ids:
            if id not in seen:
                unique_ids.append(id)
                seen.add(id)
        
        # Fetch motorcycles from database
        comparison_data = []
        for motorcycle_id in unique_ids:
            motorcycle = await db.motorcycles.find_one({"id": motorcycle_id})
            if not motorcycle:
                raise HTTPException(status_code=404, detail=f"Motorcycle with ID '{motorcycle_id}' not found")
            
            # Get vendor pricing for this motorcycle
            try:
                vendor_pricing_data = vendor_pricing.get_vendor_prices(motorcycle, "US")
            except Exception as e:
                print(f"Warning: Could not fetch vendor pricing for {motorcycle_id}: {str(e)}")
                vendor_pricing_data = []
            
            # Get ratings and comments count
            ratings_pipeline = [
                {"$match": {"motorcycle_id": motorcycle_id}},
                {"$group": {
                    "_id": None,
                    "average_rating": {"$avg": "$rating"},
                    "total_ratings": {"$sum": 1},
                    "rating_distribution": {
                        "$push": "$rating"
                    }
                }}
            ]
            
            rating_result = await db.ratings.aggregate(ratings_pipeline).to_list(1)
            rating_data = rating_result[0] if rating_result else {
                "average_rating": 0,
                "total_ratings": 0,
                "rating_distribution": []
            }
            
            # Calculate rating distribution
            rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for rating in rating_data.get("rating_distribution", []):
                if rating in rating_counts:
                    rating_counts[rating] += 1
            
            # Get comments count
            comments_count = await db.comments.count_documents({"motorcycle_id": motorcycle_id})
            
            # Prepare comparison data
            comparison_item = {
                "id": motorcycle["id"],
                "manufacturer": motorcycle["manufacturer"],
                "model": motorcycle["model"],
                "year": motorcycle["year"],
                "category": motorcycle["category"],
                "image_url": motorcycle.get("image_url", ""),
                "description": motorcycle.get("description", ""),
                
                # Technical Specifications
                "technical_specs": {
                    "engine_displacement_cc": motorcycle.get("engine_displacement_cc"),
                    "horsepower": motorcycle.get("horsepower"),
                    "torque_nm": motorcycle.get("torque_nm"),
                    "top_speed_kmh": motorcycle.get("top_speed_kmh"),
                    "weight_kg": motorcycle.get("weight_kg"),
                    "fuel_capacity_liters": motorcycle.get("fuel_capacity_liters"),
                    "mileage_kmpl": motorcycle.get("mileage_kmpl"),
                    "seat_height_mm": motorcycle.get("seat_height_mm"),
                    "ground_clearance_mm": motorcycle.get("ground_clearance_mm"),
                    "wheelbase_mm": motorcycle.get("wheelbase_mm"),
                    "wheel_size_inches": motorcycle.get("wheel_size_inches")
                },
                
                # Features and Technology
                "features": {
                    "transmission_type": motorcycle.get("transmission_type"),
                    "engine_type": motorcycle.get("engine_type"),
                    "cooling_system": motorcycle.get("cooling_system"),
                    "braking_system": motorcycle.get("braking_system"),
                    "suspension_type": motorcycle.get("suspension_type"),
                    "tyre_type": motorcycle.get("tyre_type"),
                    "headlight_type": motorcycle.get("headlight_type"),
                    "fuel_type": motorcycle.get("fuel_type"),
                    "abs_available": motorcycle.get("abs_available"),
                    "specialisations": motorcycle.get("specialisations", [])
                },
                
                # Pricing and Availability
                "pricing": {
                    "base_price_usd": motorcycle.get("base_price_usd"),
                    "price_range": motorcycle.get("price_range"),
                    "availability": motorcycle.get("availability"),
                    "vendor_pricing": {"vendors": vendor_pricing_data, "message": "Pricing data available" if vendor_pricing_data else "Pricing data unavailable"}
                },
                
                # Ratings and Reviews
                "ratings": {
                    "average_rating": round(rating_data["average_rating"], 1) if rating_data["average_rating"] else 0,
                    "total_ratings": rating_data["total_ratings"],
                    "rating_distribution": rating_counts,
                    "comments_count": comments_count
                },
                
                # Additional Metadata
                "metadata": {
                    "production_years": motorcycle.get("production_years", []),
                    "country_of_origin": motorcycle.get("country_of_origin"),
                    "market_segment": motorcycle.get("market_segment"),
                    "user_interest_score": motorcycle.get("user_interest_score", 0),
                    "last_updated": motorcycle.get("updated_at")
                }
            }
            
            comparison_data.append(comparison_item)
        
        return {
            "comparison_id": f"comp_{int(time.time())}",
            "motorcycles": comparison_data,
            "comparison_count": len(comparison_data),
            "generated_at": datetime.utcnow().isoformat(),
            "comparison_categories": [
                "Technical Specifications",
                "Features & Technology", 
                "Pricing & Availability",
                "Ratings & Reviews",
                "Additional Information"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in motorcycle comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to compare motorcycles: {str(e)}")

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
async def get_database_stats(
    hide_unavailable: Optional[bool] = Query(False, description="Hide discontinued and unavailable motorcycles"),
    region: Optional[str] = Query(None, description="Filter by region availability (country code)")
):
    """Get comprehensive database statistics with optional filtering"""
    # Build base query
    query = {}
    
    # Add hide unavailable filter if requested
    if hide_unavailable:
        query["availability"] = {"$nin": ["Discontinued", "Not Available", "Out of Stock", "Collector Item"]}
    
    # Add region filter if requested
    if region:
        region_manufacturers = {
            "US": ["Harley-Davidson", "Indian", "Kawasaki", "Yamaha", "Honda", "Suzuki", "Ducati"],
            "IN": ["Hero", "Bajaj", "TVS", "Royal Enfield", "Honda", "Yamaha", "Suzuki", "KTM"],
            "JP": ["Honda", "Yamaha", "Suzuki", "Kawasaki"],
            "DE": ["BMW", "KTM", "Ducati", "Honda", "Yamaha"],
            "GB": ["Triumph", "Honda", "Yamaha", "Suzuki", "Kawasaki"],
            "IT": ["Ducati", "MV Agusta", "Aprilia", "Honda", "Yamaha"],
            "AU": ["Honda", "Yamaha", "Suzuki", "Kawasaki", "BMW"],
        }
        
        if region in region_manufacturers:
            query["manufacturer"] = {"$in": region_manufacturers[region]}
    
    # Get filtered total count
    total = await db.motorcycles.count_documents(query)
    
    # Get filtered manufacturers
    manufacturers_pipeline = [
        {"$match": query},
        {"$group": {"_id": "$manufacturer"}}, 
        {"$sort": {"_id": 1}}
    ]
    
    # Get filtered categories  
    categories_pipeline = [
        {"$match": query},
        {"$group": {"_id": "$category"}}, 
        {"$sort": {"_id": 1}}
    ]
    
    manufacturers = await db.motorcycles.aggregate(manufacturers_pipeline).to_list(None)
    categories = await db.motorcycles.aggregate(categories_pipeline).to_list(None)
    
    # Get year range from filtered results
    year_range = await db.motorcycles.aggregate([
        {"$match": query},
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
    hide_unavailable: Optional[bool] = Query(False, description="Hide discontinued and unavailable motorcycles"),
    
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
    region: Optional[str] = Query(None, description="Filter by region availability (country code)")
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
    
    # Hide unavailable motorcycles filter
    if hide_unavailable:
        query["availability"] = {"$nin": ["Discontinued", "Not Available", "Out of Stock", "Collector Item"]}
    
    # Region-based filtering (consistent with stats API)
    if region:
        # Filter by manufacturers commonly available in specific regions
        region_manufacturers = {
            "US": ["Harley-Davidson", "Indian", "Kawasaki", "Yamaha", "Honda", "Suzuki", "Ducati"],
            "IN": ["Hero", "Bajaj", "TVS", "Royal Enfield", "Honda", "Yamaha", "Suzuki", "KTM"],
            "JP": ["Honda", "Yamaha", "Suzuki", "Kawasaki"],
            "DE": ["BMW", "KTM", "Ducati", "Honda", "Yamaha"],
            "GB": ["Triumph", "Honda", "Yamaha", "Suzuki", "Kawasaki"],
            "IT": ["Ducati", "MV Agusta", "Aprilia", "Honda", "Yamaha"],
            "AU": ["Honda", "Yamaha", "Suzuki", "Kawasaki", "BMW"],
        }
        
        if region in region_manufacturers:
            # Filter motorcycles by manufacturers commonly available in this region
            query["manufacturer"] = {"$in": region_manufacturers[region]}
        # If region not specifically mapped, show all motorcycles (no additional filter)
    
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
async def get_categories_summary(
    hide_unavailable: Optional[bool] = Query(False, description="Hide discontinued and unavailable motorcycles"),
    region: Optional[str] = Query(None, description="Filter by region availability (country code)")
):
    """Get categories with top motorcycles by user interest for homepage - shows unique models only"""
    categories = ["Sport", "Cruiser", "Touring", "Adventure", "Naked", "Vintage", "Electric", "Scooter", "Standard", "Enduro", "Motocross"]
    
    category_summaries = []
    for category in categories:
        # Base query for this category
        base_query = {"category": {"$regex": category, "$options": "i"}}
        
        # Add hide unavailable filter if requested
        if hide_unavailable:
            base_query["availability"] = {"$nin": ["Discontinued", "Not Available", "Out of Stock", "Collector Item"]}
        
        # Add region filter if requested
        if region:
            region_manufacturers = {
                "US": ["Harley-Davidson", "Indian", "Kawasaki", "Yamaha", "Honda", "Suzuki", "Ducati"],
                "IN": ["Hero", "Bajaj", "TVS", "Royal Enfield", "Honda", "Yamaha", "Suzuki", "KTM"],
                "JP": ["Honda", "Yamaha", "Suzuki", "Kawasaki"],
                "DE": ["BMW", "KTM", "Ducati", "Honda", "Yamaha"],
                "GB": ["Triumph", "Honda", "Yamaha", "Suzuki", "Kawasaki"],
                "IT": ["Ducati", "MV Agusta", "Aprilia", "Honda", "Yamaha"],
                "AU": ["Honda", "Yamaha", "Suzuki", "Kawasaki", "BMW"],
            }
            
            if region in region_manufacturers:
                base_query["manufacturer"] = {"$in": region_manufacturers[region]}
        
        # Get count for this category
        count = await db.motorcycles.count_documents(base_query)
        
        # Get unique models with lowest prices - use aggregation to group by manufacturer + model
        featured_pipeline = [
            {"$match": base_query},
            {
                "$group": {
                    "_id": {
                        "manufacturer": "$manufacturer", 
                        "model": "$model"
                    },
                    "motorcycle": {"$first": "$$ROOT"},  # Get first document
                    "lowest_price": {"$min": "$price_usd"},  # Track lowest price
                    "user_interest_score": {"$max": "$user_interest_score"}  # Use highest interest score
                }
            },
            {
                "$replaceRoot": {
                    "newRoot": {
                        "$mergeObjects": [
                            "$motorcycle",
                            {"price_usd": "$lowest_price"}  # Use the lowest price
                        ]
                    }
                }
            },
            {"$sort": {"user_interest_score": -1}},  # Sort by user interest
            {"$limit": 3}
        ]
        
        featured_results = await db.motorcycles.aggregate(featured_pipeline).to_list(3)
        
        if featured_results:  # Only include categories that have motorcycles
            category_summary = CategorySummary(
                category=category,
                count=count,
                featured_motorcycles=[Motorcycle(**moto) for moto in featured_results]
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

@api_router.post("/motorcycles/seed/ratings")
async def seed_ratings_only():
    """Add sample ratings to existing motorcycles in the database"""
    try:
        # Sample users for ratings
        sample_users = [
            {"id": "user_1", "name": "Alex Thompson", "picture": "https://ui-avatars.com/api/?name=Alex+Thompson&background=random"},
            {"id": "user_2", "name": "Sarah Chen", "picture": "https://ui-avatars.com/api/?name=Sarah+Chen&background=random"},
            {"id": "user_3", "name": "Mike Rodriguez", "picture": "https://ui-avatars.com/api/?name=Mike+Rodriguez&background=random"},
            {"id": "user_4", "name": "Emma Wilson", "picture": "https://ui-avatars.com/api/?name=Emma+Wilson&background=random"},
            {"id": "user_5", "name": "David Kumar", "picture": "https://ui-avatars.com/api/?name=David+Kumar&background=random"},
            {"id": "user_6", "name": "Lisa Johnson", "picture": "https://ui-avatars.com/api/?name=Lisa+Johnson&background=random"},
            {"id": "user_7", "name": "Chris Park", "picture": "https://ui-avatars.com/api/?name=Chris+Park&background=random"},
            {"id": "user_8", "name": "Anna Kowalski", "picture": "https://ui-avatars.com/api/?name=Anna+Kowalski&background=random"}
        ]
        
        # Sample reviews by category
        sample_reviews = {
            'Sport': [
                "Incredible acceleration and handling! Perfect for track days.",
                "Amazing power delivery and cornering capabilities.",
                "Outstanding performance bike with excellent build quality.",
                "Love the aggressive styling and responsive engine.",
                "Great for experienced riders who want pure performance."
            ],
            'Cruiser': [
                "Comfortable for long rides with great build quality.",
                "Perfect touring bike with excellent comfort.",
                "Smooth ride and classic styling that never gets old.",
                "Great for highway cruising and weekend trips.",
                "Reliable and comfortable with that classic rumble."
            ],
            'Adventure': [
                "Perfect for both on-road and off-road adventures.",
                "Great versatility and excellent suspension travel.",
                "Comfortable upright position for long distance touring.",
                "Handles well both on pavement and gravel roads.",
                "Excellent bike for exploring remote destinations."
            ]
        }
        
        # Get existing motorcycles without ratings
        motorcycles_without_ratings = await db.motorcycles.find({
            "$or": [
                {"total_ratings": {"$eq": 0}},
                {"total_ratings": {"$exists": False}},
                {"average_rating": {"$eq": 0}},
                {"average_rating": {"$exists": False}}
            ]
        }).to_list(2000)
        
        print(f"Found {len(motorcycles_without_ratings)} motorcycles without ratings")
        
        import random
        ratings_added = 0
        ratings_inserted = 0
        
        for motorcycle in motorcycles_without_ratings:
            if random.random() < 0.6:  # 60% chance to get ratings
                try:
                    category = motorcycle.get('category', 'Sport')
                    
                    # Generate 1-5 ratings for this motorcycle
                    num_ratings = random.randint(1, 5)
                    total_rating = 0
                    
                    for i in range(num_ratings):
                        # Generate rating (biased towards higher ratings: 3-5 stars)
                        # Use weighted random selection - more 4s and 5s
                        rating_options = [3, 4, 4, 4, 5, 5, 5, 5]  # Weighted towards higher ratings
                        rating = random.choice(rating_options)
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
                        
                        # Insert rating with error handling
                        try:
                            await db.ratings.insert_one(rating_doc)
                            ratings_inserted += 1
                        except Exception as e:
                            print(f"Error inserting rating: {str(e)}")
                            continue
                    
                    # Update motorcycle with average rating
                    average_rating = total_rating / num_ratings
                    try:
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
                    except Exception as e:
                        print(f"Error updating motorcycle {motorcycle['id']}: {str(e)}")
                        continue
                        
                except Exception as e:
                    print(f"Error processing motorcycle {motorcycle.get('id', 'unknown')}: {str(e)}")
                    continue
        
        return {
            "message": f"Successfully added sample ratings to {ratings_added} motorcycles",
            "motorcycles_processed": len(motorcycles_without_ratings),
            "ratings_added": ratings_added,
            "ratings_inserted": ratings_inserted,
            "status": "Sample ratings seeding complete!"
        }
        
    except Exception as e:
        logging.error(f"Error seeding ratings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Rating seeding failed: {str(e)}")

@api_router.post("/motorcycles/update-authentic-images")
async def update_authentic_images():
    """Update motorcycles with authentic, working motorcycle images"""
    try:
        # High-quality, authentic motorcycle images that will actually load
        authentic_images = {
            # General motorcycles - high quality Unsplash images
            "sport": [
                "https://images.unsplash.com/photo-1591637333184-19aa84b3e01f?w=400&h=250&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1531327431456-837da4b1d562?w=400&h=250&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=400&h=250&fit=crop&auto=format",
                "https://images.pexels.com/photos/1416169/pexels-photo-1416169.jpeg?w=400&h=250&fit=crop&auto=format",
            ],
            "cruiser": [
                "https://images.unsplash.com/photo-1659465493788-046d031bcd35?w=400&h=250&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1653554919017-fb4a40f7364b?w=400&h=250&fit=crop&auto=format",
                "https://images.pexels.com/photos/33222522/pexels-photo-33222522.jpeg?w=400&h=250&fit=crop&auto=format",
                "https://images.pexels.com/photos/2116475/pexels-photo-2116475.jpeg?w=400&h=250&fit=crop&auto=format",
            ],
            "royal_enfield": [
                "https://images.unsplash.com/photo-1694271558638-7a6f4c8879b0?w=400&h=250&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1694956792421-e946fff94564?w=400&h=250&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1675233262719-6b2309a2e751?w=400&h=250&fit=crop&auto=format",
                "https://images.pexels.com/photos/1033116/pexels-photo-1033116.jpeg?w=400&h=250&fit=crop&auto=format",
            ],
            "commuter": [
                "https://images.pexels.com/photos/2629412/pexels-photo-2629412.jpeg?w=400&h=250&fit=crop&auto=format",
                "https://images.pexels.com/photos/33215447/pexels-photo-33215447.jpeg?w=400&h=250&fit=crop&auto=format",
                "https://images.unsplash.com/photo-1591637333184-19aa84b3e01f?w=400&h=250&fit=crop&auto=format",
                "https://images.pexels.com/photos/1416169/pexels-photo-1416169.jpeg?w=400&h=250&fit=crop&auto=format",
            ]
        }
        
        import random
        updated_count = 0
        
        # Get all motorcycles
        all_motorcycles = await db.motorcycles.find({}).to_list(None)
        
        for motorcycle in all_motorcycles:
            manufacturer = motorcycle.get('manufacturer', '').lower()
            category = motorcycle.get('category', '').lower()
            
            # Choose appropriate authentic image based on manufacturer and category
            if 'royal enfield' in manufacturer:
                image_options = authentic_images["royal_enfield"]
            elif 'sport' in category:
                image_options = authentic_images["sport"]
            elif 'cruiser' in category:
                image_options = authentic_images["cruiser"]
            elif any(term in category for term in ['commuter', 'standard', 'naked']):
                image_options = authentic_images["commuter"]
            else:
                # Default to sport bikes for unknown categories
                image_options = authentic_images["sport"]
            
            # Select a random image from the appropriate category
            new_image = random.choice(image_options)
            
            # Update motorcycle with authentic image
            await db.motorcycles.update_one(
                {"id": motorcycle["id"]},
                {"$set": {"image_url": new_image}}
            )
            updated_count += 1
        
        return {
            "message": f"Successfully updated {updated_count} motorcycles with authentic images",
            "updated_count": updated_count,
            "total_processed": len(all_motorcycles),
            "status": "Authentic motorcycle images updated!"
        }
        
    except Exception as e:
        logging.error(f"Error updating authentic images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentic image update failed: {str(e)}")

@api_router.post("/motorcycles/use-base64-images")
async def use_base64_images():
    """Replace external image URLs with base64 encoded placeholder images to avoid CORS issues"""
    try:
        # Create a simple base64 encoded motorcycle silhouette for different types
        # This is a minimal SVG converted to base64 that will always load
        
        motorcycle_svg_base64 = {
            "sport": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgdmlld0JveD0iMCAwIDQwMCAyNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMjUwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjEwMCIgY3k9IjE4MCIgcj0iNDAiIGZpbGw9IiM0QjVDNjgiLz4KPGNpcmNsZSBjeD0iMzAwIiBjeT0iMTgwIiByPSI0MCIgZmlsbD0iIzRCNUM2OCIvPgo8cGF0aCBkPSJNMTAwIDEwMEwyMDAgODBMMzAwIDEwMEwzMDAgMTQwSDEwMFYxMDBaIiBmaWxsPSIjMzc0MzUxIi8+Cjx0ZXh0IHg9IjIwMCIgeT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzZCNzI4MCI+U3BvcnQgTW90b3JjeWNsZTwvdGV4dD4KPC9zdmc+",
            
            "cruiser": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgdmlld0JveD0iMCAwIDQwMCAyNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMjUwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjgwIiBjeT0iMTkwIiByPSI0NSIgZmlsbD0iIzRCNUM2OCIvPgo8Y2lyY2xlIGN4PSIzMjAiIGN5PSIxOTAiIHI9IjQ1IiBmaWxsPSIjNEI1QzY4Ii8+CjxwYXRoIGQ9Ik04MCA5MEwyMDAgMTAwTDMyMCA5MEwzMjAgMTQ1SDgwVjkwWiIgZmlsbD0iIzM3NDM1MSIvPgo8dGV4dCB4PSIyMDAiIHk9IjQwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IiM2QjcyODAiPkNydWlzZXIgTW90b3JjeWNsZTwvdGV4dD4KPHN2Zz4=",
            
            "commuter": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgdmlld0JveD0iMCAwIDQwMCAyNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMjUwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjkwIiBjeT0iMTg1IiByPSIzNSIgZmlsbD0iIzRCNUM2OCIvPgo8Y2lyY2xlIGN4PSIzMTAiIGN5PSIxODUiIHI9IjM1IiBmaWxsPSIjNEI1QzY4Ii8+CjxwYXRoIGQ9Ik05MCA5NUwyMDAgMTA1TDMxMCA5NUwzMTAgMTUwSDkwVjk1WiIgZmlsbD0iIzM3NDM1MSIvPgo8dGV4dCB4PSIyMDAiIHk9IjQwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IiM2QjcyODAiPkNvbW11dGVyIE1vdG9yY3ljbGU8L3RleHQ+Cjwvc3ZnPg==",
            
            "default": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjI1MCIgdmlld0JveD0iMCAwIDQwMCAyNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMjUwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9Ijk1IiBjeT0iMTg1IiByPSI0MCIgZmlsbD0iIzRCNUM2OCIvPgo8Y2lyY2xlIGN4PSIzMDUiIGN5PSIxODUiIHI9IjQwIiBmaWxsPSIjNEI1QzY4Ii8+CjxwYXRoIGQ9Ik05NSAxMDBMMjAwIDkwTDMwNSAxMDBMMzA1IDE0NUg5NVYxMDBaIiBmaWxsPSIjMzc0MzUxIi8+Cjx0ZXh0IHg9IjIwMCIgeT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNiIgZmlsbD0iIzZCNzI4MCI+TW90b3JjeWNsZTwvdGV4dD4KPHN2Zz4="
        }
        
        updated_count = 0
        
        # Get all motorcycles
        all_motorcycles = await db.motorcycles.find({}).to_list(None)
        
        for motorcycle in all_motorcycles:
            category = motorcycle.get('category', '').lower()
            
            # Choose appropriate base64 image based on category
            if 'sport' in category:
                new_image = motorcycle_svg_base64["sport"]
            elif 'cruiser' in category:
                new_image = motorcycle_svg_base64["cruiser"]
            elif 'commuter' in category or 'standard' in category:
                new_image = motorcycle_svg_base64["commuter"]
            else:
                new_image = motorcycle_svg_base64["default"]
            
            # Update motorcycle with base64 image
            await db.motorcycles.update_one(
                {"id": motorcycle["id"]},
                {"$set": {"image_url": new_image}}
            )
            updated_count += 1
        
        return {
            "message": f"Successfully updated {updated_count} motorcycles with base64 encoded images",
            "updated_count": updated_count,
            "total_processed": len(all_motorcycles),
            "status": "Base64 images updated - no CORS issues!"
        }
        
    except Exception as e:
        logging.error(f"Error updating to base64 images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Base64 image update failed: {str(e)}")

@api_router.post("/motorcycles/fix-images")
async def fix_motorcycle_images():
    """Fix motorcycle images with fast-loading, reliable image URLs"""
    try:
        # Curated list of fast-loading motorcycle images
        reliable_images = {
            # Indian motorcycle brands - using reliable generic motorcycle images
            ("Hero", ""): "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=400&h=250&fit=crop&auto=format",
            ("Bajaj", ""): "https://images.unsplash.com/photo-1591231720264-80b4c3b9bc76?w=400&h=250&fit=crop&auto=format", 
            ("TVS", ""): "https://images.unsplash.com/photo-1558618047-3c8c76ca7d2b?w=400&h=250&fit=crop&auto=format",
            ("Royal Enfield", ""): "https://images.unsplash.com/photo-1544552866-d3ed42536cfd?w=400&h=250&fit=crop&auto=format",
            
            # International brands - optimized images
            ("Honda", ""): "https://images.unsplash.com/photo-1558618047-3c8c76ca7d2b?w=400&h=250&fit=crop&auto=format",
            ("Yamaha", ""): "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=400&h=250&fit=crop&auto=format",
            ("Suzuki", ""): "https://images.unsplash.com/photo-1544552866-d3ed42536cfd?w=400&h=250&fit=crop&auto=format",
            ("Kawasaki", ""): "https://images.unsplash.com/photo-1591231720264-80b4c3b9bc76?w=400&h=250&fit=crop&auto=format",
            ("KTM", ""): "https://images.unsplash.com/photo-1591231720264-80b4c3b9bc76?w=400&h=250&fit=crop&auto=format",
            ("BMW", ""): "https://images.unsplash.com/photo-1544552866-d3ed42536cfd?w=400&h=250&fit=crop&auto=format",
            ("Ducati", ""): "https://images.unsplash.com/photo-1591231720264-80b4c3b9bc76?w=400&h=250&fit=crop&auto=format",
            ("Harley-Davidson", ""): "https://images.unsplash.com/photo-1544552866-d3ed42536cfd?w=400&h=250&fit=crop&auto=format",
            ("Triumph", ""): "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=400&h=250&fit=crop&auto=format"
        }
        
        updated_count = 0
        
        # Get all motorcycles
        all_motorcycles = await db.motorcycles.find({}).to_list(None)
        
        for motorcycle in all_motorcycles:
            manufacturer = motorcycle.get('manufacturer', '')
            
            # Find appropriate image for this manufacturer
            new_image = None
            for (mfr, mdl), img_url in reliable_images.items():
                if mfr == manufacturer:
                    new_image = img_url
                    break
            
            # Use a default motorcycle image if no specific mapping
            if not new_image:
                new_image = "https://images.unsplash.com/photo-1558618047-3c8c76ca7d2b?w=400&h=250&fit=crop&auto=format"
            
            # Update motorcycle with new fast-loading image
            await db.motorcycles.update_one(
                {"id": motorcycle["id"]},
                {"$set": {"image_url": new_image}}
            )
            updated_count += 1
        
        return {
            "message": f"Successfully updated images for {updated_count} motorcycles with fast-loading URLs",
            "updated_count": updated_count,
            "total_processed": len(all_motorcycles),
            "status": "Fast-loading images updated!"
        }
        
    except Exception as e:
        logging.error(f"Error fixing motorcycle images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image fix failed: {str(e)}")

@api_router.post("/motorcycles/update-images")
async def update_motorcycle_images():
    """Update motorcycle images with more authentic ones"""
    try:
        # Mapping of manufacturer/model to appropriate images
        image_mappings = {
            # Hero motorcycles - use commuter-style images
            ("Hero", "HF 100"): "https://images.unsplash.com/photo-1728567867292-e615aa97e372",
            ("Hero", "HF Deluxe"): "https://images.unsplash.com/photo-1707561525582-2ddcf937a6dd",
            ("Hero", "HF Dawn"): "https://images.pexels.com/photos/31967053/pexels-photo-31967053.jpeg",
            ("Hero", "Splendor"): "https://images.pexels.com/photos/31967054/pexels-photo-31967054.jpeg",
            
            # Bajaj motorcycles - use sporty commuter images
            ("Bajaj", "CT 100"): "https://images.unsplash.com/photo-1614152412583-bae4138b3f50",
            ("Bajaj", "Platina"): "https://images.unsplash.com/photo-1644879796743-32f929189b81",
            ("Bajaj", "Discover"): "https://images.unsplash.com/photo-1644879796656-94f5d2bf1b95",
            ("Bajaj", "Pulsar"): "https://images.pexels.com/photos/17494037/pexels-photo-17494037.jpeg",
            
            # TVS motorcycles
            ("TVS", "Star City"): "https://images.unsplash.com/photo-1691838870244-d56470357328",
            ("TVS", "Radeon"): "https://images.pexels.com/photos/33186656/pexels-photo-33186656.jpeg",
            ("TVS", "Sport"): "https://images.pexels.com/photos/33162493/pexels-photo-33162493.jpeg",
            
            # Generic fallback for other manufacturers
            ("Honda", ""): "https://images.unsplash.com/photo-1558618047-3c8c76ca7d2b",
            ("Yamaha", ""): "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7",
            ("Suzuki", ""): "https://images.unsplash.com/photo-1544552866-d3ed42536cfd",
            ("Kawasaki", ""): "https://images.unsplash.com/photo-1591231720264-80b4c3b9bc76"
        }
        
        updated_count = 0
        
        # Get all motorcycles that need image updates
        all_motorcycles = await db.motorcycles.find({}).to_list(None)
        
        for motorcycle in all_motorcycles:
            manufacturer = motorcycle.get('manufacturer', '')
            model = motorcycle.get('model', '')
            current_image = motorcycle.get('image_url', '')
            
            # Check if this motorcycle needs an image update
            new_image = None
            
            # Try exact manufacturer + model match first
            for (mfr, mdl), img_url in image_mappings.items():
                if mfr == manufacturer and (mdl == model or mdl == ""):
                    new_image = img_url
                    break
            
            # If no specific match, use manufacturer fallback
            if not new_image:
                for (mfr, mdl), img_url in image_mappings.items():
                    if mfr == manufacturer and mdl == "":
                        new_image = img_url
                        break
            
            # Update if we found a better image and it's not already the same
            if new_image and new_image != current_image:
                await db.motorcycles.update_one(
                    {"id": motorcycle["id"]},
                    {"$set": {"image_url": new_image}}
                )
                updated_count += 1
                print(f"Updated {manufacturer} {model}: {new_image}")
        
        return {
            "message": f"Successfully updated images for {updated_count} motorcycles",
            "updated_count": updated_count,
            "total_checked": len(all_motorcycles)
        }
        
    except Exception as e:
        logging.error(f"Error updating motorcycle images: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image update failed: {str(e)}")
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

# ==================== USER REQUEST AGGREGATION SYSTEM ====================

@api_router.post("/requests")
async def submit_user_request(
    request_data: UserRequestCreate,
    request: Request
):
    """Submit a user request for vendor suggestions, features, etc. (Public endpoint)"""
    try:
        # Try to get current user if available (optional)
        current_user = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                current_user = await get_current_user(authorization=auth_header)
            except:
                pass  # Ignore auth errors for public endpoint
        
        # Create user request
        user_request = UserRequest(
            user_id=current_user.id if current_user else None,
            user_email=request_data.user_email or (current_user.email if current_user else None),
            request_type=request_data.request_type,
            category=request_data.category,
            title=request_data.title,
            content=request_data.content,
            priority=request_data.priority,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Store in database
        await db.user_requests.insert_one(user_request.dict())
        
        return {
            "message": "Request submitted successfully",
            "request_id": user_request.id,
            "status": "pending"
        }
        
    except Exception as e:
        logging.error(f"Error submitting user request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit request")

@api_router.get("/admin/requests")
async def get_user_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    request_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    days: Optional[int] = Query(None, description="Filter by days back from today"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user requests with filtering (Admin only)"""
    try:
        # Build query
        query = {}
        
        if status:
            query["status"] = status
        if request_type:
            query["request_type"] = request_type
        if priority:
            query["priority"] = priority
        if days:
            date_threshold = datetime.utcnow() - timedelta(days=days)
            query["created_at"] = {"$gte": date_threshold}
        
        # Get total count
        total_count = await db.user_requests.count_documents(query)
        
        # Calculate skip for pagination
        skip = (page - 1) * limit
        
        # Get requests
        requests = await db.user_requests.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_previous = page > 1
        
        return {
            "requests": [UserRequest(**req) for req in requests],
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous
            }
        }
        
    except Exception as e:
        logging.error(f"Error fetching user requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch requests")

@api_router.put("/admin/requests/{request_id}")
async def update_user_request(
    request_id: str,
    update_data: UserRequestUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """Update user request status and notes (Admin only)"""
    try:
        # Check if request exists
        existing_request = await db.user_requests.find_one({"id": request_id})
        if not existing_request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Prepare update data
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        if update_dict:
            update_dict["updated_at"] = datetime.utcnow()
            
            # Update request
            await db.user_requests.update_one(
                {"id": request_id},
                {"$set": update_dict}
            )
        
        return {"message": "Request updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating user request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update request")

@api_router.get("/admin/requests/export")
async def export_user_requests(
    days: int = Query(90, description="Number of days to include in export"),
    format: str = Query("txt", description="Export format: txt or json"),
    current_user: User = Depends(get_current_admin_user)
):
    """Export user requests as downloadable file (Admin only)"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get requests in date range
        query = {"created_at": {"$gte": start_date, "$lte": end_date}}
        requests = await db.user_requests.find(query).sort("created_at", -1).to_list(None)
        
        if format == "txt":
            # Generate text format
            content = f"BIKE-DREAM USER REQUESTS EXPORT\n"
            content += f"Export Date: {end_date.strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            content += f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n"
            content += f"Total Requests: {len(requests)}\n"
            content += "=" * 80 + "\n\n"
            
            for req in requests:
                content += f"[{req['created_at'].strftime('%Y-%m-%d %H:%M:%S')}] - {req.get('user_email', 'Anonymous')}\n"
                content += f"Request Type: {req['request_type']}\n"
                content += f"Priority: {req['priority']} | Status: {req['status']}\n"
                if req.get('category'):
                    content += f"Category: {req['category']}\n"
                content += f"Title: {req['title']}\n"
                content += f"Content: {req['content']}\n"
                if req.get('admin_notes'):
                    content += f"Admin Notes: {req['admin_notes']}\n"
                content += "-" * 40 + "\n\n"
            
            # Return as downloadable file
            from fastapi.responses import Response
            return Response(
                content=content,
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename=user_requests_{days}days_{end_date.strftime('%Y%m%d')}.txt"}
            )
            
        else:  # JSON format
            # Convert datetime objects to strings for JSON serialization
            export_data = []
            for req in requests:
                req_copy = req.copy()
                req_copy["created_at"] = req_copy["created_at"].isoformat()
                if req_copy.get("updated_at"):
                    req_copy["updated_at"] = req_copy["updated_at"].isoformat()
                export_data.append(req_copy)
            
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content={
                    "export_info": {
                        "export_date": end_date.isoformat(),
                        "date_range": {
                            "start": start_date.isoformat(),
                            "end": end_date.isoformat()
                        },
                        "total_requests": len(requests),
                        "format": "json"
                    },
                    "requests": export_data
                },
                headers={"Content-Disposition": f"attachment; filename=user_requests_{days}days_{end_date.strftime('%Y%m%d')}.json"}
            )
        
    except Exception as e:
        logging.error(f"Error exporting user requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export requests")

@api_router.get("/admin/requests/stats")
async def get_request_statistics(
    days: int = Query(30, description="Number of days for statistics"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get user request statistics (Admin only)"""
    try:
        # Calculate date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)
        
        # Aggregate statistics
        pipeline = [
            {"$match": {"created_at": {"$gte": date_threshold}}},
            {"$group": {
                "_id": None,
                "total_requests": {"$sum": 1},
                "by_type": {"$push": "$request_type"},
                "by_status": {"$push": "$status"},
                "by_priority": {"$push": "$priority"}
            }}
        ]
        
        result = await db.user_requests.aggregate(pipeline).to_list(1)
        
        if not result:
            return {
                "period_days": days,
                "total_requests": 0,
                "by_type": {},
                "by_status": {},
                "by_priority": {}
            }
        
        data = result[0]
        
        # Count occurrences
        from collections import Counter
        type_counts = Counter(data["by_type"])
        status_counts = Counter(data["by_status"])
        priority_counts = Counter(data["by_priority"])
        
        return {
            "period_days": days,
            "total_requests": data["total_requests"],
            "by_type": dict(type_counts),
            "by_status": dict(status_counts),
            "by_priority": dict(priority_counts)
        }
        
    except Exception as e:
        logging.error(f"Error getting request statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

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

# ==================== SEARCH ANALYTICS API ENDPOINTS ====================

@api_router.post("/analytics/search")
async def log_search_analytics(
    search_term: str,
    search_type: str = "general",
    filters_applied: dict = None,
    results_count: int = 0,
    clicked_results: List[str] = None,
    request: Request = None
):
    """Log search analytics for user engagement tracking"""
    try:
        # Get user info if available
        user_id = None
        session_id = None
        
        # Try to get user from headers
        auth_header = request.headers.get('Authorization')
        session_header = request.headers.get('X-Session-ID')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                user_id = payload.get('user_id')
            except:
                pass
        elif session_header:
            session_id = session_header
            # Try to get user from session
            user = await db.users.find_one({"session_token": session_id})
            if user:
                user_id = user["id"]
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Create search analytics record
        analytics = SearchAnalytics(
            user_id=user_id,
            session_id=session_id,
            search_term=search_term,
            search_type=search_type,
            filters_applied=filters_applied or {},
            results_count=results_count,
            clicked_results=clicked_results or [],
            user_agent=request.headers.get('User-Agent'),
            user_location=request.headers.get('X-User-Location')  # Can be set by frontend
        )
        
        await db.search_analytics.insert_one(analytics.dict())
        
        return {"message": "Search analytics logged successfully"}
        
    except Exception as e:
        print(f"Error logging search analytics: {str(e)}")
        return {"message": "Analytics logging failed"}

@api_router.post("/analytics/engagement")
async def log_user_engagement(
    page_view: str,
    time_spent: int = None,
    actions: List[dict] = None,
    referrer: str = None,
    request: Request = None
):
    """Log user engagement for analytics"""
    try:
        # Get user info if available
        user_id = None
        session_id = None
        
        # Try to get user from headers
        auth_header = request.headers.get('Authorization')
        session_header = request.headers.get('X-Session-ID')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                user_id = payload.get('user_id')
            except:
                pass
        elif session_header:
            session_id = session_header
            # Try to get user from session
            user = await db.users.find_one({"session_token": session_id})
            if user:
                user_id = user["id"]
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Create engagement record
        engagement = UserEngagement(
            user_id=user_id,
            session_id=session_id,
            page_view=page_view,
            time_spent=time_spent,
            actions=actions or [],
            referrer=referrer
        )
        
        await db.user_engagement.insert_one(engagement.dict())
        
        return {"message": "User engagement logged successfully"}
        
    except Exception as e:
        print(f"Error logging user engagement: {str(e)}")
        return {"message": "Engagement logging failed"}

@api_router.get("/analytics/search-trends")
async def get_search_trends(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(20, ge=1, le=100)
):
    """Get search trends and popular search terms"""
    try:
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get popular search terms
        popular_terms_pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$group": {
                "_id": "$search_term",
                "count": {"$sum": 1},
                "avg_results": {"$avg": "$results_count"},
                "last_searched": {"$max": "$timestamp"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        popular_terms = await db.search_analytics.aggregate(popular_terms_pipeline).to_list(limit)
        
        # Get search trends over time
        trends_pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "term": "$search_term"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.date": 1}},
            {"$limit": 100}
        ]
        
        trends = await db.search_analytics.aggregate(trends_pipeline).to_list(100)
        
        # Get popular manufacturers
        manufacturer_pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}, "search_type": "manufacturer"}},
            {"$group": {
                "_id": "$search_term",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        popular_manufacturers = await db.search_analytics.aggregate(manufacturer_pipeline).to_list(10)
        
        return {
            "popular_terms": popular_terms,
            "trends": trends,
            "popular_manufacturers": popular_manufacturers,
            "period_days": days
        }
        
    except Exception as e:
        print(f"Error getting search trends: {str(e)}")
        return {"error": "Failed to get search trends"}

@api_router.get("/analytics/user-behavior")
async def get_user_behavior_analytics(
    days: int = Query(7, ge=1, le=90),
    user_id: Optional[str] = Query(None)
):
    """Get user behavior analytics"""
    try:
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query
        query = {"timestamp": {"$gte": start_date}}
        if user_id:
            query["user_id"] = user_id
        
        # Get page view analytics
        page_views_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$page_view",
                "count": {"$sum": 1},
                "avg_time_spent": {"$avg": "$time_spent"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        page_views = await db.user_engagement.aggregate(page_views_pipeline).to_list(None)
        
        # Get user actions analytics
        actions_pipeline = [
            {"$match": query},
            {"$unwind": "$actions"},
            {"$group": {
                "_id": "$actions.action_type",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        actions = await db.user_engagement.aggregate(actions_pipeline).to_list(None)
        
        # Get user session analytics
        session_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$session_id",
                "pages_visited": {"$addToSet": "$page_view"},
                "total_time": {"$sum": "$time_spent"},
                "actions_count": {"$sum": {"$size": "$actions"}}
            }},
            {"$project": {
                "pages_count": {"$size": "$pages_visited"},
                "total_time": 1,
                "actions_count": 1
            }},
            {"$group": {
                "_id": None,
                "avg_pages_per_session": {"$avg": "$pages_count"},
                "avg_time_per_session": {"$avg": "$total_time"},
                "avg_actions_per_session": {"$avg": "$actions_count"},
                "total_sessions": {"$sum": 1}
            }}
        ]
        
        session_stats = await db.user_engagement.aggregate(session_pipeline).to_list(1)
        
        return {
            "page_views": page_views,
            "actions": actions,
            "session_stats": session_stats[0] if session_stats else {},
            "period_days": days
        }
        
    except Exception as e:
        print(f"Error getting user behavior analytics: {str(e)}")
        return {"error": "Failed to get user behavior analytics"}

@api_router.get("/analytics/motorcycle-interests")
async def get_motorcycle_interests(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=100)
):
    """Get motorcycle interest analytics based on search and engagement data"""
    try:
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get most clicked motorcycles from search analytics
        clicked_bikes_pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$unwind": "$clicked_results"},
            {"$group": {
                "_id": "$clicked_results",
                "click_count": {"$sum": 1},
                "search_terms": {"$addToSet": "$search_term"}
            }},
            {"$sort": {"click_count": -1}},
            {"$limit": limit}
        ]
        
        clicked_bikes = await db.search_analytics.aggregate(clicked_bikes_pipeline).to_list(limit)
        
        # Get motorcycle details for clicked bikes
        motorcycle_interests = []
        for bike in clicked_bikes:
            motorcycle = await db.motorcycles.find_one({"id": bike["_id"]})
            if motorcycle:
                motorcycle_interests.append({
                    "motorcycle": {
                        "id": motorcycle["id"],
                        "manufacturer": motorcycle["manufacturer"],
                        "model": motorcycle["model"],
                        "year": motorcycle["year"],
                        "category": motorcycle["category"],
                        "price_usd": motorcycle.get("price_usd"),
                        "image_url": motorcycle.get("image_url")
                    },
                    "click_count": bike["click_count"],
                    "search_terms": bike["search_terms"]
                })
        
        # Get category interests
        category_pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$group": {
                "_id": "$filters_applied.category",
                "count": {"$sum": 1}
            }},
            {"$match": {"_id": {"$ne": None}}},
            {"$sort": {"count": -1}}
        ]
        
        category_interests = await db.search_analytics.aggregate(category_pipeline).to_list(None)
        
        # Get manufacturer interests
        manufacturer_pipeline = [
            {"$match": {"timestamp": {"$gte": start_date}}},
            {"$group": {
                "_id": "$filters_applied.manufacturer",
                "count": {"$sum": 1}
            }},
            {"$match": {"_id": {"$ne": None}}},
            {"$sort": {"count": -1}}
        ]
        
        manufacturer_interests = await db.search_analytics.aggregate(manufacturer_pipeline).to_list(None)
        
        return {
            "motorcycle_interests": motorcycle_interests,
            "category_interests": category_interests,
            "manufacturer_interests": manufacturer_interests,
            "period_days": days
        }
        
    except Exception as e:
        print(f"Error getting motorcycle interests: {str(e)}")
        return {"error": "Failed to get motorcycle interests"}

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