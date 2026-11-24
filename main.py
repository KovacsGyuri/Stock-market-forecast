import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import yfinance as yf
from functools import lru_cache

from forecast import NotEnoughData, make_forecast

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@lru_cache(maxsize=32)
def get_cached_stock_data(symbol: str, days: int = 7):
    try:
        # Egyedi session létrehozása User-Agenttel, hogy a Yahoo ne blokkolja a Render kéréseit
        session = requests.Session()
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        
        stock = yf.Ticker(symbol, session=session)
        # A modellnek (forecast.py) legalább 30 kereskedési nap kell, ezért 6 hónapot kérünk le
        hist = stock.history(period="6mo")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"Nem található adat a következő szimbólumhoz: {symbol}")
        
        prices = [round(float(price), 2) for price in hist['Close'].tail(10).tolist()]
        
        # Előrejelzés a múltbeli adatokból: trend + 95%-os sáv (04-es jegy, forecast.py)
        try:
            result = make_forecast(hist['Close'], days)
        except NotEnoughData as e:
            raise HTTPException(status_code=422, detail=f"Nem sikerült előrejelzést készíteni: {e}")
        points = result["points"]
        prediction = [round(p["value"], 2) for p in points]
        
        history_labels = [f"Múlt -{len(prices)-i}" for i in range(len(prices))]
        prediction_labels = [f"Előrejelzés +{i}. nap" for i in range(1, days + 1)]
        
        return {
            "symbol": symbol.upper(),
            "prices": prices,
            "prediction": prediction,
            "prediction_lower": [round(p["lower"], 2) for p in points],
            "prediction_upper": [round(p["upper"], 2) for p in points],
            "prediction_dates": [p["date"] for p in points],
            "model": result["model"],
            "history_labels": history_labels,
            "prediction_labels": prediction_labels
        }
    except HTTPException:
        raise  # a saját hibakódjaink (404, 422) ne váljanak 500-assá
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hiba történt az adatok lekérésekor: {str(e)}")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/api/stock/{symbol}")
def get_stock(symbol: str, days: int = 7):
    if days not in [7, 30]:
        raise HTTPException(status_code=400, detail="Csak 7 vagy 30 napos időtáv engedélyezett.")
    return get_cached_stock_data(symbol, days)