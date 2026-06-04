import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generar_ventas(sku, dias=730):
    fechas = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(dias)]
    base = 50 
    data = []
    for f in fechas:
        estacionalidad = 15 * np.sin(2 * np.pi * f.timetuple().tm_yday / 365)
        pico_huancayo = 25 if f.month in [7, 10, 11] else 0
        ruido = np.random.normal(0, 5)
        cantidad = max(0, int(base + estacionalidad + pico_huancayo + ruido))
        data.append([f, sku, cantidad])
    return pd.DataFrame(data, columns=['fecha', 'sku_id', 'cantidad'])

df_final = pd.concat([generar_ventas(s) for s in ['SKU-001', 'SKU-002', 'SKU-003']])
df_final.to_csv('ventas_sinteticas.csv', index=False)
print("--- ARCHIVO ventas_sinteticas.csv CREADO CON ÉXITO ---")
