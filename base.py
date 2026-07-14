import csv
import ast 

class Umamusume:
    def __init__(self, id_personaje, nombre, stat_bonus, aptitude_raw):
        """
        Clase que representa a un personaje de Umamusume con sus aptitudes separadas.
        """
        self.id = id_personaje
        self.nombre = nombre
        self.stat_bonus = stat_bonus
        
        # 1. Convertimos el string del CSV en una lista real de Python
        try:
            # Convierte texto como "['A', 'B', 'C', ...]" en una lista real
            aptitude_list = ast.literal_eval(aptitude_raw)
        except (ValueError, SyntaxError):
            # Si la columna está vacía o tiene un formato incorrecto, creamos una lista vacía
            aptitude_list = []

        # 2. Separamos la lista en las 3 categorías requeridas
        # Aseguramos que sea una lista y tenga al menos 10 elementos para evitar errores
        if isinstance(aptitude_list, list) and len(aptitude_list) >= 10:
            self.surface = aptitude_list[0:2]    # Los 2 primeros elementos (índices 0 y 1)
            self.distance = aptitude_list[2:6]   # Los 4 siguientes (índices 2, 3, 4 y 5)
            self.strategy = aptitude_list[6:10]  # Los 4 siguientes (índices 6, 7, 8 y 9)
        else:
            # Valores por defecto si la data está incompleta
            self.surface = []
            self.distance = []
            self.strategy = []

    def __str__(self):
        # Actualizamos la forma en la que se imprime para ver los atributos separados
        return (f"Umamusume [ID: {self.id} | Nombre: {self.nombre}]\n"
                f"  ┣ Stat Bonus: {self.stat_bonus}\n"
                f"  ┣ Surface:  {self.surface}\n"
                f"  ┣ Distance: {self.distance}\n"
                f"  ┗ Strategy: {self.strategy}\n")


# =====================================================================
# Función de carga del CSV (Sin muchos cambios)
# =====================================================================

def cargar_datos_csv(ruta_archivo):
    lista_personajes = []
    
    with open(ruta_archivo, mode='r', encoding='utf-8') as archivo:
        lector_csv = csv.DictReader(archivo)
        
        for fila in lector_csv:
            id_personaje = fila.get('itemData.char_id', 'Desconocido')
            
            nombre = fila.get('itemData.name_en')
            if not nombre:
                nombre = fila.get('itemData.name_jp', 'Sin Nombre')
                
            stat_bonus = fila.get('itemData.stat_bonus', 'Sin datos')
            
            # Obtenemos la aptitud en crudo (como texto)
            aptitude_raw = fila.get('itemData.aptitude', '[]')
            
            if id_personaje != 'Desconocido' and id_personaje != '':
                nuevo_personaje = Umamusume(id_personaje, nombre, stat_bonus, aptitude_raw)
                lista_personajes.append(nuevo_personaje)
                
    return lista_personajes

# --- Ejecución del código ---
if __name__ == "__main__":
    ruta = "umamusume_personajes_completo (1).csv"
    
    try:
        personajes = cargar_datos_csv(ruta)
        print(f"¡Se han cargado {len(personajes)} personajes exitosamente!\n")
        
        print("Mostrando los primeros 259 personajes con las aptitudes separadas:")
        print("=" * 60)
        for personaje in personajes[:259]:
            print(personaje)
            
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta}'.")
