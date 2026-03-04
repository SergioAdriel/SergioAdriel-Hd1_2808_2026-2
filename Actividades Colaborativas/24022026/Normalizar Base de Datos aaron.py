import pandas as pd
import unicodedata

# Funcion para quitar acentos de un texto
def quitar_acentos(texto):
    # Mantener NaN tal cual
    if pd.isna(texto):
        return texto
    # Si no es string, devolverlo sin cambios
    if not isinstance(texto, str):
        return texto
    # Normaliza y elimina marcas diacríticas (acentos)
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')

df = pd.read_csv("datos_rendimiento_universidad.csv")

# Quitar acentos de todas las columnas de tipo object (texto)
cols_obj = df.select_dtypes(include=['object']).columns.tolist()
for col in cols_obj:
    for i in range(len(df)):
        try:
            df.at[i, col] = quitar_acentos(df.at[i, col])
        except Exception:
            pass

# Quitamos duplicados (si es que hay)
df = df.drop_duplicates()

df.to_csv("datos_rendimiento_universidad_limpio.csv", index=False)