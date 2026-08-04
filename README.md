# 🐴 Umamusume Inheritance Graph Optimizer

Un sistema avanzado de análisis y optimización de herencias para **Umamusume: Pretty Derby**, desarrollado en Python utilizando Flask, procesamiento de grafos y consumo de APIs externas.

---

## 🚀 Características Principales

- **Motor de Grafos Relacional (`herencia_uma.py`):** Construye un grafo en memoria relacionando cuentas de entrenadores con sus "sparks" (factores azules de estadísticas y factores rosas de aptitudes).
- **Sistema de Penalización Inteligente:** No solo premia las coincidencias deseadas, sino que penaliza la presencia de "estrellas basura" (rasgos no deseados) para asegurar líneas de herencia puras.
- **Análisis Contextual de Carreras:** Calcula dinámicamente las prioridades de estadísticas (azules) y la brecha de aptitudes (rosas) según el tipo de terreno (Turf/Dirt), distancia (Sprint, Mile, Medium, Long) y estrategia del corredor.
- **Integración Híbrida:** Combina datos locales (Gametora CSV, catálogos de pistas y diccionario maestro JSON) con datos en tiempo real de la API de `uma.moe`.
- **Interfaz Web Dinámica:** Servidor Flask con endpoints REST para alimentar menús desplegables y mostrar resultados analíticos en tiempo real.

---

## 📂 Estructura del Proyecto

```text
PROGRAMACION-II/
│
├── app.py                  # Servidor principal de Flask y rutas de la API
├── herencia_uma.py         # Motor de grafos y conexión con la API de uma.moe
├── datos_uma.py            # Lógica de carga y parseo de personajes (Gametora)
│
├── data/                   # Bases de datos locales
│   ├── data_gametora.csv   # Estadísticas y aptitudes base de las Umamusumes
│   ├── data_racetrack.csv  # Información de pistas y tipos de carrera
│   ├── data_umamoe.xlsx    # Respaldo de datos de herencia
│   └── factores_ids.json   # Diccionario maestro de IDs de factores/sparks
│
└── templates/
    └── index.html          # Interfaz gráfica de usuario
```

---

## 🛠️ Requisitos e Instalación

Asegúrate de tener instalado **Python 3.10 o superior**. 

1. Clona o descarga este repositorio en tu equipo.
2. Instala las dependencias necesarias ejecutando el siguiente comando en tu terminal:

```bash
pip install flask pandas requests openpyxl
```

---

## ⚙️ Ejecución de la Aplicación

Para poner en marcha el servidor de desarrollo local, ejecuta:

```bash
python app.py
```

Por defecto, la aplicación se iniciará en modo debug y podrás acceder a ella desde tu navegador web en:
👉 `http://127.0.0.1:5000`

> **Nota:** Al iniciar por primera vez, el sistema conectará con la API de `uma.moe` para construir el grafo global en memoria (por defecto descarga las primeras 10 páginas, ajustable en `app.py`).

---

## 🧩 Componentes del Sistema

1. **`app.py`**: Maneja el ciclo de vida de Flask, la carga inicial de bases de datos mediante caché de entorno (`WERKZEUG_RUN_MAIN`) para evitar descargas duplicadas, y los endpoints `/api/opciones_carrera` y `/calcular`.
2. **`herencia_uma.py`**: Implementa la clase `GrafoHerenciaUma` encargada de gestionar nodos (cuentas y rasgos) y aristas, aplicando el algoritmo de afinidad con puntuaciones y penalizaciones.
3. **`datos_uma.py`**: Contiene la clase `Umamusume` para estructurar los bonos de estadísticas y aptitudes desde los archivos CSV de Gametora.
