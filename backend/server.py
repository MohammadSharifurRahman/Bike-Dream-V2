from fastapi import FastAPI, APIRouter, HTTPException, Query, BackgroundTasks, Depends, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from comprehensive_motorcycles import get_comprehensive_motorcycle_data
from daily_update_bot import run_daily_update_job
import asyncio
import aiohttp


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
    picture: str
    session_token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    favorite_motorcycles: List[str] = Field(default_factory=list)

class UserCreate(BaseModel):
    email: str
    name: str
    picture: str
    session_token: str

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
    user_id: str
    motorcycle_id: str
    comment_text: str
    parent_comment_id: Optional[str] = None  # For replies
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    likes: int = Field(default=0)

class CommentCreate(BaseModel):
    motorcycle_id: str
    comment_text: str
    parent_comment_id: Optional[str] = None

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
    average_rating: float = Field(default=0.0)
    total_ratings: int = Field(default=0)
    total_comments: int = Field(default=0)
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

# Authentication helper
async def get_current_user(x_session_id: str = Header(None)):
    """Get current user from session ID"""
    if not x_session_id:
        return None
    
    user = await db.users.find_one({"session_token": x_session_id})
    if user:
        return User(**user)
    return None

async def require_auth(x_session_id: str = Header(None)):
    """Require authentication"""
    user = await get_current_user(x_session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Welcome to Byke-Dream API - Comprehensive Motorcycle Database with User Community"}

# Authentication routes
@api_router.post("/auth/profile")
async def authenticate_user(user_data: dict):
    """Authenticate user with Emergent session data"""
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
            user = User(**user_create.dict())
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
async def add_comment(motorcycle_id: str, comment_data: CommentCreate, current_user: User = Depends(require_auth)):
    """Add a comment to a motorcycle"""
    # Check if motorcycle exists
    motorcycle = await db.motorcycles.find_one({"id": motorcycle_id})
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    comment = Comment(
        user_id=current_user.id,
        motorcycle_id=motorcycle_id,
        comment_text=comment_data.comment_text,
        parent_comment_id=comment_data.parent_comment_id
    )
    await db.comments.insert_one(comment.dict())
    
    # Update motorcycle comment count
    await update_motorcycle_comment_count(motorcycle_id)
    
    return {"message": "Comment added", "comment_id": comment.id}

@api_router.get("/motorcycles/{motorcycle_id}/comments")
async def get_motorcycle_comments(motorcycle_id: str, limit: int = Query(20, le=100)):
    """Get comments for a motorcycle with user information"""
    comments_pipeline = [
        {"$match": {"motorcycle_id": motorcycle_id, "parent_comment_id": None}},  # Top-level comments only
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
            "user_id": 1,
            "motorcycle_id": 1,
            "comment_text": 1,
            "parent_comment_id": 1,
            "created_at": 1,
            "updated_at": 1,
            "likes": 1,
            "user_name": "$user.name",
            "user_picture": "$user.picture"
        }}
    ]
    
    comments = await db.comments.aggregate(comments_pipeline).to_list(limit)
    
    # Get replies for each comment
    for comment in comments:
        replies_pipeline = [
            {"$match": {"parent_comment_id": comment["id"]}},
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user"
            }},
            {"$unwind": "$user"},
            {"$sort": {"created_at": 1}},
            {"$project": {
                "id": 1,
                "user_id": 1,
                "comment_text": 1,
                "created_at": 1,
                "likes": 1,
                "user_name": "$user.name",
                "user_picture": "$user.picture"
            }}
        ]
        replies = await db.comments.aggregate(replies_pipeline).to_list(None)
        comment["replies"] = replies
    
    return comments

@api_router.post("/comments/{comment_id}/like")
async def like_comment(comment_id: str, current_user: User = Depends(require_auth)):
    """Like a comment"""
    # Check if already liked
    existing_like = await db.comment_likes.find_one({
        "user_id": current_user.id,
        "comment_id": comment_id
    })
    
    if existing_like:
        # Unlike
        await db.comment_likes.delete_one({"id": existing_like["id"]})
        await db.comments.update_one({"id": comment_id}, {"$inc": {"likes": -1}})
        return {"message": "Comment unliked", "liked": False}
    else:
        # Like
        like_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "comment_id": comment_id,
            "created_at": datetime.utcnow()
        }
        await db.comment_likes.insert_one(like_data)
        await db.comments.update_one({"id": comment_id}, {"$inc": {"likes": 1}})
        return {"message": "Comment liked", "liked": True}

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

# Motorcycle routes with increased limits
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
    limit: Optional[int] = Query(1000, le=3000),  # Increased limit to show all motorcycles
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
        
        return {
            "message": f"Successfully seeded comprehensive database with {total_inserted} motorcycles",
            "total_motorcycles": stats.total_motorcycles,
            "manufacturers": len(stats.manufacturers),
            "categories": len(stats.categories),
            "year_range": stats.year_range,
            "status": "Database expansion complete - Ready for global motorcycle enthusiasts!",
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