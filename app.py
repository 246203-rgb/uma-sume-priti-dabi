from flask import Flask, render_template, request, jsonify
import json
import pandas as pd
import base_prototipo      # Tu motor de grafos conectado a la API de uma.moe
import datos_umamusumes    # Tu módulo que convierte el CSV de personajes en objetos

app = Flask(__name__)

# ==========================================
# 1. CARGA DE BASES DE DATOS (AL INICIAR)
# ==========================================

# Carga la lista de Umamusumes
try:
    LISTA_PERSONAJES = datos_umamusumes.cargar_personajes('umamusume_personajes_completo.csv') 
except Exception as e:
    print(f"Advertencia: No se pudo cargar la base de personajes: {e}")
    LISTA_PERSONAJES = {}

# Carga tu diccionario maestro desde el archivo JSON
try:
    with open('factores_ids.json', 'r', encoding='utf-8') as f:
        FACTORES_MAESTRO = json.load(f)
except FileNotFoundError:
    print("Error crítico: No se encontró factores_ids.json.")
    FACTORES_MAESTRO = {}

# ==========================================
# Construir el grafo global al iniciar
# ==========================================
print("Descargando base de datos y construyendo el grafo global. Por favor espera...")
GRAFO_GLOBAL = base_prototipo.construir_grafo_desde_api()


def extraer_opciones_menu(ruta_csv):
    """Lee tu archivo CSV de pistas y extrae listas limpias de valores únicos."""
    try:
        df = pd.read_csv(ruta_csv)
        df.columns = df.columns.str.strip()
        
        return {
            "racetracks": df["Racetrack"].dropna().unique().tolist(),
            "terrains": df["Terrain"].dropna().unique().tolist(),
            "directions": df["Direction"].dropna().unique().tolist(),
            "length_types": df["Length type"].dropna().unique().tolist(),
            "lengths": df["length"].dropna().astype(int).unique().tolist(),
        }
    except Exception as e:
        print(f"Error al leer el CSV de pistas: {e}")
        return {"racetracks": [], "terrains": [], "directions": [], "length_types": [], "lengths": []}


# ==========================================
# 2. LÓGICA DE INFERENCIA DE HERENCIA
# ==========================================

def calcular_estrellas_necesarias(rango_actual, rango_meta='A'):
    """Calcula cuántas estrellas totales de aptitud (Rosas) se necesitan mecánicamente."""
    valores_rango = {'G': 1, 'F': 2, 'E': 3, 'D': 4, 'C': 5, 'B': 6, 'A': 7, 'S': 8}
    
    rango_base = valores_rango.get(str(rango_actual).upper())
    rango_objetivo = valores_rango.get(str(rango_meta).upper())
    
    if not rango_base or not rango_objetivo: 
        return 0
        
    delta_r = rango_objetivo - rango_base
    if delta_r <= 0: 
        return 0
        
    if delta_r == 1: return 1
    elif delta_r == 2: return 4
    elif delta_r == 3: return 7
    elif delta_r >= 4: return 10
    return 0


def calcular_prioridades_azules(length_type, length, estrategia):
    """Calcula dinámicamente el peso de los stats base (Azules) según la pista y estrategia."""
    prioridades = {}
    
    # 1. Configuración base por distancia de la carrera
    if length_type == 'Long' or (length and length >= 2500):
        prioridades["20"] = 60  # Stamina como prioridad crítica
        prioridades["10"] = 40  # Speed
        prioridades["30"] = 20  # Power
    elif length_type == 'Medium' or (length and 2000 <= length < 2500):
        prioridades["10"] = 50  # Speed
        prioridades["20"] = 40  # Stamina
        prioridades["30"] = 30  # Power
    elif length_type == 'Mile' or (length and 1400 <= length < 2000):
        prioridades["10"] = 60  # Speed
        prioridades["30"] = 40  # Power
        prioridades["20"] = 20  # Stamina
    elif length_type == 'Sprint' or (length and length < 1400):
        prioridades["10"] = 70  # Máxima Speed
        prioridades["30"] = 40  # Power
        prioridades["50"] = 20  # Wisdom / Inteligencia

    # 2. Modificadores contextuales por Estrategia (Mecánica de posicionamiento)
    if estrategia == 'Front Runner':
        prioridades["10"] = prioridades.get("10", 0) + 15  # Arrancar y mantener la punta
        prioridades["50"] = prioridades.get("50", 0) + 10  # Sabiduría para no perder posición
    elif estrategia == 'Pace Chaser':
        prioridades["10"] = prioridades.get("10", 0) + 10
        prioridades["30"] = prioridades.get("30", 0) + 10
    elif estrategia == 'Late Surger':
        prioridades["30"] = prioridades.get("30", 0) + 15  # Fuerza para abrirse paso
    elif estrategia == 'End Closer':
        prioridades["30"] = prioridades.get("30", 0) + 25  # Power crítico para acelerar al final

    return prioridades


# ==========================================
# 3. RUTAS Y ENDPOINTS DEL SERVIDOR
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/opciones_carrera', methods=['GET'])
def obtener_opciones_carrera():
    """Ruta para que el Frontend cargue los menús desplegables dinámicamente."""
    opciones = extraer_opciones_menu("Racetrack Base date(Hoja1).csv")

    lista_desplegable_umas = []
    for u_id, u_obj in LISTA_PERSONAJES.items():
        lista_desplegable_umas.append({"id": u_id, "nombre": u_obj.nombre})
        
    opciones["umas"] = lista_desplegable_umas
    
    return jsonify(opciones)


@app.route('/calcular', methods=['POST'])
def calcular():
    datos_usuario = request.json
    uma_id = datos_usuario.get('uma_id')
    
    # Parámetros provenientes de la selección detallada de la pista
    racetrack = datos_usuario.get('racetrack')
    terrain = datos_usuario.get('terrain')          # "Turf" o "Dirt"
    direction = datos_usuario.get('direction')      # "Left" o "Right"
    length_type = datos_usuario.get('length_type')  # "Sprint", "Mile", etc.
    try:
        length = int(datos_usuario.get('length', 0))
    except (ValueError, TypeError):
        length = 0
        
    estrategia = datos_usuario.get('estrategia')    # "Front Runner", "End Closer", etc.

    # 1. Validar la existencia de la Umamusume seleccionada
    uma_elegida = LISTA_PERSONAJES.get(uma_id)
    if not uma_elegida:
        # CORRECCIÓN 1 APLICADA AQUÍ: Se restaura el error 404 original
        return jsonify({"error": "Umamusume no encontrada"}), 404

    prioridades_finales = {}

    # 2. ANÁLISIS DE BRECHAS ROSAS (APTITUDES)
    
    # A) Brecha de Terreno (Superficie)
    if terrain == 'Turf':
        aptitud_real = getattr(uma_elegida, 'turf_aptitude', 'G') 
        peso_estrellas = calcular_estrellas_necesarias(aptitud_real, 'A')
        if peso_estrellas > 0:
            prioridades_finales["110"] = peso_estrellas  # ID "110" de Turf en tu JSON
    elif terrain == 'Dirt':
        aptitud_real = getattr(uma_elegida, 'dirt_aptitude', 'G')
        peso_estrellas = calcular_estrellas_necesarias(aptitud_real, 'A')
        if peso_estrellas > 0:
            prioridades_finales["120"] = peso_estrellas  # ID "120" de Dirt en tu JSON

    # B) Brecha de Distancia (Mapeo exacto según tu JSON maestro)
    mapa_distancias = {
        'Sprint': ('sprint_aptitude', '310'),
        'Mile': ('mile_aptitude', '320'),
        'Medium': ('medium_aptitude', '330'),
        'Long': ('long_aptitude', '340')
    }
    if length_type in mapa_distancias:
        attr_name, json_id = mapa_distancias[length_type]
        aptitud_dist_real = getattr(uma_elegida, attr_name, 'G')
        peso_dist = calcular_estrellas_necesarias(aptitud_dist_real, 'A')
        if peso_dist > 0:
            prioridades_finales[json_id] = peso_dist

    # C) Brecha de Estrategia 
    mapa_estrategias = {
        'Front Runner': ('front_runner_aptitude', '210'),
        'Pace Chaser': ('pace_chaser_aptitude', '220'),
        'Late Surger': ('late_surger_aptitude', '230'),
        'End Closer': ('end_closer_aptitude', '240')
    }
    if estrategia in mapa_estrategias:
        attr_name, json_id = mapa_estrategias[estrategia]
        aptitud_est_real = getattr(uma_elegida, attr_name, 'G')
        peso_est = calcular_estrellas_necesarias(aptitud_est_real, 'A')
        if peso_est > 0:
            prioridades_finales[json_id] = peso_est

    # 3. ANÁLISIS DE BRECHAS AZULES (ESTADÍSTICAS BASE)
    prioridades_azules = calcular_prioridades_azules(length_type, length, estrategia)
    for stat_id, valor_prioridad in prioridades_azules.items():
        prioridades_finales[stat_id] = prioridades_finales.get(stat_id, 0) + valor_prioridad

    # 4. EJECUCIÓN DEL MOTOR DE GRAFOS COMPARTIDO
    try:
        # Usamos el grafo que ya se descargó al prender el servidor
        mejores_padres = GRAFO_GLOBAL.buscar_mejor_match(prioridades_finales)

        return jsonify({
            "mensaje": "Análisis de pista y herencia completado exitosamente",
            "condiciones_carrera": {
                "racetrack": racetrack,
                "terrain": terrain,
                "length_type": length_type,
                "length_m": length
            },
            "prioridades_calculadas": prioridades_finales,
            "resultados": mejores_padres,
            "factores_maestro": FACTORES_MAESTRO  # CORRECCIÓN 2 APLICADA AQUÍ
        })
    except Exception as e:
        return jsonify({"error": f"Fallo en la comunicación con el motor relacional: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)