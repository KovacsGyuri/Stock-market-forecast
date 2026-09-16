from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Stock Predictor Project")

# HTML sablonok betöltése a templates mappából
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Itt jelenítjük meg a főoldalt
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    # Ide jön majd az igazi API hívás (pl. Yahoo Finance)
    # Most mock (minta) adatokat küldünk vissza tesztelésre
    mock_data = {
        "symbol": symbol.upper(),
        "prices": [150, 152, 155, 153, 158, 160, 165], # Múltbeli adatok
        "prediction": [168, 172]                         # Előrejelzett adatok
    }
    return mock_data
