from fastapi import APIRouter
from playwright.async_api import async_playwright

router=APIRouter(
    prefix="/ipc",
    tags=["ipc"]
)

@router.get("/")
async def get_ipc():
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
            "proximo": "#contenidoPrincipal > div:nth-child(1) > div.col-md-12.pr-5r.pl-5r.pt-4 > div > div > div > div:nth-child(2) > div.col-md-9 > div > p:nth-child(8)"
        }
        resultados={}
        for nombre, selector in selectores.items():
            elementos = await page.query_selector_all(selector)
            textos = [ await el.inner_text() for el in elementos if el]
            resultados [nombre]= " ".join(t.strip() for t in textos if t.strip())
        await browser.close()
        return resultados