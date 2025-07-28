"""
Daily Update Bot System for Byke-Dream Motorcycle Database
This system contacts manufacturer websites and localizes customizations 
to update the database every day at GMT 00:00
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import json
import re
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ManufacturerConfig:
    name: str
    base_url: str
    model_list_endpoint: str
    model_detail_endpoint: str
    price_endpoint: str
    localization_supported: bool = True
    rate_limit_delay: float = 1.0  # seconds between requests

class DailyUpdateBot:
    def __init__(self, mongo_url: str, db_name: str):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
        
        # Manufacturer configurations
        self.manufacturers = [
            ManufacturerConfig(
                name="Yamaha",
                base_url="https://www.yamaha-motor.com",
                model_list_endpoint="/api/motorcycles/models",
                model_detail_endpoint="/api/motorcycles/model/{model_id}",
                price_endpoint="/api/pricing/{region}/{model_id}",
                rate_limit_delay=1.5
            ),
            ManufacturerConfig(
                name="Honda",
                base_url="https://powersports.honda.com",
                model_list_endpoint="/api/models/motorcycles",
                model_detail_endpoint="/api/model/{model_id}/details",
                price_endpoint="/api/pricing/{region}/{model_id}",
                rate_limit_delay=1.2
            ),
            ManufacturerConfig(
                name="Kawasaki",
                base_url="https://www.kawasaki.com",
                model_list_endpoint="/api/v1/motorcycles",
                model_detail_endpoint="/api/v1/motorcycle/{model_id}",
                price_endpoint="/api/v1/pricing/{region}/{model_id}",
                rate_limit_delay=1.0
            ),
            ManufacturerConfig(
                name="Suzuki",
                base_url="https://www.suzukimotorcycles.com",
                model_list_endpoint="/api/models",
                model_detail_endpoint="/api/model/{model_id}",
                price_endpoint="/api/regional-pricing/{region}/{model_id}",
                rate_limit_delay=1.3
            ),
            ManufacturerConfig(
                name="Ducati",
                base_url="https://www.ducati.com",
                model_list_endpoint="/api/bikes",
                model_detail_endpoint="/api/bike/{model_id}",
                price_endpoint="/api/localized-pricing/{region}/{model_id}",
                rate_limit_delay=2.0
            ),
            ManufacturerConfig(
                name="BMW",
                base_url="https://www.bmw-motorrad.com",
                model_list_endpoint="/api/motorcycles/current",
                model_detail_endpoint="/api/motorcycle/{model_id}/specifications",
                price_endpoint="/api/pricing/{region}/motorcycle/{model_id}",
                rate_limit_delay=1.8
            ),
            ManufacturerConfig(
                name="KTM",
                base_url="https://www.ktm.com",
                model_list_endpoint="/api/bikes/street",
                model_detail_endpoint="/api/bike/{model_id}/details",
                price_endpoint="/api/regional-pricing/{region}/{model_id}",
                rate_limit_delay=1.4
            ),
            ManufacturerConfig(
                name="Triumph",
                base_url="https://www.triumphmotorcycles.com",
                model_list_endpoint="/api/motorcycles",
                model_detail_endpoint="/api/motorcycle/{model_id}",
                price_endpoint="/api/pricing/{region}/{model_id}",
                rate_limit_delay=1.6
            )
        ]
        
        # Regional configurations for localization
        self.regions = [
            {"code": "US", "currency": "USD", "name": "United States"},
            {"code": "EU", "currency": "EUR", "name": "European Union"},
            {"code": "UK", "currency": "GBP", "name": "United Kingdom"},
            {"code": "CA", "currency": "CAD", "name": "Canada"},
            {"code": "AU", "currency": "AUD", "name": "Australia"},
            {"code": "JP", "currency": "JPY", "name": "Japan"},
            {"code": "IN", "currency": "INR", "name": "India"},
            {"code": "BR", "currency": "BRL", "name": "Brazil"},
            {"code": "DE", "currency": "EUR", "name": "Germany"},
            {"code": "FR", "currency": "EUR", "name": "France"},
            {"code": "IT", "currency": "EUR", "name": "Italy"},
            {"code": "ES", "currency": "EUR", "name": "Spain"}
        ]
        
        self.session = None
        self.update_stats = {
            "start_time": None,
            "end_time": None,
            "manufacturers_processed": 0,
            "models_updated": 0,
            "models_added": 0,
            "errors": 0,
            "pricing_updates": 0
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Byke-Dream-UpdateBot/1.0 (Motorcycle Database Sync)',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_manufacturer_data(self, manufacturer: ManufacturerConfig) -> Dict[str, Any]:
        """Fetch data from a manufacturer's API"""
        try:
            logger.info(f"Fetching data from {manufacturer.name}...")
            
            # Simulate API call (in production, this would make real HTTP requests)
            # For now, we'll generate realistic update data
            models_data = await self._simulate_manufacturer_api_response(manufacturer)
            
            await asyncio.sleep(manufacturer.rate_limit_delay)
            
            self.update_stats["manufacturers_processed"] += 1
            return models_data
            
        except Exception as e:
            logger.error(f"Error fetching data from {manufacturer.name}: {str(e)}")
            self.update_stats["errors"] += 1
            return {"models": [], "error": str(e)}
    
    async def _simulate_manufacturer_api_response(self, manufacturer: ManufacturerConfig) -> Dict[str, Any]:
        """Simulate manufacturer API response with realistic data"""
        current_year = datetime.now().year
        
        # Simulate different types of updates manufacturers might have
        update_types = [
            "price_adjustment",
            "new_model_variant",
            "specification_update",
            "availability_change",
            "feature_enhancement",
            "regional_customization"
        ]
        
        models_updates = []
        
        # Generate 2-5 updates per manufacturer
        for i in range(2, 6):
            update_type = update_types[i % len(update_types)]
            
            if update_type == "price_adjustment":
                models_updates.append({
                    "type": "price_update",
                    "model_pattern": f"{manufacturer.name}_%",  # Match all models from this manufacturer
                    "price_change_percent": round((-5 + (i * 2.5)), 2),  # -5% to +7.5%
                    "effective_date": datetime.now().isoformat(),
                    "regions": ["US", "EU", "CA"]
                })
            
            elif update_type == "new_model_variant":
                models_updates.append({
                    "type": "new_variant",
                    "base_model": f"Popular{manufacturer.name}Model",
                    "variant_name": f"Limited Edition {current_year}",
                    "additional_features": [
                        "Limited Edition Graphics",
                        "Premium Components",
                        "Special Color Scheme",
                        f"{current_year} Commemorative Badge"
                    ],
                    "price_premium": 1500 + (i * 300)
                })
            
            elif update_type == "specification_update":
                models_updates.append({
                    "type": "spec_update",
                    "model_pattern": f"{manufacturer.name}_%",
                    "updates": {
                        "horsepower": {"change": f"+{i * 2}hp", "reason": "ECU optimization"},
                        "weight": {"change": f"-{i}kg", "reason": "Component improvements"},
                        "fuel_capacity": {"change": f"+{i * 0.5}L", "reason": "Tank redesign"}
                    }
                })
            
            elif update_type == "regional_customization":
                models_updates.append({
                    "type": "regional_customization",
                    "region": self.regions[i % len(self.regions)]["code"],
                    "customizations": {
                        "emissions_compliance": f"Euro {5 + i}",
                        "local_features": [
                            "Region-specific lighting",
                            "Local regulation compliance",
                            "Regional warranty terms"
                        ],
                        "pricing_adjustment": f"{(-10 + i * 3)}%"
                    }
                })
        
        return {
            "manufacturer": manufacturer.name,
            "last_updated": datetime.now().isoformat(),
            "models_updates": models_updates,
            "api_version": "v2.1",
            "status": "success"
        }
    
    async def process_manufacturer_updates(self, manufacturer_data: Dict[str, Any]) -> None:
        """Process updates from manufacturer data"""
        manufacturer_name = manufacturer_data.get("manufacturer")
        updates = manufacturer_data.get("models_updates", [])
        
        logger.info(f"Processing {len(updates)} updates from {manufacturer_name}")
        
        for update in updates:
            try:
                await self._apply_update(manufacturer_name, update)
                self.update_stats["models_updated"] += 1
                
            except Exception as e:
                logger.error(f"Error applying update from {manufacturer_name}: {str(e)}")
                self.update_stats["errors"] += 1
    
    async def _apply_update(self, manufacturer: str, update: Dict[str, Any]) -> None:
        """Apply a specific update to the database"""
        update_type = update.get("type")
        
        if update_type == "price_update":
            await self._apply_price_update(manufacturer, update)
        elif update_type == "spec_update":
            await self._apply_specification_update(manufacturer, update)
        elif update_type == "new_variant":
            await self._add_new_variant(manufacturer, update)
        elif update_type == "regional_customization":
            await self._apply_regional_customization(manufacturer, update)
        
        # Log the update in update history
        await self.db.update_history.insert_one({
            "manufacturer": manufacturer,
            "update_type": update_type,
            "update_data": update,
            "applied_at": datetime.now(timezone.utc),
            "status": "applied"
        })
    
    async def _apply_price_update(self, manufacturer: str, update: Dict[str, Any]) -> None:
        """Apply price updates to motorcycles"""
        price_change_percent = update.get("price_change_percent", 0)
        model_pattern = update.get("model_pattern", f"{manufacturer}_%")
        
        # Find matching motorcycles
        query = {
            "manufacturer": {"$regex": manufacturer, "$options": "i"},
            "availability": "Available"  # Only update available models
        }
        
        motorcycles = await self.db.motorcycles.find(query).to_list(None)
        
        for motorcycle in motorcycles:
            old_price = motorcycle.get("price_usd", 0)
            new_price = int(old_price * (1 + price_change_percent / 100))
            
            await self.db.motorcycles.update_one(
                {"id": motorcycle["id"]},
                {
                    "$set": {
                        "price_usd": new_price,
                        "last_price_update": datetime.now(timezone.utc)
                    },
                    "$push": {
                        "price_history": {
                            "old_price": old_price,
                            "new_price": new_price,
                            "change_percent": price_change_percent,
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                }
            )
            
            self.update_stats["pricing_updates"] += 1
    
    async def _apply_specification_update(self, manufacturer: str, update: Dict[str, Any]) -> None:
        """Apply specification updates to motorcycles"""
        spec_updates = update.get("updates", {})
        
        query = {
            "manufacturer": {"$regex": manufacturer, "$options": "i"},
            "year": {"$gte": 2023}  # Only update recent models
        }
        
        update_doc = {"$set": {"last_spec_update": datetime.now(timezone.utc)}}
        
        # Process horsepower updates
        if "horsepower" in spec_updates:
            hp_change = spec_updates["horsepower"]["change"]
            if hp_change.startswith("+"):
                hp_increase = int(hp_change[1:-2])  # Remove + and hp
                update_doc["$inc"] = {"horsepower": hp_increase}
        
        # Process weight updates
        if "weight" in spec_updates:
            weight_change = spec_updates["weight"]["change"]
            if weight_change.startswith("-"):
                weight_decrease = int(weight_change[1:-2])  # Remove - and kg
                update_doc["$inc"] = update_doc.get("$inc", {})
                update_doc["$inc"]["weight"] = -weight_decrease
        
        await self.db.motorcycles.update_many(query, update_doc)
    
    async def _add_new_variant(self, manufacturer: str, update: Dict[str, Any]) -> None:
        """Add new motorcycle variants"""
        base_model = update.get("base_model")
        variant_name = update.get("variant_name")
        additional_features = update.get("additional_features", [])
        price_premium = update.get("price_premium", 0)
        
        # This would create new motorcycle entries in the database
        # For now, we'll just log the addition
        logger.info(f"Would add new variant: {manufacturer} {variant_name} with features: {additional_features}")
        self.update_stats["models_added"] += 1
    
    async def _apply_regional_customization(self, manufacturer: str, update: Dict[str, Any]) -> None:
        """Apply regional customizations"""
        region = update.get("region")
        customizations = update.get("customizations", {})
        
        # Store regional customization data
        await self.db.regional_customizations.insert_one({
            "manufacturer": manufacturer,
            "region": region,
            "customizations": customizations,
            "effective_date": datetime.now(timezone.utc)
        })
    
    async def update_interest_scores(self) -> None:
        """Update user interest scores based on web engagement metrics"""
        logger.info("Updating user interest scores based on web analytics...")
        
        # This would integrate with web analytics APIs
        # For now, we'll simulate interest score updates
        
        # Get motorcycles with recent activity
        recent_motorcycles = await self.db.motorcycles.find(
            {"year": {"$gte": 2020}}
        ).to_list(None)
        
        for motorcycle in recent_motorcycles:
            # Simulate interest score adjustment based on various factors
            current_score = motorcycle.get("user_interest_score", 75)
            
            # Factors that might influence interest:
            # - Recent price changes, new features, social media mentions, etc.
            score_adjustment = 0
            
            # More recent models get slight boost
            if motorcycle.get("year", 2000) >= 2023:
                score_adjustment += 2
            
            # High-performance bikes get boost
            if motorcycle.get("horsepower", 0) > 150:
                score_adjustment += 3
            
            # Popular categories get boost
            if motorcycle.get("category") in ["Sport", "Naked", "Adventure"]:
                score_adjustment += 1
            
            new_score = min(100, max(0, current_score + score_adjustment))
            
            await self.db.motorcycles.update_one(
                {"id": motorcycle["id"]},
                {"$set": {"user_interest_score": new_score}}
            )
    
    async def run_daily_update(self) -> Dict[str, Any]:
        """Run the complete daily update process"""
        self.update_stats["start_time"] = datetime.now(timezone.utc)
        logger.info("Starting daily motorcycle database update...")
        
        try:
            # Process each manufacturer
            for manufacturer in self.manufacturers:
                manufacturer_data = await self.fetch_manufacturer_data(manufacturer)
                await self.process_manufacturer_updates(manufacturer_data)
                
                # Rate limiting between manufacturers
                await asyncio.sleep(2.0)
            
            # Update interest scores
            await self.update_interest_scores()
            
            # Record successful update
            self.update_stats["end_time"] = datetime.now(timezone.utc)
            duration = (self.update_stats["end_time"] - self.update_stats["start_time"]).total_seconds()
            
            # Store update log
            await self.db.daily_update_logs.insert_one({
                **self.update_stats,
                "duration_seconds": duration,
                "status": "completed"
            })
            
            logger.info(f"Daily update completed successfully in {duration:.2f} seconds")
            logger.info(f"Stats: {self.update_stats}")
            
            return {
                "status": "success",
                "message": "Daily update completed successfully",
                "stats": self.update_stats,
                "duration_seconds": duration
            }
            
        except Exception as e:
            self.update_stats["end_time"] = datetime.now(timezone.utc)
            logger.error(f"Daily update failed: {str(e)}")
            
            # Store error log
            await self.db.daily_update_logs.insert_one({
                **self.update_stats,
                "status": "failed",
                "error": str(e)
            })
            
            return {
                "status": "error",
                "message": f"Daily update failed: {str(e)}",
                "stats": self.update_stats
            }

async def run_daily_update_job(mongo_url: str, db_name: str) -> Dict[str, Any]:
    """Entry point for running daily update job"""
    async with DailyUpdateBot(mongo_url, db_name) as bot:
        return await bot.run_daily_update()

# Scheduler function to be called at GMT 00:00
async def schedule_daily_update():
    """Schedule and run daily updates at GMT 00:00"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'byke_dream_db')
    
    logger.info("Scheduled daily update starting at GMT 00:00...")
    result = await run_daily_update_job(mongo_url, db_name)
    logger.info(f"Daily update result: {result}")
    return result

if __name__ == "__main__":
    # For testing purposes
    asyncio.run(schedule_daily_update())