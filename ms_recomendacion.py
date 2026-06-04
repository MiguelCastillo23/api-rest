from fastapi import FastAPI
import httpx

app = FastAPI(title="Motor de Recomendación - Tesis Huancayo")

# Configuración: Stock de Seguridad (15%)
STOCK_SEGURIDAD_PORCENTAJE = 0.15 

@app.get("/recomendar/{sku_id}")
async def recomendar(sku_id: str, stock_actual: float):
    # Definimos un timeout de 30 segundos para darle tiempo a Prophet de procesar
    timeout = httpx.Timeout(30.0, read=30.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Llamada al microservicio de pronóstico en el puerto 8002
        response = await client.get(f"http://localhost:8002/predict/{sku_id}")
        data_pronostico = response.json()
    
    pronostico = data_pronostico["pronostico_proximo_periodo"]
    
    # Lógica Logística
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
