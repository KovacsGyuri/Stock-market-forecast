import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import yfinance as yf
from functools import lru_cache

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@lru_cache(maxsize=32)
def get_cached_stock_data(symbol: str, days: int = 7):
    try:
        # Egyedi session létrehozása User-Agenttel, hogy a Yahoo ne blokkolja a Render kéréseit
        session = requests.Session()
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        
        stock = yf.Ticker(symbol, session=session)
        hist = stock.history(period="3mo" if days > 7 else "1mo")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"Nem található adat a következő szimbólumhoz: {symbol}")
        
        prices = [round(float(price), 2) for price in hist['Close'].tail(10).tolist()]
        
        last_price = prices[-1]
        prediction = [round(last_price * (1 + 0.002 * i), 2) for i in range(1, days + 1)]
        
        history_labels = [f"Múlt -{len(prices)-i}" for i in range(len(prices))]
        prediction_labels = [f"Előrejelzés +{i}. nap" for i in range(1, days + 1)]
        
        return {
            "symbol": symbol.upper(),
            "prices": prices,
            "prediction": prediction,
            "history_labels": history_labels,
            "prediction_labels": prediction_labels
        }
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