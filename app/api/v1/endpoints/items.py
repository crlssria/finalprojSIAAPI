from fastapi import APIRouter, HTTPException, Query,Depends
from typing import List, Dict
from app.schemas.item import Item, ItemCreate
from app.db.mongodb import mongodb
from app.core.config import settings
import requests
from datetime import datetime, timedelta
import logging

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)


def fetch_spot_prices() -> Dict[str, Dict]:
    metals = ["XAU", "XAG", "XPT", "XPD"]  # Gold, Silver, Platinum, Palladium
    prices = {}
    headers = {
        "x-access-token": settings.api_key,
        "Content-Type": "application/json"
    }
    for metal in metals:
        url = f"https://www.goldapi.io/api/{metal}/USD"
        logging.debug(f"Fetching spot prices with URL: {url} and headers: {headers}")
        response = requests.get(url, headers=headers)
        logging.debug(f"Response status code: {response.status_code}, response body: {response.text}")
        response.raise_for_status()
        data = response.json()
        if 'timestamp' in data:
            try:
                timestamp = data['timestamp']
                # Check if timestamp is in seconds or milliseconds
                if len(str(timestamp)) == 10:
                    timestamp *= 1000
                data['timestamp'] = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
            except (OSError, ValueError):
                data['timestamp'] = data['timestamp']
        prices[metal] = data
    return prices

def fetch_historical_prices(metal: str, start_date: str, end_date: str) -> List[Dict]:
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    historical_data = []
    
    headers = {
        "x-access-token": settings.api_key,
        "Content-Type": "application/json"
    }
    
    while current_date <= end_date:
        url = f"https://www.goldapi.io/api/{metal}/USD/{current_date.strftime('%Y%m%d')}"
        logging.debug(f"Fetching historical prices with URL: {url} and headers: {headers}")
        response = requests.get(url, headers=headers)
        logging.debug(f"Response status code: {response.status_code}, response body: {response.text}")
        if response.status_code == 200:
            data = response.json()
            if "price" in data:
                historical_data.append(data)
            else:
                logging.debug(f"No price data available for {metal} on {current_date.strftime('%Y-%m-%d')}")
        current_date += timedelta(days=1)
    
    return historical_data

@router.get("/historical-prices")
def get_historical_prices(
    metal: str = Query(..., description="Metal symbol (e.g., XAU, XAG, XPT, XPD)"),
    start_date: str = Query(..., description="Start date in the format YYYY-MM-DD"),
    end_date: str = Query(..., description="End date in the format YYYY-MM-DD")
):
    try:
        historical_prices = fetch_historical_prices(metal, start_date, end_date)
        if not historical_prices:
            return {"error": "No historical data available for the specified date range."}
        return historical_prices
    except requests.RequestException as e:
        logging.error(f"Error fetching historical prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def fetch_conversion_rate(target_currency: str) -> float:
    url = f"https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data["rates"].get(target_currency, 1)

@router.get("/", response_model=List[Item])
async def read_items(skip: int = 0, limit: int = 10):
    items = await mongodb.db.items.find().skip(skip).limit(limit).to_list(length=limit)
    for item in items:
        item["_id"] = str(item["_id"])
    return items

@router.post("/", response_model=Item)
async def create_item(item: ItemCreate):
    new_item = item.dict()
    result = await mongodb.db.items.insert_one(new_item)
    created_item = await mongodb.db.items.find_one({"_id": result.inserted_id})
    created_item["_id"] = str(created_item["_id"])
    return created_item

@router.get("/spot-prices")
def get_spot_prices():
    try:
        prices = fetch_spot_prices()
        return prices
    except requests.RequestException as e:
        logging.error(f"Error fetching spot prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert")
def convert_metal_price(metal: str, target_currency: str):
    try:
        spot_prices = fetch_spot_prices()
        if metal not in spot_prices:
            raise HTTPException(status_code=400, detail=f"Invalid metal: {metal}")
        metal_price = spot_prices[metal]["price"]
        conversion_rate = fetch_conversion_rate(target_currency)
        converted_price = metal_price * conversion_rate
        return {"converted_price": converted_price}
    except Exception as e:
        logging.error(f"Error converting metal price: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/currencies")
def get_available_currencies():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        currencies = list(data["rates"].keys())
        return {"currencies": currencies}
    except requests.RequestException as e:
        logging.error(f"Error fetching currencies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
