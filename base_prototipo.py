import pandas as pd
import requests
import json

class GrafoHerenciaUma:
    def __init__(self):
        # NODOS: Guardaremos la información de las entidades
        self.nodos_umas = {}       # id_cuenta -> {entrenador, victorias}
        self.nodos_rasgos = {}     # id_rasgo -> {nombre, categoria}
        
        # ARISTAS (Conexiones): uma_id -> {rasgo_id: total_estrellas}
        self.aristas = {}

    def agregar_nodo_rasgo(self, id_rasgo, nombre, categoria):
        """Crea un nodo para una característica específica en el grafo."""
        self.nodos_rasgos[id_rasgo] = {'nombre': nombre, 'categoria': categoria}

    def agregar_nodo_uma(self, id_cuenta, entrenador, victorias_g1):
        """Crea un nodo para una Uma de la base de datos."""
        self.nodos_umas[id_cuenta] = {
            'entrenador': entrenador,
            'victorias_g1': victorias_g1
        }
        # Preparamos el diccionario de conexiones para esta Uma
        if id_cuenta not in self.aristas:
            self.aristas[id_cuenta] = {}

    def conectar(self, id_cuenta, id_rasgo, estrellas):
        """
        Crea o refuerza una conexión (Arista) entre una Uma y un Rasgo.
        """
        if id_cuenta in self.aristas:
            # Si el rasgo ya existe en esta Uma (ej. por un abuelo), sumamos
            if id_rasgo in self.aristas[id_cuenta]:
                self.aristas[id_cuenta][id_rasgo] += estrellas
            else:
                self.aristas[id_cuenta][id_rasgo] = estrellas

    def obtener_conexiones(self, id_uma):
        """
        Devuelve un diccionario con los rasgos que posee una Uma y sus estrellas.
        Ejemplo: {'10': 3, '120': 2}
        """
        return self.aristas.get(id_uma, {})

def construir_grafo_desde_api(max_paginas=10):
    url = "https://uma.moe/api/v3/search"
    print("Descargando la base de datos de herencias de Uma.moe...")
    
    # 1. Autenticación con la API
    cabeceras = {
        "X-API-Key": "uma_k_HhskxZ5V7SiM7xhgMeD6BwjGEt2VddXG7sm0yccEQuVH24er"
    }
    
    # 2. Cargar nuestro diccionario maestro de factores
    try:
        with open('factores_ids.json', 'r', encoding='utf-8') as f:
            diccionario_rasgos = json.load(f)
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'factores_ids.json'. Asegúrate de crearlo en la misma carpeta.")
        return GrafoHerenciaUma()
        
    # 3. Inicializar el grafo
    grafo = GrafoHerenciaUma()
    
    # Registramos todos los rasgos posibles en el grafo primero
    for rasgo_id, rasgo_nombre in diccionario_rasgos.items():
        grafo.agregar_nodo_rasgo(rasgo_id, rasgo_nombre, "Factor Base")
        
    total_umas_descargadas = 0
    
    # 4. BUCLE DE PAGINACIÓN: Pedimos múltiples páginas a la API
    for pagina in range(1, max_paginas + 1):
        print(f"  -> Descargando página {pagina}...")
        
        # Le indicamos a la API qué página queremos usando el parámetro 'page'
        parametros = {"page": pagina}
        respuesta = requests.get(url, headers=cabeceras, params=parametros)
        
        if respuesta.status_code != 200:
            print(f"  -> Fin de la descarga. Código de la API: {respuesta.status_code}")
            break # Salimos del bucle si hay error o no hay más páginas
            
        data = respuesta.json()
        lista_herencias = data.get('items', [])
        
        if not lista_herencias:
            print("  -> No hay más Umas en la base de datos.")
            break # Salimos si la página está vacía
            
        # 5. Procesar la lista de Umas de ESTA página
        for item in lista_herencias:
            cuenta_id = item.get('account_id', 'Desconocido')
            entrenador = item.get('trainer_name', 'Sin Nombre')
            
            # Agregamos la Uma al grafo
            grafo.agregar_nodo_uma(cuenta_id, entrenador, 0)
            
            # Extraemos el diccionario interno de herencias
            herencia = item.get('inheritance', {})
            
            # Juntamos las estadísticas (blue) y las aptitudes (pink)
            sparks_combinados = herencia.get('blue_sparks', []) + herencia.get('pink_sparks', [])
            
            # Desempaquetar los códigos matemáticos
            for codigo_spark in sparks_combinados:
                rasgo_base_id = str(codigo_spark // 10) 
                estrellas = codigo_spark % 10
                
                if rasgo_base_id in diccionario_rasgos:
                    grafo.conectar(cuenta_id, rasgo_base_id, estrellas)
                    
        total_umas_descargadas += len(lista_herencias)

    print(f"Grafo construido exitosamente con {total_umas_descargadas} Umas descargadas e integradas.")
    return grafo

if __name__ == "__main__":
    archivo_bd = 'base_datos_uma_profesional.xlsx'
    
    try:
        mi_grafo = construir_grafo_desde_api()
        print("Grafo construido exitosamente.\n")
        
# Ejemplo de prueba con los IDs oficiales del juego
        prioridades_usuario = {
            "10": 10,   # Speed con peso máximo
            "120": 8    # Dirt con peso alto
        }
        
        print("Buscando los mejores caminos en el grafo...")
        mejores_umas = mi_grafo.buscar_mejor_match(prioridades_usuario)
        
        print("\nTOP 5 UMAS ENCONTRADAS:")
        print("-" * 50)
        top_n = min(5, len(mejores_umas))
        if top_n == 0:
            print("No se encontraron Umas que coincidan con las prioridades dadas.")
        else:
            for i in range(top_n):
                id_uma, puntaje = mejores_umas[i]
                info = mi_grafo.nodos_umas.get(id_uma, {'entrenador': 'Desconocido', 'victorias_g1': 0})
                print(f"#{i+1} | ID: {id_uma} | Entrenador: {info['entrenador']} | Victorias G1: {info['victorias_g1']}")
                print(f"Puntaje de Afinidad: {puntaje}\n")
            
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo_bd}'. Asegúrate de que esté en la misma carpeta.")
    
