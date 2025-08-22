from fastapi import APIRouter,HTTPException
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import logging
import redis.asyncio as redis
import json
import os


router=APIRouter(
    prefix="/ipc",
    tags=["ipc"]
)

logging.basicConfig(level=logging.INFO)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True  # para que devuelva strings
)

CACHE_KEY = "ipc_data"
CACHE_TTL = 43200  # 12 horas

@router.get("/")
async def get_ipc():
    browser=None
    try:
        cached_data=await redis_client.get(CACHE_KEY)
        if cached_data:
            logging.info("Datos cargados desde redis")
            return json.loads(cached_data)
        logging.info("Consultando sitio del INDEC...")
        async with async_playwright() as p:
            browser= await p.chromium.launch(headless=True)
            context= await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page= await context.new_page()
            await page.goto("https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31", timeout=10000)
            await page.wait_for_load_state("networkidle")
            selectores={
                "fecha": "#contenidoPrincipal > div:nth-child(1) > div.col-md-12.pr-5r.pl-5r.pt-4 > div > div > div > div:nth-child(1) > div.col-md-9 > div",
                "informe": "#contenidoPrincipal > div:nth-child(1) > div.col-md-12.pr-5r.pl-5r.pt-4 > div > div > div > div:nth-child(2) > div.col-md-9 > div > p:nth-child(1)",
                "proximo": "#contenidoPrincipal > div:nth-child(1) > div.col-md-12.pr-5r.pl-5r.pt-4 > div > div > div > div:nth-child(2) > div.col-md-9 > div > p:nth-child(2)"
            }
            resultados={}
            for nombre, selector in selectores.items():
                elementos = await page.query_selector_all(selector)
                textos = [ await el.inner_text() for el in elementos if el]
                resultados [nombre]= " ".join(t.strip() for t in textos if t.strip())
            await redis_client.set(CACHE_KEY, json.dumps(resultados), ex=CACHE_TTL)
            logging.info("Datos almacenados en caché Redis.")
            return resultados
    except PlaywrightTimeoutError:
        raise HTTPException(status_code=504, detail="Tiempo de espera agotado al cargar la página")
    except Exception as e:
        logging.exception("Error al obtener datos del IPC")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    finally:
        if browser:
            await browser.close()