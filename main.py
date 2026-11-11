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
        stock = yf.Ticker(symbol)
        # Ha 30 napos előrejelzést kérünk, több múltbeli adatot töltünk be
        hist = stock.history(period="3mo" if days > 7 else "1mo")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"Nem található adat a következő szimbólumhoz: {symbol}")
        
        # Múltbeli záró árak (az utolsó 10 nap)
        prices = [round(float(price), 2) for price in hist['Close'].tail(10).tolist()]
        
        # Trend-alapú predikció a megadott napokra (7 vagy 30)
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
    # ITT A JAVÍTÁS: A request megy első helyen, a sablon neve a másodikon
    return templates.TemplateResponse(request, "index.html")

@app.get("/api/stock/{symbol}")
def get_stock(symbol: str, days: int = 7):
    if days not in [7, 30]:
        raise HTTPException(status_code=400, detail="Csak 7 vagy 30 napos időtáv engedélyezett.")
    return get_cached_stock_data(symbol, days)