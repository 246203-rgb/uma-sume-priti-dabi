import pandas as pd

class GrafoHerenciaUma:
    def __init__(self):
        # NODOS: Guardaremos la información de las entidades
        self.nodos_umas = {}       # id_cuenta -> {entrenador, victorias_g1}
        self.nodos_rasgos = {}     # id_rasgo -> {nombre, categoria}
        
        # ARISTAS (Conexiones): rasgo_id -> {uma_id: total_estrellas}
        # Esto es una Lista de Adyacencia ponderada.
        self.aristas = {}

    def agregar_nodo_rasgo(self, id_rasgo, nombre, categoria):
        """Crea un nodo para una característica específica en el grafo."""
        self.nodos_rasgos[id_rasgo] = {'nombre': nombre, 'categoria': categoria}
        if id_rasgo not in self.aristas:
            self.aristas[id_rasgo] = {}

    def agregar_nodo_uma(self, id_cuenta, entrenador, victorias_g1):
        """Crea un nodo para una Uma de la base de datos."""
        self.nodos_umas[id_cuenta] = {
            'entrenador': entrenador,
            'victorias_g1': victorias_g1
        }

    def conectar(self, id_cuenta, id_rasgo, estrellas):
        """
        Crea o refuerza una conexión (Arista) entre una Uma y un Rasgo.
        El peso de la arista son las estrellas. Si la conexión ya existe 
        (ej. por los abuelos), se suman las estrellas.
        """
        if id_rasgo in self.aristas:
            if id_cuenta in self.aristas[id_rasgo]:
                # Acumulamos las estrellas de toda la genealogía
                self.aristas[id_rasgo][id_cuenta] += estrellas
            else:
                self.aristas[id_rasgo][id_cuenta] = estrellas

    def buscar_mejor_match(self, prioridades):
        """
        Algoritmo de Búsqueda en el Grafo: 
        Viaja desde los Nodos de Rasgos solicitados hacia las Umas conectadas,
        multiplicando el peso de la conexión (estrellas) por la prioridad del usuario.
        """
        # Inicializamos el puntaje de todos los nodos Uma en 0
        puntajes = {id_cuenta: 0 for id_cuenta in self.nodos_umas}
        
        # Recorremos solo los nodos de las características que le importan al usuario
        for id_rasgo, prioridad_usuario in prioridades.items():
            if id_rasgo in self.aristas:
                # Vemos qué Umas están conectadas a esta característica
                for id_cuenta, estrellas_conexion in self.aristas[id_rasgo].items():
                    # Fórmula del Grafo: Puntaje = Peso de Arista * Peso de Nodo Usuario
                    puntaje_arista = estrellas_conexion * prioridad_usuario
                    puntajes[id_cuenta] += puntaje_arista
                    
        # Ordenar los nodos Uma por su puntaje de mayor a menor
        ranking = sorted(puntajes.items(), key=lambda x: x[1], reverse=True)
        return ranking

def construir_grafo_desde_csv(ruta_csv):
    grafo = GrafoHerenciaUma()
    
    # 1. Definir los Nodos de Rasgos (Agregamos más según necesites)
    grafo.agregar_nodo_rasgo(100, 'Speed', 'Azul')
    grafo.agregar_nodo_rasgo(200, 'Stamina', 'Azul')
    grafo.agregar_nodo_rasgo(300, 'Power', 'Azul')
    grafo.agregar_nodo_rasgo(10011, 'Dirt', 'Rosa')
    grafo.agregar_nodo_rasgo(10015, 'Long', 'Rosa')
    grafo.agregar_nodo_rasgo(30001, 'URA Scenario', 'Blanco')

    # Cargar datos según el formato del archivo
    if ruta_csv.lower().endswith('.xlsx') or ruta_csv.lower().endswith('.xls'):
        df = pd.read_excel(ruta_csv)
    else:
        df = pd.read_csv(ruta_csv, low_memory=False)
    df = df.rename(columns=lambda x: x.strip())
    
    columnas_factores = [
        'main_blue_factors', 'left_blue_factors', 'right_blue_factors',
        'main_pink_factors', 'left_pink_factors', 'right_pink_factors',
        'main_white_factors', 'left_white_factors', 'right_white_factors'
    ]
    
    # Nos aseguramos de tener la columna de IDs correcta (tomamos la primera)
    col_id = df.columns[0]
    
    print("Construyendo el grafo... (Creando nodos y trazando aristas)")
    
    for index, row in df.iterrows():
        id_cuenta = row[col_id]
        entrenador = row.get('Entrenador', 'Desconocido')
        victorias = row.get('Victorias G1', 0)
        
        # Crear el Nodo de la Uma
        grafo.agregar_nodo_uma(id_cuenta, entrenador, victorias)
        
        # Procesar genes para trazar las conexiones (Aristas)
        for col in columnas_factores:
            if col in row and not pd.isna(row[col]):
                factores_str = str(row[col]).replace('[', '').replace(']', '').replace('"', '').strip()
                if not factores_str:
                    continue
                    
                for item in factores_str.split(','):
                    item = item.strip()
                    if item.isdigit():
                        factor_num = int(item)
                        
                        # Tu lógica de códigos: Separar prefijo y estrellas (Max 3 estrellas)
                        if factor_num < 1000:
                            prefijo = (factor_num // 100) * 100 # ej: 203 -> 200
                        else:
                            prefijo = factor_num // 100         # ej: 1001401 -> 10014
                            
                        estrellas = factor_num % 100
                        # Forzamos límite de seguridad (max 3 por generación)
                        estrellas = min(3, estrellas) 
                        
                        # Conectar la Uma con el Rasgo en el grafo
                        grafo.conectar(id_cuenta, prefijo, estrellas)
                        
    return grafo

if __name__ == "__main__":
    archivo_bd = 'base_datos_uma_profesional.xlsx'
    
    try:
        # 1. Instanciamos y poblamos el Grafo
        mi_grafo = construir_grafo_desde_csv(archivo_bd)
        print("Grafo construido exitosamente.\n")
        
        # 2. El usuario hace una consulta (IDs de rasgos : Nivel de Prioridad)
        # Queremos Stamina (200), Pista de Tierra (10011) y Escenario URA (30001)
        prioridades_usuario = {
            200: 10,     # Prioridad altísima para Stamina
            10011: 8,    # Prioridad alta para Dirt
            30001: 5     # Prioridad media para URA
        }
        
        print("Buscando los mejores caminos en el grafo...")
        mejores_umas = mi_grafo.buscar_mejor_match(prioridades_usuario)
        
        # 3. Mostrar el Top 5
        print("\nTOP 5 UMAS ENCONTRADAS:")
        print("-" * 50)
        for i in range(5):
            id_uma, puntaje = mejores_umas[i]
            info = mi_grafo.nodos_umas[id_uma]
            print(f"#{i+1} | ID: {id_uma} | Entrenador: {info['entrenador']} | Victorias G1: {info['victorias_g1']}")
            print(f"Puntaje de Afinidad: {puntaje}\n")
            
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo_bd}'. Asegúrate de que esté en la misma carpeta.")
