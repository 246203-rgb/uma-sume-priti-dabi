from flask import Flask, render_template, request, jsonify
from base_prototipo import GrafoHerenciaUma, construir_grafo_desde_api
from datos_umamusumes import cargar_datos_csv 

app = Flask(__name__)

# ==========================================
# 🌟 1. EL MOTOR MATEMÁTICO (Azules y Rosas)
# ==========================================
def calcular_estrellas_necesarias(rango_actual, rango_meta):
    """Calcula cuántas estrellas totales de aptitud (Rosas) se necesitan."""
    valores_rango = {'G': 1, 'F': 2, 'E': 3, 'D': 4, 'C': 5, 'B': 6, 'A': 7, 'S': 8}
    
    rango_base = valores_rango.get(rango_actual.upper())
    rango_objetivo = valores_rango.get(rango_meta.upper())
    
    if not rango_base or not rango_objetivo: return 0
    delta_r = rango_objetivo - rango_base
    if delta_r <= 0: return 0
        
    if delta_r == 1: return 1
    elif delta_r == 2: return 4
    elif delta_r == 3: return 7
    elif delta_r >= 4: return 10
    return 0

IDS_ESTADISTICAS = {
    "speed": "10",
    "stamina": "20",
    "power": "30",
    "guts": "40",
    "wit": "50"
}

def calcular_prioridades_azules(bonos_crecimiento_uma, estrategia="parcheo"):
    """Calcula cuántas estrellas de estadísticas (Azules) pedir."""
    necesidades_azules = {}
    
    for stat_nombre, porcentaje_bono in bonos_crecimiento_uma.items():
        id_factor = IDS_ESTADISTICAS.get(stat_nombre.lower())
        if not id_factor: continue
            
        if estrategia == "parcheo":
            # Prioriza estadísticas donde la Uma no tiene bonos (0%)
            estrellas_a_pedir = 9 - int((porcentaje_bono / 20.0) * 9)
            necesidades_azules[id_factor] = max(0, min(9, estrellas_a_pedir))
            
        elif estrategia == "refuerzo":
            # Prioriza estadísticas donde la Uma ya tiene bonos altos
            estrellas_a_pedir = int((porcentaje_bono / 20.0) * 9)
            if estrellas_a_pedir > 0:
                necesidades_azules[id_factor] = min(9, estrellas_a_pedir)
                
    return necesidades_azules

def buscar_mejores_padres(grafo, necesidades, top_n=5):
    """Busca en el grafo respetando el límite de 9 estrellas por padre."""
    candidatos_evaluados = []
    
    # Recorremos los nodos cargados desde la API
    for cuenta_id, datos_uma in grafo.nodos_umas.items():
        puntaje_total = 0
        factores_cubiertos = {}
        factores_que_posee = grafo.obtener_conexiones(cuenta_id) 
        
        for rasgo_id, estrellas_req in necesidades.items():
            if rasgo_id in factores_que_posee:
                estrellas_uma = min(factores_que_posee[rasgo_id], 9)
                tope_para_este_padre = min(estrellas_req, 9)
                estrellas_aportadas = min(tope_para_este_padre, estrellas_uma)
                
                puntaje_total += estrellas_aportadas
                if estrellas_aportadas > 0:
                    factores_cubiertos[rasgo_id] = estrellas_aportadas
                
        if puntaje_total > 0:
            candidatos_evaluados.append({
                "cuenta_id": cuenta_id,
                "entrenador": datos_uma.get("entrenador", "Desconocido"),
                "puntaje": puntaje_total,
                "factores_utiles": factores_cubiertos
            })
            
    candidatos_evaluados.sort(key=lambda x: x["puntaje"], reverse=True)
    return candidatos_evaluados[:top_n]


# ==========================================
# ⚙️ 2. CARGA INICIAL DE DATOS (GRAFO Y CSV)
# ==========================================
print("Conectando con la API de Uma.moe... Por favor espera.")
try:
    # Llama a tu función del módulo original para construir el Grafo
    mi_grafo = construir_grafo_desde_api(max_paginas=10)
except Exception as e:
    print(f"Error al cargar el grafo desde la API: {e}")
    mi_grafo = None

print("Cargando base de datos CSV de personajes...")
try:
    # Cargamos usando tu clase Umamusume personalizada
    lista_csv = cargar_datos_csv("umamusume_personajes_completo (1).csv")
    db_personajes = {uma.nombre.lower(): uma for uma in lista_csv}
except Exception as e:
    print(f"Error al cargar CSV: {e}")
    db_personajes = {}


# ==========================================
# 🌐 3. RUTAS WEB DE FLASK
# ==========================================
@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular_herencia():
    datos = request.json
    uma_elegida = datos.get('uma')         # Ej: "Oguri Cap"
    carrera_elegida = datos.get('carrera') # Ej: "dirt" o "turf"
    
    if not uma_elegida:
        return jsonify({"error": "Por favor, introduce el nombre de una Umamusume"}), 400

    # 1. BUSCAR LOS DATOS REALES DE LA UMA ELEGIDA DESDE TU DICCIONARIO CSV
    personaje_data = db_personajes.get(uma_elegida.strip().lower())
    
    if personaje_data:
        bonos_uma = personaje_data.bonos_dict
    else:
        # Valores por defecto si la Uma no se encuentra escrita igual en el CSV
        bonos_uma = {"speed": 0, "stamina": 0, "power": 0, "guts": 0, "wit": 0}

    # 2. CALCULAR ESTRELLAS AZULES (Estadísticas base)
    prioridades_azules = calcular_prioridades_azules(bonos_uma, estrategia="parcheo")
    
    # 3. CALCULAR ESTRELLAS ROSAS (Aptitudes)
    prioridades_rosas = {}
    carrera_limpia = carrera_elegida.lower() if carrera_elegida else ""
    
    if "dirt" in carrera_limpia or "tierra" in carrera_limpia:
        estrellas_tierra_necesarias = calcular_estrellas_necesarias('C', 'A') 
        prioridades_rosas["120"] = estrellas_tierra_necesarias
    elif "turf" in carrera_limpia or "césped" in carrera_limpia:
        estrellas_cesped_necesarias = calcular_estrellas_necesarias('C', 'A') 
        prioridades_rosas["110"] = estrellas_cesped_necesarias
        
    # 4. FUSIONAR AMBAS PRIORIDADES Y BUSCAR EN EL GRAFO DE LA API
    prioridades_totales = {**prioridades_azules, **prioridades_rosas}
    
    if not mi_grafo:
        return jsonify({"error": "La base de datos de la API de Uma.moe no está disponible en este momento."}), 503
        
    mejores_umas = buscar_mejores_padres(mi_grafo, prioridades_totales)
    
    # 5. ENVIAR RESULTADOS AL FRONTEND
    resultados_top5 = []
    for i, candidato in enumerate(mejores_umas):
        resultados_top5.append({
            "posicion": i + 1,
            "id": candidato["cuenta_id"],
            "entrenador": candidato["entrenador"],
            "puntaje": candidato["puntaje"],
            "aportes": candidato["factores_utiles"] 
        })
        
    return jsonify({"resultados": resultados_top5})

if __name__ == '__main__':
    app.run(debug=True, port=5000)