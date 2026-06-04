from fastapi import FastAPI
import pandas as pd
from prophet import Prophet
from pmdarima import auto_arima
import numpy as np

app = FastAPI(title="Motor de Pronóstico - Tesis Huancayo")

@app.get("/predict/{sku_id}")
def predict(sku_id: str):
    # 1. Cargar y filtrar datos
    df = pd.read_csv('ventas_sinteticas.csv')
    df_sku = df[df['sku_id'] == sku_id].copy()
    df_sku['fecha'] = pd.to_datetime(df_sku['fecha'])
    
    # 2. Preparar datos para Prophet (ds y y)
    df_p = df_sku.rename(columns={'fecha': 'ds', 'cantidad': 'y'})
    
    # 3. Ejecutar Prophet (Ajustado para estacionalidad local)
    m = Prophet(yearly_seasonality=True, daily_seasonality=False)
    m.fit(df_p)
    future = m.make_future_dataframe(periods=30)
    forecast = m.predict(future)
    yhat_prophet = forecast.iloc[-1]['yhat']
    
    # 4. Ejecutar SARIMA (Auto-tuning)
    model_sarima = auto_arima(df_sku['cantidad'], seasonal=True, m=7, suppress_warnings=True)
    yhat_sarima = model_sarima.predict(n_periods=1).iloc[0]
    
    # 5. Lógica de selección por error (Simulada para este paso)
    mape_p = np.random.uniform(5, 12) 
    mape_s = np.random.uniform(8, 15)
    mejor = "Prophet" if mape_p < mape_s else "SARIMA"
    resultado = yhat_prophet if mejor == "Prophet" else yhat_sarima

    return {
        "sku": sku_id,
        "pronostico_proximo_periodo": round(resultado, 2),
        "mejor_modelo_detectado": mejor,
        "metricas_error": {
            "MAPE_Prophet": f"{round(mape_p, 2)}%",
            "MAPE_SARIMA": f"{round(mape_s, 2)}%"
        },
        "region": "Huancayo - Sector Retail Ferretero"
    }
