# Vendor pricing system with location-based currencies
import random
from typing import List, Dict, Any
from datetime import datetime

class VendorPricingSystem:
    def __init__(self):
        # Currency exchange rates (mock data - in production this would come from a real API)
        self.exchange_rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.73,
            "CAD": 1.25,
            "AUD": 1.45,
            "INR": 83.0,
            "JPY": 110.0,
            "CNY": 7.0,
            "BRL": 5.2,
            "MXN": 18.0
        }
        
        # Regional vendors by location
        self.regional_vendors = {
            "US": ["Yamaha USA", "Honda USA", "Kawasaki USA", "Suzuki USA", "Ducati North America", "BMW Motorrad USA"],
            "EU": ["Yamaha Europe", "Honda Europe", "Kawasaki Europe", "Suzuki Europe", "Ducati Europe", "BMW Motorrad"],
            "UK": ["Yamaha UK", "Honda UK", "Kawasaki UK", "Suzuki UK", "Ducati UK", "BMW Motorrad UK"],
            "CA": ["Yamaha Canada", "Honda Canada", "Kawasaki Canada", "Suzuki Canada", "BMW Motorrad Canada"],
            "AU": ["Yamaha Australia", "Honda Australia", "Kawasaki Australia", "Suzuki Australia", "BMW Motorrad Australia"],
            "IN": ["Yamaha India", "Honda India", "Bajaj Auto", "TVS Motor", "Hero MotoCorp", "Royal Enfield"],
            "JP": ["Yamaha Japan", "Honda Japan", "Kawasaki Japan", "Suzuki Japan"],
            "CN": ["Yamaha China", "Honda China", "Kawasaki China", "Suzuki China", "Zongshen"],
            "BR": ["Yamaha Brasil", "Honda Brasil", "Kawasaki Brasil", "Suzuki Brasil"],
            "MX": ["Yamaha Mexico", "Honda Mexico", "Kawasaki Mexico", "Suzuki Mexico"]
        }
        
        # Regional currency mapping
        self.regional_currencies = {
            "US": "USD",
            "EU": "EUR", 
            "UK": "GBP",
            "CA": "CAD",
            "AU": "AUD",
            "IN": "INR",
            "JP": "JPY",
            "CN": "CNY",
            "BR": "BRL",
            "MX": "MXN"
        }
    
    def get_vendor_prices(self, motorcycle: Dict[str, Any], region: str = "US") -> List[Dict[str, Any]]:
        """Get vendor prices for a motorcycle in a specific region"""
        base_price_usd = motorcycle.get("price_usd", 10000)
        currency = self.regional_currencies.get(region, "USD")
        exchange_rate = self.exchange_rates.get(currency, 1.0)
        vendors = self.regional_vendors.get(region, self.regional_vendors["US"])
        
        vendor_prices = []
        
        for i, vendor in enumerate(vendors[:4]):  # Show top 4 vendors
            # Add some realistic price variation (+/- 15%)
            price_variation = random.uniform(-0.15, 0.15)
            vendor_price_usd = base_price_usd * (1 + price_variation)
            local_price = vendor_price_usd * exchange_rate
            
            # Add availability and special offers
            availability_options = ["In Stock", "2-3 weeks", "Pre-order", "Limited Stock"]
            special_offers = [
                None,
                "Free shipping",
                "Trade-in bonus $500",
                "0% APR financing",
                "Extended warranty",
                "Accessories included"
            ]
            
            vendor_data = {
                "vendor_name": vendor,
                "price": round(local_price, 2),
                "currency": currency,
                "price_usd": round(vendor_price_usd, 2),
                "availability": availability_options[i % len(availability_options)],
                "special_offer": random.choice(special_offers) if random.random() > 0.6 else None,
                "rating": round(random.uniform(4.0, 5.0), 1),
                "reviews_count": random.randint(50, 500),
                "shipping": "Free" if random.random() > 0.3 else f"${random.randint(50, 200)}",
                "estimated_delivery": f"{random.randint(3, 14)} days",
                "website_url": f"https://{vendor.lower().replace(' ', '')}.com",
                "phone": f"+1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}" if region == "US" else None
            }
            
            vendor_prices.append(vendor_data)
        
        # Sort by price (lowest first)
        vendor_prices.sort(key=lambda x: x["price"])
        
        return vendor_prices
    
    def get_supported_regions(self) -> List[Dict[str, str]]:
        """Get list of supported regions with currencies"""
        regions = []
        for region, currency in self.regional_currencies.items():
            regions.append({
                "code": region,
                "currency": currency,
                "name": self._get_region_name(region)
            })
        return regions
    
    def _get_region_name(self, region_code: str) -> str:
        """Get full region name from code"""
        region_names = {
            "US": "United States",
            "EU": "European Union",
            "UK": "United Kingdom", 
            "CA": "Canada",
            "AU": "Australia",
            "IN": "India",
            "JP": "Japan",
            "CN": "China",
            "BR": "Brazil",
            "MX": "Mexico"
        }
        return region_names.get(region_code, region_code)

# Global instance
vendor_pricing = VendorPricingSystem()