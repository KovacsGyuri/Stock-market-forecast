# SYSTEM DESIGN

## Stock Market Forecast -- Rendszerterv és műszaki specifikáció

**Dokumentum típusa:** Rendszerterv\
**Projekt:** Stock Market Forecast\
**Verzió:** 1.0\
**Státusz:** Tervezési dokumentum

------------------------------------------------------------------------

## 1. A projekt áttekintése

A Stock Market Forecast egy webalkalmazás, amely lehetővé teszi a
felhasználók számára kiválasztott részvények múltbeli árfolyamadatainak
lekérését, grafikus megjelenítését és rövid távú árfolyam-előrejelzés
készítését.

A rendszer külső adatforrásból, a Yahoo Finance szolgáltatásból szerzi
be az árfolyamadatokat a Python `yfinance` könyvtár segítségével. A
lekért adatokat a backend feldolgozza, majd API-n keresztül továbbítja a
frontend számára. A felhasználó az adatokat és az előrejelzést
interaktív grafikonon tekintheti meg.

A projekt elsődleges célja egy működő, könnyen használható és oktatási
célokra is alkalmas részvényárfolyam-elemző alkalmazás létrehozása.

## 2. Üzleti és rendszerkövetelmények

### 2.1. Funkcionális követelmények

-   A felhasználó részvényszimbólum (ticker), például `AAPL` megadásával
    kiválaszthatja a vizsgálni kívánt részvényt.
-   A rendszer lekéri a kiválasztott részvény historikus árfolyamadatait
    a Yahoo Finance szolgáltatásból.
-   A rendszer ellenőrzi, hogy a megadott tickerhez elérhető-e megfelelő
    adat.
-   A historikus árfolyamadatok grafikus formában jelennek meg.
-   A rendszer statisztikai módszerrel előrejelzést készít a
    kiválasztott részvény várható árfolyamára.
-   Az előrejelzés mellett 95%-os predikciós intervallum jelenik meg.
-   A felhasználó választhat rövid és hosszabb előrejelzési időtáv
    között.
-   A rendszer érthető hibaüzenetet ad hibás ticker, hiányzó adat vagy
    külső adatforrás-hiba esetén.

### 2.2. Nem funkcionális követelmények

-   A webalkalmazás böngészőből legyen használható.
-   A backend Python-alapú, a frontend HTML, CSS és JavaScript
    technológiákat használjon.
-   A grafikon legyen áttekinthető, és különböztesse meg a múltbeli
    adatokat az előrejelzéstől.
-   A rendszer kezelje a külső adatforrás átmeneti elérhetetlenségét.
-   A kód legyen moduláris és a GitHubon közösen fejleszthető.
-   A fejlesztés és az elsődleges tesztelés helyi környezetben
    (localhost) történjen.

## 3. Alkalmazott technológiák

  -------------------------------------------------------------------------
  Rendszerelem            Technológia             Feladat
  ----------------------- ----------------------- -------------------------
  Backend                 Python                  Üzleti logika és
                                                  adatfeldolgozás

  Webes keretrendszer     FastAPI                 HTTP-végpontok és API

  ASGI-kiszolgáló         Uvicorn                 A FastAPI alkalmazás
                                                  futtatása

  Adatlekérés             yfinance                Részvényárfolyam-adatok
                                                  lekérése

  Frontend                HTML, CSS, JavaScript   Felhasználói felület

  Sablonkezelés           Jinja2                  HTML-oldalak kiszolgálása

  Grafikon                Chart.js                Historikus adatok és
                                                  előrejelzés megjelenítése

  Verziókezelés           Git és GitHub           Közös fejlesztés és
                                                  forráskód-kezelés
  -------------------------------------------------------------------------

## 4. Rendszerarchitektúra

A rendszer három fő rétegből épül fel:

1.  **Frontend:** A felhasználói felület, ahol a ticker megadása, az
    időtáv kiválasztása és az eredmények megtekintése történik.
2.  **Backend:** A FastAPI-alapú alkalmazás, amely fogadja a kéréseket,
    lekéri és feldolgozza az adatokat, majd előállítja az előrejelzést.
3.  **Külső adatforrás:** A Yahoo Finance, ahonnan a historikus
    részvényárfolyamok érkeznek.

### 4.1. A rendszer működési folyamata

1.  A felhasználó megnyitja az alkalmazást a böngészőben.
2.  Megadja a részvény ticker szimbólumát.
3.  Kiválasztja az előrejelzés időtávját.
4.  A frontend API-kérést küld a FastAPI backendnek.
5.  A backend a `yfinance` segítségével lekéri a historikus
    árfolyamadatokat.
6.  A backend ellenőrzi és előkészíti az adatokat.
7.  Az előrejelző modul kiszámítja a trendet és a 95%-os predikciós
    intervallumot.
8.  A backend JSON formátumban visszaküldi az eredményt.
9.  A frontend a Chart.js segítségével megjeleníti a historikus
    árfolyamot, az előrejelzést és a bizonytalansági tartományt.

### 4.2. Logikai architektúra

``` text
Felhasználó
    |
    v
Böngésző – HTML / CSS / JavaScript
    |
    | HTTP-kérés
    v
FastAPI backend
    |
    +----------------------+
    |                      |
    v                      v
Adatlekérő modul       Előrejelző modul
    |                      |
    v                      v
Yahoo Finance          Trend + 95%-os
(yfinance)             predikciós intervallum
    |                      |
    +-----------+----------+
                |
                v
         JSON válasz
                |
                v
      Chart.js grafikon
```

## 5. Adatlekérés és -feldolgozás

A rendszer a Yahoo Finance adatforrásból kér le historikus
részvényárfolyamokat a Python `yfinance` könyvtár segítségével.

Az előrejelzés alapjául elsősorban a napi záróárfolyamok szolgálnak. A
lekért adatokat a backend ellenőrzi, és kiszűri azokat az eseteket,
amikor az adatsor üres vagy nem megfelelő a számításhoz.

A rendszernek kezelnie kell többek között: - a nem létező vagy hibás
ticker szimbólumot; - az üres adatlekérést; - a hiányzó vagy nem
numerikus árfolyamértékeket; - a Yahoo Finance szolgáltatás
elérhetetlenségét; - az előrejelzéshez nem elegendő adatmennyiséget.

A lekért adatok átmeneti gyorsítótárazása tervezett optimalizáció, amely
csökkentheti a felesleges külső kérések számát. A gyorsítótár
érvényességi idejét a megvalósítás során kell meghatározni.

## 6. Előrejelzési modell

### 6.1. A modell célja

A rendszer célja, hogy a historikus részvényárfolyamok alapján rövid
távú becslést készítsen a jövőbeli árfolyam alakulásáról. Az előrejelzés
tájékoztató jellegű, nem tekinthető befektetési tanácsadásnak.

### 6.2. Tervezett módszer

A projektben logaritmikus árfolyamokra illesztett lineáris trendmodell
alkalmazása tervezett:

`log(P) = a + b * t + ε`

ahol: - `P` az árfolyam; - `t` az idő; - `a` a modell konstans tagja; -
`b` a becsült trend meredeksége; - `ε` a modell hibája.

A modell a historikus adatok alapján becsüli meg a trendet, majd a
becsült értékeket visszaalakítja az eredeti árfolyamskálára.

### 6.3. 95%-os predikciós intervallum

Az előrejelzéshez 95%-os predikciós intervallum is készül. Ez azt a
bizonytalansági tartományt mutatja, amelyen belül a modell
feltételezései mellett egy jövőbeli megfigyelés várhatóan
elhelyezkedhet.

A predikciós intervallum számításánál figyelembe kell venni a modell
maradékszórását, az előrejelzési pont távolságát a historikus adatok
átlagos időpontjától, valamint a megfelelő Student-féle t-kritikus
értéket. A logaritmikus skálán számított alsó és felső határokat
exponenciálással kell visszaalakítani.

Fontos különbség, hogy a predikciós intervallum egy jövőbeli
árfolyam-megfigyelés bizonytalanságát mutatja, nem csupán a becsült
átlagos trend bizonytalanságát. A tényleges lefedettség a modell
feltételezéseitől és a piaci folyamatoktól függ.

### 6.4. Előrejelzési időtáv

A tervezett választható időtáv: - 7 kereskedési nap; - 30 kereskedési
nap.

A kereskedési napok nem azonosak a naptári napokkal, ezért a hétvégéket
és a tőzsdei szünnapokat figyelembe kell venni.

### 6.5. A modell korlátai

A részvényárfolyamokat számos, előre nem jelezhető tényező befolyásolja.
Egy egyszerű trendmodell nem képes minden piaci eseményt, hírt vagy
hirtelen árfolyamváltozást előre jelezni. Ezért az eredmény becslésként
jelenik meg, és nem garantálja a jövőbeli árfolyamot.

A modell minőségét historikus adatokon végzett visszateszteléssel
célszerű értékelni.

## 7. API-terv

A frontend és a backend HTTP-alapú API-n keresztül kommunikál. Az API
JSON formátumban adja vissza az adatokat.

  --------------------------------------------------------------------------
  Végpont                    Metódus                 Feladat
  -------------------------- ----------------------- -----------------------
  `/`                        GET                     A főoldal megjelenítése

  `/api/stock/{symbol}`      GET                     A kiválasztott részvény
                                                     historikus adatainak
                                                     lekérése

  `/api/forecast/{symbol}`   GET                     Előrejelzés és
                                                     predikciós intervallum
                                                     visszaadása

  `/api/health`              GET                     A backend működésének
                                                     ellenőrzése
  --------------------------------------------------------------------------

Az API pontos paramétereit és válaszstruktúráját a fejlesztés során kell
véglegesíteni. A részvény ticker és az előrejelzési időtáv validálása
backend oldalon is szükséges.

## 8. Adatkezelés és gyorsítótárazás

A projekt első változatában nem szükséges külön adatbázis használata,
mivel az árfolyamadatok külső szolgáltatásból lekérhetők, és a
számítások futás közben elvégezhetők.

A rendszer tervezett adatkezelése: - a historikus árfolyamadatok
lekérése a Yahoo Finance szolgáltatásból; - az adatok ideiglenes
tárolása a feldolgozás idejére; - opcionális gyorsítótárazás a gyakori
lekérések csökkentésére; - az előrejelzési eredmények továbbítása a
frontendnek.

A felhasználók személyes adatainak tárolása a projekt jelenlegi
hatókörében nem tervezett.

## 9. Futtatási és fejlesztési környezet

A projekt elsődleges fejlesztési és tesztelési környezete a helyi
számítógépen futó localhost.

A csapattagok a GitHub repository klónozásával saját számítógépükön
futtatják az alkalmazást. A backend Uvicorn segítségével indítható, a
felület pedig böngészőből érhető el.

Példa helyi cím: - Alkalmazás: `http://127.0.0.1:8000/` - API
dokumentáció: `http://127.0.0.1:8000/docs`

A localhost nem jelent nyilvános internetes telepítést: az alkalmazás az
adott fejlesztő saját gépén fut. A Yahoo Finance adatainak lekéréséhez
internetkapcsolat szükséges.

A Render.com korábban felmerült telepítési lehetőségként, de a projekt
jelenlegi elsődleges fejlesztési és tesztelési környezete a localhost.

## 10. GitHub és csapatmunka

A forráskód és a projekt dokumentációja GitHub repositoryban kerül
kezelésre.

A csapatmunka során: - minden fejlesztő a közös repositoryból
dolgozik; - a módosításokat Git segítségével verziókezelik; - a
feladatokat egymás között felosztják; - a nagyobb módosításokat célszerű
külön branch-en elkészíteni; - a kész módosításokat ellenőrzés után
lehet a fő ágba egyesíteni.

A rendszerterv a repository gyökérkönyvtárában `SYSTEM_DESIGN.md` néven
helyezhető el.

## 11. Tesztelési terv

A rendszer tesztelése több területre terjed ki.

### 11.1. Funkcionális tesztek

-   Érvényes ticker megadása esetén a rendszer lekéri és megjeleníti az
    adatokat.
-   Hibás ticker esetén megfelelő hibaüzenet jelenik meg.
-   Üres adatlekérés esetén a rendszer nem készít hibás előrejelzést.
-   A 7 és 30 kereskedési napos időtáv helyesen működik.
-   A grafikon külön jelöli a historikus árfolyamot és az előrejelzést.
-   A predikciós intervallum alsó és felső határa megjelenik.

### 11.2. Technikai tesztek

-   Az API-végpontok válaszainak ellenőrzése.
-   A ticker és az időtáv bemeneti validálása.
-   Külső adatforrás-hiba kezelése.
-   Az előrejelző modell számításainak ellenőrzése ismert tesztadatokon.
-   A grafikon adatainak és címkéinek ellenőrzése.

### 11.3. Modellértékelés

A modell teljesítményét historikus adatokon végzett visszateszteléssel
kell értékelni. Célszerű vizsgálni az előrejelzési hibát, valamint azt,
hogy a tényleges árfolyam milyen gyakran esik a 95%-os predikciós
intervallumba.

## 12. Elfogadási kritériumok

A rendszer akkor tekinthető a projekt céljainak megfelelően
elkészültnek, ha: 1. A felhasználó meg tud adni egy érvényes részvény
tickert. 2. A rendszer képes historikus árfolyamadatokat lekérni. 3. Az
árfolyamadatok áttekinthető grafikonon jelennek meg. 4. A rendszer a
kiválasztott időtávra előrejelzést készít. 5. A grafikon a becsült trend
mellett a 95%-os predikciós intervallumot is megjeleníti. 6. A hibás
bemeneteket és adatlekérési problémákat a rendszer megfelelően kezeli.
7. Az alkalmazás a csapattagok helyi fejlesztői környezetében
futtatható. 8. A forráskód és a dokumentáció elérhető a közös GitHub
repositoryban.

## 13. Összefoglalás

A Stock Market Forecast rendszer egy Python és FastAPI alapú
webalkalmazás, amely a Yahoo Finance adataira támaszkodva jeleníti meg a
részvények historikus árfolyamát, és trendalapú előrejelzést készít
95%-os predikciós intervallummal.

A frontend HTML, CSS, JavaScript és Chart.js technológiákat használ. A
fejlesztés és a tesztelés elsődleges környezete a localhost, a közös
munkát pedig GitHub támogatja.

Ez a dokumentum a tervezett rendszer műszaki felépítését írja le. A
benne szereplő funkciók és végpontok a megvalósítás során kerülnek
kialakításra; nem jelenti azt, hogy valamennyi funkció már elkészült.
