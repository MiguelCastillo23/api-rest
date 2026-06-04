from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="Motor de Recomendación - Tesis Huancayo")

# --- CONFIGURACIÓN DE CORS (OPCIÓN A) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite conexiones externas desde Windows
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STOCK_SEGURIDAD_PORCENTAJE = 0.15 

@app.get("/recomendar/{sku_id}")
async def recomendar(sku_id: str, stock_actual: float):
    timeout = httpx.Timeout(30.0, read=30.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(f"http://localhost:8002/predict/{sku_id}")
        data_pronostico = response.json()
    
    pronostico = data_pronostico["pronostico_proximo_periodo"]
    stock_seguridad = pronostico * STOCK_SEGURIDAD_PORCENTAJE
    cantidad_a_comprar = pronostico + stock_seguridad - stock_actual
    
    cantidad_final = max(0, round(cantidad_a_comprar, 2))

    return {
        "sku": sku_id,
        "analisis": {
            "pronostico_demanda": pronostico,
            "stock_actual": stock_actual,
            "stock_seguridad_sugerido": round(stock_seguridad, 2)
        },
        "decision_compra": {
            "cantidad_a_pedir": cantidad_final,
            "unidad": "Unidades/Bolsas",
            "mensaje": f"Se recomienda pedir {cantidad_final} unidades para cubrir la demanda."
        }
    }
