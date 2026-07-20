import csv
import ast 

class Umamusume:
    def __init__(self, id_personaje, nombre, stat_bonus, aptitude_raw):
        self.id = id_personaje
        self.nombre = nombre
        self.stat_bonus_raw = stat_bonus
        
        # 1. Transformar Bonos (Estrellas Azules) para que app.py los pueda leer
        try:
            bonos_lista = ast.literal_eval(stat_bonus)
            if isinstance(bonos_lista, list) and len(bonos_lista) >= 5:
                self.bonos_dict = {
                    "speed": bonos_lista[0],
                    "stamina": bonos_lista[1],
                    "power": bonos_lista[2],
                    "guts": bonos_lista[3],
                    "wit": bonos_lista[4]
                }
            else:
                self.bonos_dict = {"speed": 0, "stamina": 0, "power": 0, "guts": 0, "wit": 0}
        except (ValueError, SyntaxError):
            self.bonos_dict = {"speed": 0, "stamina": 0, "power": 0, "guts": 0, "wit": 0}
        
        # 2. Transformar Aptitudes (Estrellas Rosas)
        try:
            aptitude_list = ast.literal_eval(aptitude_raw)
        except (ValueError, SyntaxError):
            aptitude_list = []

        if isinstance(aptitude_list, list) and len(aptitude_list) >= 10:
            self.surface = aptitude_list[0:2]    
            self.distance = aptitude_list[2:6]   
            self.strategy = aptitude_list[6:10]  
        else:
            self.surface = []
            self.distance = []
            self.strategy = []

    def __str__(self):
        return (f"Umamusume [ID: {self.id} | Nombre: {self.nombre}]\n"
                f"  ┣ Bonos Azules: {self.bonos_dict}\n")


# =====================================================================
# Función de carga del CSV
# =====================================================================
def cargar_datos_csv(ruta_archivo):
    lista_personajes = []
    with open(ruta_archivo, mode='r', encoding='utf-8') as archivo:
        lector_csv = csv.DictReader(archivo)
        for fila in lector_csv:
            id_personaje = fila.get('itemData.char_id', 'Desconocido')
            nombre = fila.get('itemData.name_en') or fila.get('itemData.name_jp', 'Sin Nombre')
            stat_bonus = fila.get('itemData.stat_bonus', '[]')
            aptitude_raw = fila.get('itemData.aptitude', '[]')
            
            if id_personaje not in ['Desconocido', '']:
                lista_personajes.append(Umamusume(id_personaje, nombre, stat_bonus, aptitude_raw))
    return lista_personajes
