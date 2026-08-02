import csv
import ast 

class Umamusume:
    def __init__(self, id_personaje, nombre, stat_bonus, aptitude_raw):
        self.id = id_personaje
        self.nombre = nombre
        self.stat_bonus_raw = stat_bonus
        
        # 1. Transformar Bonos (Estrellas Azules)
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
        
        # 2. Transformar Aptitudes (Estrellas Rosas) con nombres de atributos explícitos
        try:
            aptitude_list = ast.literal_eval(aptitude_raw)
        except (ValueError, SyntaxError):
            aptitude_list = []

        if isinstance(aptitude_list, list) and len(aptitude_list) >= 10:
            # Mapeo exacto esperado por app.py
            self.turf_aptitude = aptitude_list[0]
            self.dirt_aptitude = aptitude_list[1]
            self.sprint_aptitude = aptitude_list[2]
            self.mile_aptitude = aptitude_list[3]
            self.medium_aptitude = aptitude_list[4]
            self.long_aptitude = aptitude_list[5]
            self.front_runner_aptitude = aptitude_list[6]
            self.pace_chaser_aptitude = aptitude_list[7]
            self.late_surger_aptitude = aptitude_list[8]
            self.end_closer_aptitude = aptitude_list[9]
        else:
            # Valores por defecto 'G' si el CSV viene vacío o con errores
            self.turf_aptitude = 'G'
            self.dirt_aptitude = 'G'
            self.sprint_aptitude = 'G'
            self.mile_aptitude = 'G'
            self.medium_aptitude = 'G'
            self.long_aptitude = 'G'
            self.front_runner_aptitude = 'G'
            self.pace_chaser_aptitude = 'G'
            self.late_surger_aptitude = 'G'
            self.end_closer_aptitude = 'G'

    def __str__(self):
        return (f"Umamusume [ID: {self.id} | Nombre: {self.nombre}]\n"
                f"  ┣ Bonos Azules: {self.bonos_dict}\n")


# =====================================================================
# Función de carga del CSV adaptada para devolver un Diccionario
# =====================================================================
def cargar_personajes(ruta_archivo):
    diccionario_personajes = {}
    with open(ruta_archivo, mode='r', encoding='utf-8') as archivo:
        lector_csv = csv.DictReader(archivo)
        for fila in lector_csv:
            id_personaje = fila.get('itemData.char_id', 'Desconocido')
            nombre = fila.get('itemData.name_en') or fila.get('itemData.name_jp', 'Sin Nombre')
            stat_bonus = fila.get('itemData.stat_bonus', '[]')
            aptitude_raw = fila.get('itemData.aptitude', '[]')
            
            if id_personaje not in ['Desconocido', '']:
                # Guardamos usando el ID como clave principal
                diccionario_personajes[id_personaje] = Umamusume(id_personaje, nombre, stat_bonus, aptitude_raw)
                
    return diccionario_personajes
