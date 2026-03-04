# ============================================
# SMART ACADEMIC ANALYTICS ENGINE PRO MAX
# Corre TODO desde Python
# ============================================

import pandas as pd
import matplotlib.pyplot as plt
import json
from flask import Flask, render_template_string
import os

app = Flask(__name__)

# ============================================
# 1️⃣ ANALISIS AUTOMATICO AL INICIAR
# ============================================

def generar_analisis():

    print("\n=== SMART ACADEMIC ANALYSIS PRO ===\n")

    df = pd.read_csv("datos_rendimiento_universidad_limpio.csv")

    df["reprobado"] = df["calificacion"] < 6

    # Reprobación por materia
    reprobacion_materia = (
        df.groupby("materia")["reprobado"]
        .mean() * 100
    ).sort_values(ascending=False)

    # Promedio por carrera
    promedio_carrera = (
        df.groupby("carrera")["calificacion"]
        .mean()
        .sort_values(ascending=False)
    )

    # Promedio por semestre
    promedio_semestre = df.groupby("semestre")["calificacion"].mean()

    # Estudiantes en riesgo
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

    print("🔥 resultados.json generado correctamente")


# Ejecutar análisis al iniciar
generar_analisis()


# ============================================
# 2️⃣ DASHBOARD HTML ULTRA ANIMADO
# ============================================

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Smart Academic Intelligence PRO</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body{
    background: linear-gradient(135deg,#0f172a,#1e293b);
    color:white;
    font-family:system-ui;
}

.card{
    background:rgba(30,41,59,.9);
    backdrop-filter: blur(10px);
    border-radius:18px;
    padding:25px;
    box-shadow:0 20px 40px rgba(0,0,0,.5);
    transition:.4s;
}
.card:hover{
    transform: translateY(-6px) scale(1.02);
}

.fade-in{
    animation: fadeIn 1s ease forwards;
    opacity:0;
}
@keyframes fadeIn{
    to{opacity:1;}
}

.glow{
    animation: glow 2s infinite alternate;
}
@keyframes glow{
    from{ text-shadow:0 0 10px #6366f1; }
    to{ text-shadow:0 0 25px #9333ea; }
}
</style>
</head>

<body class="p-10">

<h1 class="text-5xl font-bold mb-10 glow">
🚀 Smart Academic Intelligence PRO
</h1>

<div class="grid md:grid-cols-2 gap-10">

<div class="card fade-in">
<h2 class="text-2xl mb-6">📉 Reprobación por Materia</h2>
<canvas id="chartMaterias"></canvas>
</div>

<div class="card fade-in">
<h2 class="text-2xl mb-6">🏆 Promedio por Carrera</h2>
<canvas id="chartCarreras"></canvas>
</div>

</div>

<div class="card mt-10 fade-in">
<h2 class="text-2xl mb-6">⚠ Estudiantes en Riesgo</h2>
<table class="w-full">
<thead>
<tr class="border-b border-gray-600">
<th>ID</th>
<th>Promedio</th>
<th>Reprobadas</th>
</tr>
</thead>
<tbody id="tablaRiesgo"></tbody>
</table>
</div>

<script>
async function cargarDatos(){
    const res = await fetch("/resultados.json");
    const data = await res.json();

    // MATERIAS
    new Chart(document.getElementById('chartMaterias'),{
        type:'bar',
        data:{
            labels:Object.keys(data.reprobacion_materia),
            datasets:[{
                data:Object.values(data.reprobacion_materia),
                backgroundColor:'rgba(239,68,68,.85)',
                borderRadius:10
            }]
        },
        options:{
            animation:{duration:2000},
            scales:{y:{beginAtZero:true,max:100}},
            plugins:{legend:{display:false}}
        }
    });

    // CARRERAS
    new Chart(document.getElementById('chartCarreras'),{
        type:'line',
        data:{
            labels:Object.keys(data.promedio_carrera),
            datasets:[{
                data:Object.values(data.promedio_carrera),
                borderColor:'#6366f1',
                backgroundColor:'rgba(99,102,241,.2)',
                fill:true,
                tension:.4
            }]
        },
        options:{
            animation:{duration:2000},
            scales:{y:{beginAtZero:true,suggestedMax:10}},
            plugins:{legend:{display:false}}
        }
    });

    // TABLA
    const tbody=document.getElementById("tablaRiesgo");
    data.estudiantes_riesgo.forEach(e=>{
        tbody.innerHTML+=`
        <tr class="border-b border-gray-700 hover:bg-gray-800 transition">
            <td class="py-2">${e.id_estudiante}</td>
            <td>${e.promedio.toFixed(2)}</td>
            <td class="text-red-400 font-bold">${e.reprobadas}</td>
        </tr>`;
    });
}

cargarDatos();
</script>

</body>
</html>
"""


# ============================================
# 3️⃣ RUTAS FLASK
# ============================================

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/resultados.json")
def resultados():
    with open("resultados.json", encoding="utf-8") as f:
        return json.load(f)

# ============================================
# 4️⃣ INICIAR SERVIDOR
# ============================================

if __name__ == "__main__":
    app.run(debug=True)