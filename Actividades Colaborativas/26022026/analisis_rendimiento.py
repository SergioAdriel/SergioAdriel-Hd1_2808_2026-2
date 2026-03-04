# Carlos
# sergio 

import pandas as pd
import matplotlib.pyplot as plt
import json

print("\n=== SMART ACADEMIC ANALYSIS ===\n")

# =============================
# CARGAR DATOS
# =============================
df = pd.read_csv("datos_rendimiento_universidad_limpio.csv")
print("✅ Datos cargados\n")

# =============================
# 1. REPROBACIÓN POR MATERIA
# =============================
df["reprobado"] = df["calificacion"] < 6

reprobacion_materia = (
    df.groupby("materia")["reprobado"]
    .mean() * 100
).sort_values(ascending=False)

print("Reprobación por materia (%)")
print(reprobacion_materia, "\n")

plt.figure()
reprobacion_materia.plot(kind="bar")
plt.title("Reprobación por materia (%)")
plt.ylabel("%")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("grafica_reprobacion.png")

# =============================
# 2. PROMEDIO POR CARRERA
# =============================
promedio_carrera = (
    df.groupby("carrera")["calificacion"]
    .mean()
    .sort_values(ascending=False)
)

print("Promedio por carrera")
print(promedio_carrera, "\n")

plt.figure()
promedio_carrera.plot(kind="bar")
plt.title("Promedio por carrera")
plt.ylabel("Promedio")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("grafica_carreras.png")

# =============================
# 3. TENDENCIA POR SEMESTRE
# =============================
promedio_semestre = df.groupby("semestre")["calificacion"].mean()

print("Promedio por semestre")
print(promedio_semestre, "\n")

plt.figure()
promedio_semestre.plot(marker="o")
plt.title("Promedio por semestre")
plt.xlabel("Semestre")
plt.ylabel("Promedio")
plt.tight_layout()
plt.savefig("grafica_semestre.png")

# =============================
# 4. DETECTAR ESTUDIANTES EN RIESGO
# =============================
promedio_estudiante = df.groupby("id_estudiante")["calificacion"].mean()

reprobadas = (
    df[df["calificacion"] < 6]
    .groupby("id_estudiante")
    .size()
)

riesgo = pd.DataFrame({
    "promedio": promedio_estudiante,
    "reprobadas": reprobadas
}).fillna(0)

riesgo["en_riesgo"] = (
    (riesgo["promedio"] < 6.5) |
    (riesgo["reprobadas"] >= 1)
)

print("Estudiantes en riesgo:")
print(riesgo[riesgo["en_riesgo"]])

# =============================
# EXPORTAR RESULTADOS A JSON
# =============================
resultados = {
    "reprobacion_materia": reprobacion_materia.to_dict(),
    "promedio_carrera": promedio_carrera.to_dict(),
    "promedio_semestre": promedio_semestre.to_dict(),
    "estudiantes_riesgo":
        riesgo[riesgo["en_riesgo"]]
        .reset_index()
        .to_dict(orient="records")
}

with open("resultados.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=4, ensure_ascii=False)


print("\n🔥 resultados.json generado correctamente")
