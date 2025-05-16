from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
import httpx
from pydantic import BaseModel
from amazon_scraper import scrape_amazon

router = APIRouter()

class Sneaker(BaseModel):
    """Model for sneaker data"""
    name: str
    brand: str
    price: float
    image_url: str
    product_url: str
    site: Optional[str] = None
    available_sizes: List[str] = []

@router.get("/sneakers/{site_name}", response_model=Dict[str, List[Sneaker]])
async def get_sneakers_by_site(site_name: str, brand: Optional[str] = None, limit: int = 20):
    """Fetch sneakers from a specific e-commerce site"""
    supported_sites = ["nike", "footlocker"]
    
    if site_name.lower() not in supported_sites:
        raise HTTPException(status_code=404, detail=f"Site {site_name} not supported")
    
    # Choose the appropriate scraper based on site name
    if site_name.lower() == "nike":
        sneakers = await scrape_nike(brand, 5)
    elif site_name.lower() == "footlocker":
        sneakers = await scrape_footlocker(brand, limit) 
    
    return {"sneakers": sneakers}

# scrape with playwright
async def scrape_nike(brand: Optional[str] = None, limit: int = 5) -> List[Sneaker]:
    sneakers = await scrape_amazon("Nike sneakers", limit=5)
    transformed = []
    for item in sneakers:
        transformed.append({
            "name": item.get("product_name"),
            "brand": "Nike",  # If you’re scraping Nike only, hardcode it or extract properly
            "image_url": item.get("image_url", ""),  # You might need to scrape this if missing
            "product_url": item.get("url"),
            "price": item.get("price"),
            "currency": item.get("currency", "USD"),
        })
    return transformed

# dummy data
# async def scrape_nike(brand: Optional[str] = None, limit: int = 20) -> List[Sneaker]:
    """Scrape Nike website for sneakers"""
    url = "https://www.nike.com/w/mens-shoes-nik1zy7ok"
    if brand:
        # In a real implementation, you'd modify the URL to include brand filter
        pass
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            
            # In a real implementation, you'd parse the HTML response
            # This is a mock implementation for demonstration
            sneakers = [
                Sneaker(
                    name=f"Nike Air Max {i}",
                    brand="Nike",
                    price=119.99 + i,
                    image_url=f"https://static.nike.com/a/images/c_limit,w_592,f_auto/t_product_v1/sample{i}.jpg",
                    product_url=f"https://www.nike.com/t/air-max-{i}",
                    site="nike",
                    available_sizes=["8", "9", "10", "11", "12"]
                )
                for i in range(1, min(limit + 1, 21))
            ]
            
            return sneakers
            
        except httpx.HTTPError as e:
            # Handle error - in production, log this
            raise HTTPException(status_code=503, detail=f"Failed to fetch data from Nike: {str(e)}")

# dummy data
async def scrape_footlocker(brand: Optional[str] = None, limit: int = 20) -> List[Sneaker]:
    """Scrape Footlocker website for sneakers"""
    url = "https://www.footlocker.com/category/shoes.html"
    if brand:
        # In a real implementation, you'd modify the URL to include brand filter
        pass
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            
            # Mock implementation for demonstration
            sneakers = [
                Sneaker(
                    name=f"Footlocker Exclusive {i}",
                    brand="Adidas" if i % 2 == 0 else "Nike",
                    price=89.99 + i,
                    image_url=f"https://images.footlocker.com/is/image/product{i}",
                    product_url=f"https://www.footlocker.com/product/model/sneaker-{i}",
                    site="footlocker",
                    available_sizes=["7", "8", "9", "10", "11"] 
                )
                for i in range(1, min(limit + 1, 21))
            ]
            
            return sneakers
            
        except httpx.HTTPError as e:
            # Handle error
            raise HTTPException(status_code=503, detail=f"Failed to fetch data from Footlocker: {str(e)}")
