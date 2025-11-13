import tkinter as tk
from tkinter import ttk, messagebox
import random
import math

class SimuladorPlatano:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Monitoreo - Cultivo de Plátano")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2d5016')
        
        # Parámetros del cultivo de plátano
        self.humedad_ideal_min = 65  # % humedad ideal mínima
        self.humedad_ideal_max = 80  # % humedad ideal máxima
        
        # Configuración de la parcela
        self.num_areas = 12
        self.sensores_por_area = 2
        self.total_sensores = self.num_areas * self.sensores_por_area
        
        # Estado del cultivo
        self.platano_sembrado = False
        self.etapa_crecimiento = 0  # 0: No sembrado, 1: Germinación, 2: Crecimiento, 3: Maduración
        self.dias_desde_siembra = 0
        
        # Datos de simulación
        self.meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                     'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        # Patrones climáticos por mes (promedio)
        self.patrones_clima = {
            'Ene': {'lluvia': 40, 'temperatura': 28, 'sequia': 20},
            'Feb': {'lluvia': 30, 'temperatura': 29, 'sequia': 30},
            'Mar': {'lluvia': 50, 'temperatura': 30, 'sequia': 15},
            'Abr': {'lluvia': 80, 'temperatura': 29, 'sequia': 5},
            'May': {'lluvia': 120, 'temperatura': 28, 'sequia': 2},
            'Jun': {'lluvia': 100, 'temperatura': 27, 'sequia': 5},
            'Jul': {'lluvia': 80, 'temperatura': 27, 'sequia': 10},
            'Ago': {'lluvia': 90, 'temperatura': 28, 'sequia': 8},
            'Sep': {'lluvia': 110, 'temperatura': 28, 'sequia': 4},
            'Oct': {'lluvia': 130, 'temperatura': 27, 'sequia': 3},
            'Nov': {'lluvia': 90, 'temperatura': 27, 'sequia': 6},
            'Dic': {'lluvia': 60, 'temperatura': 27, 'sequia': 12}
        }
        
        # Estado inicial
        self.mes_actual = 0
        self.datos_sensores = {}
        self.historial_humedad = []
        self.historial_riego = []
        self.alertas = []
        
        self.inicializar_datos()
        self.crear_interfaz()
        self.actualizar_simulacion()
        
    def inicializar_datos(self):
        """Inicializa los datos de los sensores"""
        for i in range(self.total_sensores):
            self.datos_sensores[i] = {
                'humedad': random.randint(60, 75),
                'area': i // self.sensores_por_area,
                'estado': 'Normal',
                'lado': 'izquierdo' if (i // self.sensores_por_area) < 6 else 'derecho'
            }
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2d5016')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título principal
        titulo_frame = tk.Frame(main_frame, bg='#4a7c1f', height=80)
        titulo_frame.pack(fill=tk.X, pady=(0,10))
        titulo_frame.pack_propagate(False)
        
        tk.Label(titulo_frame, text="🌴 SISTEMA DE MONITOREO - CULTIVO DE PLÁTANO 🌴", 
                font=('Arial', 20, 'bold'), bg='#4a7c1f', fg='white').pack(expand=True)
        
        # Frame para controles y visualización
        content_frame = tk.Frame(main_frame, bg='#2d5016')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo - Vista de la parcela
        left_panel = tk.Frame(content_frame, bg='#3a6519', relief=tk.RAISED, bd=3)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        # Panel derecho - Gráficos y controles
        right_panel = tk.Frame(content_frame, bg='#3a6519', relief=tk.RAISED, bd=3)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        
        self.crear_vista_parcela(left_panel)
        self.crear_controles_derecha(right_panel)
    
    def crear_vista_parcela(self, parent):
        """Crea la vista visual de la parcela con sensores"""
        # Frame principal de la parcela
        parcela_frame = tk.Frame(parent, bg='#3a6519')
        parcela_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(parcela_frame, text="🏞️ VISTA DE LA PARCELA", 
                font=('Arial', 16, 'bold'), bg='#3a6519', fg='white').pack(pady=10)
        
        # Frame con scroll para la parcela
        parcela_container = tk.Frame(parcela_frame, bg='#3a6519')
        parcela_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar para la parcela
        canvas_parcela = tk.Canvas(parcela_container, bg='#3a6519', highlightthickness=0)
        scrollbar_parcela = tk.Scrollbar(parcela_container, orient="vertical", command=canvas_parcela.yview)
        
        self.scrollable_parcela = tk.Frame(canvas_parcela, bg='#3a6519')
        
        self.scrollable_parcela.bind(
            "<Configure>",
            lambda e: canvas_parcela.configure(scrollregion=canvas_parcela.bbox("all"))
        )
        
        canvas_parcela.create_window((0, 0), window=self.scrollable_parcela, anchor="nw")
        canvas_parcela.configure(yscrollcommand=scrollbar_parcela.set)
        
        canvas_parcela.pack(side="left", fill="both", expand=True)
        scrollbar_parcela.pack(side="right", fill="y")
        
        # Canvas para dibujar la parcela dentro del frame scrollable
        self.parcela_canvas = tk.Canvas(self.scrollable_parcela, bg='#5a8c2f', highlightthickness=0,
                                       width=600, height=600)
        self.parcela_canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame para controles de riego y siembra
        controles_frame = tk.Frame(self.scrollable_parcela, bg='#3a6519')
        controles_frame.pack(fill=tk.X, pady=10)
        
        # Pileta de agua
        pileta_frame = tk.LabelFrame(controles_frame, text="💧 PILETA DE AGUA", 
                                   font=('Arial', 12, 'bold'), bg='#4a7c1f', fg='white',
                                   padx=10, pady=10)
        pileta_frame.pack(fill=tk.X, pady=5)
        
        # Botones de control de riego
        botones_frame = tk.Frame(pileta_frame, bg='#4a7c1f')
        botones_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(botones_frame, text="🚿 REGAR LADO IZQUIERDO", 
                 command=lambda: self.regar_lado('izquierdo'),
                 bg='#2196f3', fg='white', font=('Arial', 11, 'bold'),
                 relief=tk.RAISED, bd=3, cursor='hand2', width=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(botones_frame, text="🚿 REGAR LADO DERECHO", 
                 command=lambda: self.regar_lado('derecho'),
                 bg='#2196f3', fg='white', font=('Arial', 11, 'bold'),
                 relief=tk.RAISED, bd=3, cursor='hand2', width=20).pack(side=tk.RIGHT, padx=10)
        
        # Botón para sembrar plátano
        siembra_frame = tk.Frame(pileta_frame, bg='#4a7c1f')
        siembra_frame.pack(fill=tk.X, pady=5)
        
        self.btn_sembrar = tk.Button(siembra_frame, text="🌱 SEMBRAR PLÁTANO", 
                                    command=self.sembrar_platano,
                                    bg='#4caf50', fg='white', font=('Arial', 12, 'bold'),
                                    relief=tk.RAISED, bd=3, cursor='hand2', width=25)
        self.btn_sembrar.pack(pady=5)
        
        # Indicador de nivel de agua y estado del cultivo
        info_frame = tk.Frame(pileta_frame, bg='#4a7c1f')
        info_frame.pack(fill=tk.X, pady=5)
        
        self.nivel_agua = 80  # Nivel inicial de agua (%)
        self.nivel_label = tk.Label(info_frame, text=f"Nivel de agua: {self.nivel_agua}%", 
                                   font=('Arial', 11, 'bold'), bg='#4a7c1f', fg='#00ffff')
        self.nivel_label.pack(side=tk.LEFT, padx=20)
        
        self.estado_cultivo_label = tk.Label(info_frame, text="Estado: No sembrado", 
                                            font=('Arial', 11, 'bold'), bg='#4a7c1f', fg='#ffeb3b')
        self.estado_cultivo_label.pack(side=tk.RIGHT, padx=20)
        
        # Botón para recargar agua
        recarga_frame = tk.Frame(pileta_frame, bg='#4a7c1f')
        recarga_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(recarga_frame, text="💦 RECARGAR AGUA", 
                 command=self.recargar_agua,
                 bg='#00bcd4', fg='white', font=('Arial', 11, 'bold'),
                 relief=tk.RAISED, bd=3, cursor='hand2', width=20).pack(pady=5)
        
        # Dibujar la parcela inicial
        self.dibujar_parcela()
    
    def dibujar_parcela(self):
        """Dibuja la representación visual de la parcela"""
        self.parcela_canvas.delete("all")
        
        canvas_width = 600
        canvas_height = 600
        
        # Dibujar el canal central
        canal_x = canvas_width // 2
        canal_ancho = 30
        self.parcela_canvas.create_rectangle(canal_x - canal_ancho//2, 50,
                                           canal_x + canal_ancho//2, canvas_height - 50,
                                           fill='#1e88e5', outline='#0d47a1', width=2)
        
        # Dibujar texto "CANAL"
        self.parcela_canvas.create_text(canal_x, canvas_height // 2, 
                                       text="CANAL", font=('Arial', 12, 'bold'),
                                       fill='white', angle=90)
        
        # Dibujar sensores del lado izquierdo
        lado_izq_x = canal_x - canal_ancho//2 - 60
        self.dibujar_sensores_lado(lado_izq_x, 'izquierdo')
        
        # Dibujar sensores del lado derecho
        lado_der_x = canal_x + canal_ancho//2 + 60
        self.dibujar_sensores_lado(lado_der_x, 'derecho')
        
        # Dibujar pileta de agua
        self.dibujar_pileta_agua()
        
        # Dibujar plátanos si están sembrados
        if self.platano_sembrado:
            self.dibujar_platanos()
    
    def dibujar_sensores_lado(self, x_base, lado):
        """Dibuja los sensores de un lado específico"""
        canvas_height = 600
        
        # Calcular qué sensores pertenecen a este lado
        sensores_lado = []
        for sensor_id, data in self.datos_sensores.items():
            if data['lado'] == lado:
                sensores_lado.append((sensor_id, data))
        
        # Ordenar sensores por área
        sensores_lado.sort(key=lambda x: x[1]['area'])
        
        # Dibujar 6 sensores en este lado (2 por área × 3 áreas en vertical)
        espaciado_y = (canvas_height - 100) // 6
        radio_sensor = 15
        
        for i, (sensor_id, data) in enumerate(sensores_lado[:6]):  # Solo primeros 6 del lado
            y = 80 + i * espaciado_y
            
            # Color según estado de humedad
            if data['humedad'] < self.humedad_ideal_min:
                color = '#ff9800'  # Naranja - baja humedad
            elif data['humedad'] > self.humedad_ideal_max:
                color = '#f44336'  # Rojo - alta humedad
            else:
                color = '#4caf50'  # Verde - ideal
            
            # Dibujar sensor
            self.parcela_canvas.create_oval(x_base - radio_sensor, y - radio_sensor,
                                           x_base + radio_sensor, y + radio_sensor,
                                           fill=color, outline='white', width=2)
            
            # Etiqueta del sensor
            self.parcela_canvas.create_text(x_base, y, 
                                           text=str(sensor_id + 1),
                                           font=('Arial', 8, 'bold'), fill='white')
            
            # Indicador de humedad
            humedad_text = f"{data['humedad']}%"
            self.parcela_canvas.create_text(x_base, y + radio_sensor + 10,
                                           text=humedad_text,
                                           font=('Arial', 7), fill='white')
            
            # Línea conectando al canal (simulando tubería de riego)
            canal_x = 300
            if lado == 'izquierdo':
                self.parcela_canvas.create_line(x_base + radio_sensor, y,
                                               canal_x - 15, y,
                                               fill='#888888', width=1, dash=(2, 2))
            else:
                self.parcela_canvas.create_line(x_base - radio_sensor, y,
                                               canal_x + 15, y,
                                               fill='#888888', width=1, dash=(2, 2))
    
    def dibujar_pileta_agua(self):
        """Dibuja la pileta de agua"""
        canvas_width = 600
        canvas_height = 600
        
        # Posición de la pileta (abajo a la derecha)
        pileta_x = canvas_width - 100
        pileta_y = canvas_height - 80
        pileta_ancho = 80
        pileta_alto = 60
        
        # Dibujar pileta
        self.parcela_canvas.create_rectangle(pileta_x, pileta_y,
                                           pileta_x + pileta_ancho, pileta_y + pileta_alto,
                                           fill='#1e88e5', outline='#0d47a1', width=3)
        
        # Dibujar nivel de agua
        nivel_alto = (self.nivel_agua / 100) * pileta_alto
        self.parcela_canvas.create_rectangle(pileta_x, pileta_y + pileta_alto - nivel_alto,
                                           pileta_x + pileta_ancho, pileta_y + pileta_alto,
                                           fill='#29b6f6', outline='')
        
        # Etiqueta de la pileta
        self.parcela_canvas.create_text(pileta_x + pileta_ancho//2, pileta_y - 10,
                                       text="PILETA", font=('Arial', 9, 'bold'),
                                       fill='white')
        
        # Tuberías de conexión a los lados
        canal_x = 300
        self.parcela_canvas.create_line(pileta_x, pileta_y + pileta_alto//2,
                                       canal_x, pileta_y + pileta_alto//2,
                                       fill='#888888', width=2)
    
    def dibujar_platanos(self):
        """Dibuja los plátanos en la parcela"""
        canvas_width = 600
        canvas_height = 600
        
        canal_x = canvas_width // 2
        
        # Dibujar plátanos en ambos lados
        for lado, offset in [('izquierdo', -80), ('derecho', 80)]:
            x_base = canal_x + offset
            
            # Dibujar 3 plantas de plátano por lado
            for i in range(3):
                y = 120 + i * 120
                
                # Tamaño según etapa de crecimiento
                if self.etapa_crecimiento == 1:  # Germinación
                    tamaño = 15
                    color = '#8bc34a'
                    emoji = "🌱"
                elif self.etapa_crecimiento == 2:  # Crecimiento
                    tamaño = 25
                    color = '#4caf50'
                    emoji = "🌿"
                else:  # Maduración
                    tamaño = 35
                    color = '#388e3c'
                    emoji = "🍌"
                
                # Dibujar planta
                self.parcela_canvas.create_oval(x_base - tamaño, y - tamaño,
                                               x_base + tamaño, y + tamaño,
                                               fill=color, outline='#2e7d32', width=2)
                
                # Dibujar emoji de plátano
                self.parcela_canvas.create_text(x_base, y, text=emoji,
                                               font=('Arial', 12), fill='#795548')
    
    def crear_controles_derecha(self, parent):
        """Crea los controles del panel derecho"""
        # Notebook para organizar contenido
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Estilo para el notebook
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
        
        # Pestaña 1: Información y controles
        info_tab = tk.Frame(notebook, bg='#2d5016')
        notebook.add(info_tab, text='📋 Información')
        
        # Pestaña 2: Gráficos
        graficos_tab = tk.Frame(notebook, bg='#2d5016')
        notebook.add(graficos_tab, text='📊 Gráficos')
        
        # Pestaña 3: Estadísticas Detalladas
        stats_tab = tk.Frame(notebook, bg='#2d5016')
        notebook.add(stats_tab, text='📈 Estadísticas')
        
        self.crear_pestana_informacion(info_tab)
        self.crear_pestana_graficos(graficos_tab)
        self.crear_pestana_estadisticas(stats_tab)
    
    def crear_pestana_informacion(self, parent):
        """Crea la pestaña de información con scroll"""
        # Frame con scroll
        canvas = tk.Canvas(parent, bg='#2d5016', highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2d5016')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Información del mes actual
        info_frame = tk.LabelFrame(scrollable_frame, text="📅 INFORMACIÓN DEL MES ACTUAL", 
                                  font=('Arial', 12, 'bold'), bg='#4a7c1f', fg='white',
                                  padx=15, pady=15)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.mes_label = tk.Label(info_frame, text="Mes: Enero", font=('Arial', 14, 'bold'),
                                 bg='#4a7c1f', fg='yellow')
        self.mes_label.pack(anchor=tk.W)
        
        self.clima_label = tk.Label(info_frame, text="Lluvia: 40mm | Temp: 28°C | Sequía: 20%",
                                   font=('Arial', 11), bg='#4a7c1f', fg='white')
        self.clima_label.pack(anchor=tk.W)
        
        # Información del cultivo
        self.cultivo_frame = tk.LabelFrame(scrollable_frame, text="🌱 ESTADO DEL CULTIVO", 
                                        font=('Arial', 12, 'bold'), bg='#4a7c1f', fg='white',
                                        padx=15, pady=15)
        self.cultivo_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.etapa_label = tk.Label(self.cultivo_frame, text="Estado: No sembrado", 
                                   font=('Arial', 11, 'bold'), bg='#4a7c1f', fg='#ffeb3b')
        self.etapa_label.pack(anchor=tk.W)
        
        self.dias_label = tk.Label(self.cultivo_frame, text="", 
                                  font=('Arial', 11), bg='#4a7c1f', fg='white')
        self.dias_label.pack(anchor=tk.W)
        
        self.proxima_label = tk.Label(self.cultivo_frame, text="", 
                                     font=('Arial', 11), bg='#4a7c1f', fg='white')
        self.proxima_label.pack(anchor=tk.W)
        
        # Controles de simulación
        control_frame = tk.LabelFrame(scrollable_frame, text="🎮 CONTROLES DE SIMULACIÓN", 
                                     font=('Arial', 12, 'bold'), bg='#4a7c1f', fg='white',
                                     padx=15, pady=15)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(control_frame, text="⏭️ AVANZAR MES", command=self.avanzar_mes,
                 bg='#ff6b35', fg='white', font=('Arial', 12, 'bold'),
                 relief=tk.RAISED, bd=3, cursor='hand2', width=20).pack(pady=5)
        
        tk.Button(control_frame, text="🔄 REINICIAR SIMULACIÓN", command=self.reiniciar_simulacion,
                 bg='#2196f3', fg='white', font=('Arial', 12, 'bold'),
                 relief=tk.RAISED, bd=3, cursor='hand2', width=20).pack(pady=5)
        
        # Estado de sensores
        sensores_frame = tk.LabelFrame(scrollable_frame, text="🔍 ESTADO DE SENSORES", 
                                      font=('Arial', 12, 'bold'), bg='#4a7c1f', fg='white',
                                      padx=15, pady=15)
        sensores_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Crear grid de sensores
        for area in range(self.num_areas):
            area_frame = tk.Frame(sensores_frame, bg='#4a7c1f')
            area_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(area_frame, text=f"Área {area+1}:", font=('Arial', 9, 'bold'),
                    bg='#4a7c1f', fg='white', width=8).pack(side=tk.LEFT)
            
            for sensor_idx in range(self.sensores_por_area):
                sensor_id = area * self.sensores_por_area + sensor_idx
                sensor_data = self.datos_sensores[sensor_id]
                
                # Color según estado
                if sensor_data['humedad'] < self.humedad_ideal_min:
                    color = '#ff9800'
                elif sensor_data['humedad'] > self.humedad_ideal_max:
                    color = '#f44336'
                else:
                    color = '#4caf50'
                
                sensor_text = f"S{sensor_id+1}: {sensor_data['humedad']}%"
                lbl = tk.Label(area_frame, text=sensor_text, font=('Arial', 8),
                             bg=color, fg='white', width=12)
                lbl.pack(side=tk.LEFT, padx=2)
        
        # Leyenda
        leyenda_frame = tk.Frame(sensores_frame, bg='#4a7c1f')
        leyenda_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(leyenda_frame, text="Leyenda:", font=('Arial', 9, 'bold'),
                bg='#4a7c1f', fg='white').pack(side=tk.LEFT)
        
        for color, texto in [('#4caf50', 'Ideal'), ('#ff9800', 'Baja'), ('#f44336', 'Alta')]:
            tk.Label(leyenda_frame, text="■", font=('Arial', 12),
                    bg=color, fg=color).pack(side=tk.LEFT, padx=2)
            tk.Label(leyenda_frame, text=texto, font=('Arial', 8),
                    bg='#4a7c1f', fg='white').pack(side=tk.LEFT, padx=5)
    
    def crear_pestana_graficos(self, parent):
        """Crea la pestaña de gráficos con scroll"""
        # Frame con scroll para gráficos
        canvas_graficos = tk.Canvas(parent, bg='#2d5016', highlightthickness=0)
        scrollbar_graficos = tk.Scrollbar(parent, orient="vertical", command=canvas_graficos.yview)
        scrollable_graficos = tk.Frame(canvas_graficos, bg='#2d5016')
        
        scrollable_graficos.bind(
            "<Configure>",
            lambda e: canvas_graficos.configure(scrollregion=canvas_graficos.bbox("all"))
        )
        
        canvas_graficos.create_window((0, 0), window=scrollable_graficos, anchor="nw")
        canvas_graficos.configure(yscrollcommand=scrollbar_graficos.set)
        
        canvas_graficos.pack(side="left", fill="both", expand=True)
        scrollbar_graficos.pack(side="right", fill="y")
        
        # Notebook para gráficos dentro del frame scrollable
        graficos_notebook = ttk.Notebook(scrollable_graficos)
        graficos_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de gráfico de barras
        bar_frame = tk.Frame(graficos_notebook, bg='#2d5016')
        graficos_notebook.add(bar_frame, text='📊 Barras')
        
        # Pestaña de gráfico de pastel
        pie_frame = tk.Frame(graficos_notebook, bg='#2d5016')
        graficos_notebook.add(pie_frame, text='🥧 Pastel')
        
        # Pestaña de predicción
        pred_frame = tk.Frame(graficos_notebook, bg='#2d5016')
        graficos_notebook.add(pred_frame, text='🔮 Predicción')
        
        # Canvas para gráficos con tamaño fijo
        self.bar_canvas = tk.Canvas(bar_frame, bg='#2d5016', highlightthickness=0, width=650, height=500)
        self.bar_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.pie_canvas = tk.Canvas(pie_frame, bg='#2d5016', highlightthickness=0, width=650, height=500)
        self.pie_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.pred_canvas = tk.Canvas(pred_frame, bg='#2d5016', highlightthickness=0, width=650, height=500)
        self.pred_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def crear_pestana_estadisticas(self, parent):
        """Crea la pestaña de estadísticas detalladas con scroll"""
        # Frame con scroll para estadísticas
        canvas_stats = tk.Canvas(parent, bg='#2d5016', highlightthickness=0)
        scrollbar_stats = tk.Scrollbar(parent, orient="vertical", command=canvas_stats.yview)
        scrollable_stats = tk.Frame(canvas_stats, bg='#2d5016')
        
        scrollable_stats.bind(
            "<Configure>",
            lambda e: canvas_stats.configure(scrollregion=canvas_stats.bbox("all"))
        )
        
        canvas_stats.create_window((0, 0), window=scrollable_stats, anchor="nw")
        canvas_stats.configure(yscrollcommand=scrollbar_stats.set)
        
        canvas_stats.pack(side="left", fill="both", expand=True)
        scrollbar_stats.pack(side="right", fill="y")
        
        # Canvas para estadísticas
        self.stats_canvas = tk.Canvas(scrollable_stats, bg='#2d5016', highlightthickness=0, width=650, height=800)
        self.stats_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def sembrar_platano(self):
        """Acción de sembrar plátano"""
        if self.platano_sembrado:
            messagebox.showinfo("Cultivo Existente", "¡Ya hay plátanos sembrados en la parcela!")
            return
        
        self.platano_sembrado = True
        self.etapa_crecimiento = 1  # Comienza en germinación
        self.dias_desde_siembra = 0
        self.btn_sembrar.config(text="🌱 PLÁTANO SEMBRADO", state=tk.DISABLED, bg='#795548')
        
        # ACTUALIZAR EL ESTADO A "Plátanos sembrados" - CORRECCIÓN APLICADA
        self.estado_cultivo_label.config(text="Estado: Plátanos sembrados")
        self.actualizar_info_cultivo()
        
        self.dibujar_parcela()
        messagebox.showinfo("Siembra Exitosa", 
                          "✅ ¡Plátanos sembrados correctamente!\n\n"
                          "🌱 Etapa: Germinación\n"
                          "⏰ Próxima etapa en: 30 días\n"
                          "💧 Mantén la humedad entre 65%-80%")
    
    def recargar_agua(self):
        """Recarga la pileta de agua"""
        self.nivel_agua = 100
        self.nivel_label.config(text=f"Nivel de agua: {self.nivel_agua}%")
        self.dibujar_parcela()
        messagebox.showinfo("Agua Recargada", "✅ La pileta ha sido recargada al 100%")
    
    def regar_lado(self, lado):
        """Riega un lado específico de la parcela"""
        if self.nivel_agua < 10:
            messagebox.showwarning("Agua Insuficiente", 
                                 "¡La pileta está casi vacía! Recargue agua primero.")
            return
        
        # Reducir nivel de agua
        self.nivel_agua = max(0, self.nivel_agua - 15)
        self.nivel_label.config(text=f"Nivel de agua: {self.nivel_agua}%")
        
        # Aumentar humedad en los sensores del lado seleccionado
        sensores_regados = 0
        for sensor_id, data in self.datos_sensores.items():
            if data['lado'] == lado:
                # Aumentar humedad entre 15-25%
                aumento = random.uniform(15, 25)
                nueva_humedad = min(95, data['humedad'] + aumento)
                self.datos_sensores[sensor_id]['humedad'] = round(nueva_humedad, 1)
                sensores_regados += 1
        
        # Actualizar visualización
        self.dibujar_parcela()
        self.actualizar_graficos()
        self.actualizar_estadisticas()
        
        messagebox.showinfo("Riego Completado", 
                          f"✅ Lado {lado.upper()} regado correctamente\n"
                          f"📊 {sensores_regados} sensores actualizados\n"
                          f"💧 Nivel de agua restante: {self.nivel_agua}%")
    
    def avanzar_mes(self):
        """Avanza al siguiente mes en la simulación"""
        self.mes_actual = (self.mes_actual + 1) % 12
        
        # Recargar un poco de agua cada mes (lluvia natural)
        self.nivel_agua = min(100, self.nivel_agua + 10)
        self.nivel_label.config(text=f"Nivel de agua: {self.nivel_agua}%")
        
        # Avanzar crecimiento del plátano
        if self.platano_sembrado:
            self.dias_desde_siembra += 30  # 30 días por mes
            
            # Actualizar etapa de crecimiento
            if self.dias_desde_siembra >= 90:
                self.etapa_crecimiento = 3  # Maduración
            elif self.dias_desde_siembra >= 60:
                self.etapa_crecimiento = 2  # Crecimiento
        
        self.actualizar_simulacion()
    
    def reiniciar_simulacion(self):
        """Reinicia la simulación a su estado inicial"""
        self.mes_actual = 0
        self.historial_humedad = []
        self.historial_riego = []
        self.alertas = []
        self.nivel_agua = 80
        self.nivel_label.config(text=f"Nivel de agua: {self.nivel_agua}%")
        self.platano_sembrado = False
        self.etapa_crecimiento = 0
        self.dias_desde_siembra = 0
        self.btn_sembrar.config(text="🌱 SEMBRAR PLÁTANO", state=tk.NORMAL, bg='#4caf50')
        
        # RESTABLECER EL ESTADO A "No sembrado" AL REINICIAR
        self.estado_cultivo_label.config(text="Estado: No sembrado")
        self.actualizar_info_cultivo()
        
        self.inicializar_datos()
        self.actualizar_simulacion()
        messagebox.showinfo("Reinicio", "Simulación reiniciada correctamente")
    
    def actualizar_info_cultivo(self):
        """Actualiza la información del cultivo en la interfaz"""
        if self.platano_sembrado:
            etapas = {1: "Germinación", 2: "Crecimiento", 3: "Maduración"}
            etapa_text = etapas.get(self.etapa_crecimiento, "Desconocida")
            
            self.etapa_label.config(text=f"Etapa: {etapa_text}")
            self.dias_label.config(text=f"Días desde siembra: {self.dias_desde_siembra}")
            
            if self.etapa_crecimiento < 3:
                dias_restantes = 30 - (self.dias_desde_siembra % 30)
                self.proxima_label.config(text=f"Próxima etapa en: {dias_restantes} días")
            else:
                self.proxima_label.config(text="¡Etapa final alcanzada!")
        else:
            self.etapa_label.config(text="Estado: No sembrado")
            self.dias_label.config(text="")
            self.proxima_label.config(text="")
    
    def actualizar_simulacion(self):
        """Actualiza toda la simulación con los datos del mes actual"""
        self.simular_clima()
        self.actualizar_controles()
        self.actualizar_graficos()
        self.actualizar_estadisticas()
        self.actualizar_info_cultivo()
        self.dibujar_parcela()
        self.verificar_alertas()
    
    def simular_clima(self):
        """Simula los efectos del clima en la humedad del suelo"""
        mes_nombre = self.meses[self.mes_actual]
        clima = self.patrones_clima[mes_nombre]
        
        # Calcular efecto neto en humedad
        efecto_lluvia = clima['lluvia'] * 0.1
        efecto_sequia = clima['sequia'] * 0.2
        efecto_temperatura = (clima['temperatura'] - 25) * 0.5
        
        cambio_humedad_neto = efecto_lluvia - efecto_sequia - efecto_temperatura
        
        # Aplicar cambios a cada sensor
        for sensor_id in self.datos_sensores:
            variacion = random.uniform(-5, 5)
            nueva_humedad = self.datos_sensores[sensor_id]['humedad'] + cambio_humedad_neto + variacion
            nueva_humedad = max(30, min(95, nueva_humedad))
            
            self.datos_sensores[sensor_id]['humedad'] = round(nueva_humedad, 1)
        
        # Registrar datos para historial
        humedades = [sensor['humedad'] for sensor in self.datos_sensores.values()]
        humedad_promedio = sum(humedades) / len(humedades)
        self.historial_humedad.append(humedad_promedio)
    
    def actualizar_controles(self):
        """Actualiza los controles de la interfaz"""
        mes_nombre = self.meses[self.mes_actual]
        clima = self.patrones_clima[mes_nombre]
        
        self.mes_label.config(text=f"Mes: {mes_nombre}")
        self.clima_label.config(
            text=f"Lluvia: {clima['lluvia']}mm | Temp: {clima['temperatura']}°C | Sequía: {clima['sequia']}%"
        )
    
    def actualizar_graficos(self):
        """Actualiza todos los gráficos"""
        self.actualizar_grafico_barras()
        self.actualizar_grafico_pastel()
        self.actualizar_grafico_prediccion()
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas detalladas"""
        self.stats_canvas.delete("all")
        
        if not self.historial_humedad:
            self.stats_canvas.create_text(325, 400, 
                                        text='No hay datos suficientes\npara mostrar estadísticas', 
                                        font=('Arial', 14, 'bold'), fill='white',
                                        justify=tk.CENTER)
            return
        
        # Calcular estadísticas
        humedad_actual = self.historial_humedad[-1] if self.historial_humedad else 0
        humedad_min = min(self.historial_humedad) if self.historial_humedad else 0
        humedad_max = max(self.historial_humedad) if self.historial_humedad else 0
        humedad_promedio = sum(self.historial_humedad) / len(self.historial_humedad) if self.historial_humedad else 0
        
        # Contar sensores por estado
        estados = {'IDEAL': 0, 'BAJA': 0, 'ALTA': 0}
        for sensor in self.datos_sensores.values():
            if sensor['humedad'] < self.humedad_ideal_min:
                estados['BAJA'] += 1
            elif sensor['humedad'] > self.humedad_ideal_max:
                estados['ALTA'] += 1
            else:
                estados['IDEAL'] += 1
        
        # Texto de estadísticas
        stats_text = f"""ESTADÍSTICAS DETALLADAS - MES {self.meses[self.mes_actual]}

HUMEDAD:
• Actual: {humedad_actual:.1f}%
• Mínima Histórica: {humedad_min:.1f}%
• Máxima Histórica: {humedad_max:.1f}%
• Promedio: {humedad_promedio:.1f}%

SENSORES ({self.total_sensores} total):
• Ideales: {estados['IDEAL']} ({estados['IDEAL']/self.total_sensores*100:.1f}%)
• Baja Humedad: {estados['BAJA']} ({estados['BAJA']/self.total_sensores*100:.1f}%)
• Alta Humedad: {estados['ALTA']} ({estados['ALTA']/self.total_sensores*100:.1f}%)

RECURSOS:
• Nivel de agua: {self.nivel_agua}%
• Meses simulados: {len(self.historial_humedad)}
• Áreas totales: {self.num_areas}

CULTIVO:
• Estado: {'Plátanos sembrados' if self.platano_sembrado else 'No sembrado'}"""
        
        if self.platano_sembrado:
            etapas = {1: "Germinación", 2: "Crecimiento", 3: "Maduración"}
            etapa_text = etapas.get(self.etapa_crecimiento, "Desconocida")
            stats_text += f"""
• Etapa actual: {etapa_text}
• Días desde siembra: {self.dias_desde_siembra}
• Próxima etapa: {30 - (self.dias_desde_siembra % 30) if self.etapa_crecimiento < 3 else '¡Final!'} días

RANGO IDEAL PARA PLÁTANO: {self.humedad_ideal_min}% - {self.humedad_ideal_max}%"""
        
        # Dibujar texto
        lines = stats_text.split('\n')
        for i, line in enumerate(lines):
            y_pos = 50 + i * 25
            self.stats_canvas.create_text(50, y_pos, text=line, 
                                         font=('Arial', 11, 'bold'), 
                                         fill='white', anchor=tk.W)
        
        # Título
        self.stats_canvas.create_text(325, 20, 
                                     text="📈 ESTADÍSTICAS DETALLADAS", 
                                     font=('Arial', 16, 'bold'), fill='white')
        
        # Dibujar gráfico de progreso si hay cultivo
        if self.platano_sembrado:
            self.dibujar_progreso_cultivo()
    
    def dibujar_progreso_cultivo(self):
        """Dibuja una barra de progreso del cultivo"""
        y_base = 600
        ancho_total = 600
        alto_barra = 30
        
        # Fondo de la barra
        self.stats_canvas.create_rectangle(50, y_base, 50 + ancho_total, y_base + alto_barra,
                                          fill='#333333', outline='white', width=2)
        
        # Progreso actual
        progreso = min(1.0, self.dias_desde_siembra / 90.0)
        ancho_progreso = ancho_total * progreso
        
        # Color según etapa
        if self.etapa_crecimiento == 1:
            color = '#8bc34a'
        elif self.etapa_crecimiento == 2:
            color = '#4caf50'
        else:
            color = '#388e3c'
        
        # Barra de progreso
        self.stats_canvas.create_rectangle(50, y_base, 50 + ancho_progreso, y_base + alto_barra,
                                          fill=color, outline='')
        
        # Etiquetas
        self.stats_canvas.create_text(325, y_base - 20, 
                                     text="PROGRESO DEL CULTIVO", 
                                     font=('Arial', 12, 'bold'), fill='white')
        
        self.stats_canvas.create_text(325, y_base + alto_barra + 20, 
                                     text=f"{self.dias_desde_siembra}/90 días ({progreso*100:.1f}%)", 
                                     font=('Arial', 10, 'bold'), fill='white')
        
        # Marcas de etapas
        for i, (dias, etapa) in enumerate([(0, "Inicio"), (30, "Germ"), (60, "Crec"), (90, "Mad")]):
            x = 50 + (dias / 90.0) * ancho_total
            self.stats_canvas.create_line(x, y_base - 10, x, y_base + alto_barra + 10, 
                                        fill='white', width=1)
            self.stats_canvas.create_text(x, y_base - 25, text=etapa, 
                                         font=('Arial', 8), fill='white')
    
    def actualizar_grafico_barras(self):
        """Actualiza el gráfico de barras de humedad por áreas"""
        self.bar_canvas.delete("all")
        
        # Calcular humedad promedio por área
        humedades_areas = []
        for area in range(self.num_areas):
            sensores_area = [self.datos_sensores[area * self.sensores_por_area + i] 
                           for i in range(self.sensores_por_area)]
            humedades = [sensor['humedad'] for sensor in sensores_area]
            humedad_promedio = sum(humedades) / len(humedades)
            humedades_areas.append(humedad_promedio)
        
        # Configuración del gráfico
        canvas_width = 650
        canvas_height = 500
        margin = 80
        graph_width = canvas_width - 2 * margin
        graph_height = canvas_height - 2 * margin
        bar_width = graph_width / (self.num_areas + 1)
        
        # Dibujar ejes
        self.bar_canvas.create_line(margin, margin, margin, canvas_height - margin, width=2, fill='white')
        self.bar_canvas.create_line(margin, canvas_height - margin, canvas_width - margin, canvas_height - margin, width=2, fill='white')
        
        # Título
        self.bar_canvas.create_text(canvas_width // 2, 30, 
                                   text="Humedad por Área de Cultivo", 
                                   font=('Arial', 16, 'bold'), fill='white')
        
        # Dibujar barras
        max_humedad = max(humedades_areas) if humedades_areas else 100
        min_humedad = min(humedades_areas) if humedades_areas else 0
        
        for i, humedad in enumerate(humedades_areas):
            x0 = margin + (i + 0.5) * bar_width
            y0 = canvas_height - margin
            
            # Calcular altura de la barra
            bar_height = (humedad / 100) * graph_height
            
            # Color según humedad
            if humedad < self.humedad_ideal_min:
                color = '#ff9800'  # Naranja
            elif humedad > self.humedad_ideal_max:
                color = '#f44336'  # Rojo
            else:
                color = '#4caf50'  # Verde
            
            # Dibujar barra
            self.bar_canvas.create_rectangle(
                x0 - bar_width/2, y0 - bar_height,
                x0 + bar_width/2, y0,
                fill=color, outline='white', width=1
            )
            
            # Etiqueta del valor
            self.bar_canvas.create_text(x0, y0 - bar_height - 10, 
                                       text=f"{humedad:.1f}%", 
                                       font=('Arial', 9, 'bold'), fill='white')
            
            # Etiqueta del área
            self.bar_canvas.create_text(x0, y0 + 15, 
                                       text=f"Área {i+1}", 
                                       font=('Arial', 9), fill='white')
        
        # Líneas de referencia
        y_ideal_min = canvas_height - margin - (self.humedad_ideal_min / 100) * graph_height
        y_ideal_max = canvas_height - margin - (self.humedad_ideal_max / 100) * graph_height
        
        self.bar_canvas.create_line(margin, y_ideal_min, canvas_width - margin, y_ideal_min, 
                                   fill='blue', dash=(4, 2), width=2)
        self.bar_canvas.create_line(margin, y_ideal_max, canvas_width - margin, y_ideal_max, 
                                   fill='red', dash=(4, 2), width=2)
        
        # Leyenda
        self.bar_canvas.create_text(canvas_width - 100, margin - 20, 
                                   text="=== Mín Ideal", fill='blue', font=('Arial', 9))
        self.bar_canvas.create_text(canvas_width - 100, margin, 
                                   text="=== Máx Ideal", fill='red', font=('Arial', 9))
    
    def actualizar_grafico_pastel(self):
        """Actualiza el gráfico de pastel de estados de sensores"""
        self.pie_canvas.delete("all")
        
        # Contar estados
        estados = {'IDEAL': 0, 'BAJA': 0, 'ALTA': 0}
        for sensor in self.datos_sensores.values():
            if sensor['humedad'] < self.humedad_ideal_min:
                estados['BAJA'] += 1
            elif sensor['humedad'] > self.humedad_ideal_max:
                estados['ALTA'] += 1
            else:
                estados['IDEAL'] += 1
        
        total_sensores = self.total_sensores
        if total_sensores == 0:
            return
        
        # Configuración
        canvas_width = 650
        canvas_height = 500
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        radius = 150
        
        # Colores
        colores = {'IDEAL': '#4caf50', 'BAJA': '#ff9800', 'ALTA': '#f44336'}
        
        # Dibujar gráfico de pastel
        start_angle = 0
        for estado, cantidad in estados.items():
            if cantidad == 0:
                continue
                
            # Calcular ángulo
            angle = (cantidad / total_sensores) * 360
            
            # Dibujar sector
            self.dibujar_sector(self.pie_canvas, center_x, center_y, radius, 
                               start_angle, start_angle + angle, colores[estado])
            
            # Etiqueta
            porcentaje = (cantidad / total_sensores) * 100
            mid_angle = start_angle + angle / 2
            label_radius = radius + 40
            label_x = center_x + label_radius * math.cos(math.radians(mid_angle))
            label_y = center_y - label_radius * math.sin(math.radians(mid_angle))
            
            self.pie_canvas.create_text(label_x, label_y, 
                                       text=f"{estado}\n{porcentaje:.1f}%", 
                                       font=('Arial', 10, 'bold'), 
                                       fill=colores[estado], 
                                       justify=tk.CENTER)
            
            start_angle += angle
        
        # Título
        self.pie_canvas.create_text(center_x, 30, 
                                   text="Distribución de Estados de Sensores", 
                                   font=('Arial', 16, 'bold'), fill='white')
        
        # Leyenda
        y_legend = center_y + radius + 60
        for i, (estado, color) in enumerate(colores.items()):
            x_legend = center_x - 100 + i * 120
            self.pie_canvas.create_rectangle(x_legend - 50, y_legend - 15,
                                           x_legend - 30, y_legend + 15,
                                           fill=color, outline='white')
            self.pie_canvas.create_text(x_legend, y_legend,
                                       text=f"{estado}: {estados[estado]}",
                                       font=('Arial', 10, 'bold'), fill='white')
    
    def dibujar_sector(self, canvas, x, y, r, start_angle, end_angle, color):
        """Dibuja un sector circular"""
        points = [x, y]
        for angle in range(int(start_angle), int(end_angle) + 1):
            rad_angle = math.radians(angle)
            points.extend([x + r * math.cos(rad_angle), y - r * math.sin(rad_angle)])
        points.extend([x, y])
        canvas.create_polygon(points, fill=color, outline='white', width=2)
    
    def actualizar_grafico_prediccion(self):
        """Actualiza el gráfico de predicción"""
        self.pred_canvas.delete("all")
        
        if len(self.historial_humedad) < 2:
            self.pred_canvas.create_text(325, 250, 
                                       text="Se necesitan más datos\npara la predicción", 
                                       font=('Arial', 14, 'bold'), fill='white',
                                       justify=tk.CENTER)
            return
        
        # Configuración
        canvas_width = 650
        canvas_height = 500
        margin = 80
        graph_width = canvas_width - 2 * margin
        graph_height = canvas_height - 2 * margin
        
        # Datos para mostrar
        meses_mostrar = min(12, len(self.historial_humedad) + 3)
        datos = self.historial_humedad[:]
        
        # Añadir predicción simple
        if len(datos) >= 3:
            ultimos_3 = datos[-3:]
            tendencia = (ultimos_3[-1] - ultimos_3[0]) / 2
            for i in range(meses_mostrar - len(datos)):
                pred_valor = datos[-1] + tendencia * (i + 1)
                datos.append(max(30, min(90, pred_valor)))
        
        # Dibujar ejes
        self.pred_canvas.create_line(margin, margin, margin, canvas_height - margin, width=2, fill='white')
        self.pred_canvas.create_line(margin, canvas_height - margin, canvas_width - margin, canvas_height - margin, width=2, fill='white')
        
        # Título
        self.pred_canvas.create_text(canvas_width // 2, 30, 
                                   text="Predicción de Humedad", 
                                   font=('Arial', 16, 'bold'), fill='white')
        
        # Dibujar líneas de referencia
        y_min_ideal = canvas_height - margin - (self.humedad_ideal_min / 100) * graph_height
        y_max_ideal = canvas_height - margin - (self.humedad_ideal_max / 100) * graph_height
        
        self.pred_canvas.create_line(margin, y_min_ideal, canvas_width - margin, y_min_ideal, 
                                   fill='blue', dash=(4, 2), width=2)
        self.pred_canvas.create_line(margin, y_max_ideal, canvas_width - margin, y_max_ideal, 
                                   fill='red', dash=(4, 2), width=2)
        
        # Dibujar línea de datos
        puntos = []
        for i, humedad in enumerate(datos):
            x = margin + (i / (meses_mostrar - 1)) * graph_width
            y = canvas_height - margin - (humedad / 100) * graph_height
            
            puntos.extend([x, y])
            
            # Punto
            color = '#4caf50' if i < len(self.historial_humedad) else '#ff6b35'
            self.pred_canvas.create_oval(x-4, y-4, x+4, y+4, fill=color, outline='white')
            
            # Etiqueta del mes
            if i < len(self.meses):
                mes_text = self.meses[i]
            else:
                mes_text = f"P{i-len(self.meses)+1}"
            
            self.pred_canvas.create_text(x, canvas_height - margin + 20, 
                                       text=mes_text, font=('Arial', 8), fill='white')
        
        # Dibujar línea continua
        if len(puntos) >= 4:
            self.pred_canvas.create_line(puntos[:len(self.historial_humedad)*2], 
                                       fill='#4caf50', width=3)
            if len(datos) > len(self.historial_humedad):
                puntos_pred = puntos[len(self.historial_humedad)*2-2:]
                self.pred_canvas.create_line(puntos_pred, fill='#ff6b35', width=3, dash=(4, 2))
        
        # Leyenda
        self.pred_canvas.create_text(canvas_width - 100, margin - 20, 
                                   text="==== Mín Ideal", fill='blue', font=('Arial', 9))
        self.pred_canvas.create_text(canvas_width - 100, margin, 
                                   text="=== Máx Ideal", fill='red', font=('Arial', 9))
        self.pred_canvas.create_text(canvas_width - 100, margin + 20, 
                                   text="● Histórico", fill='#4caf50', font=('Arial', 9))
        self.pred_canvas.create_text(canvas_width - 100, margin + 40, 
                                   text="● Predicción", fill='#ff6b35', font=('Arial', 9))
    
    def verificar_alertas(self):
        """Verifica y muestra alertas si es necesario"""
        alertas_nuevas = []
        
        # Verificar humedad crítica
        for sensor_id, data in self.datos_sensores.items():
            if data['humedad'] < 50:
                alertas_nuevas.append(f"🚨 Sensor {sensor_id + 1}: HUMEDAD MUY BAJA ({data['humedad']}%)")
            elif data['humedad'] > 90:
                alertas_nuevas.append(f"⚠️ Sensor {sensor_id + 1}: HUMEDAD MUY ALTA ({data['humedad']}%)")
        
        # Verificar nivel de agua
        if self.nivel_agua < 20:
            alertas_nuevas.append("💧 PILETA: Nivel de agua crítico (<20%)")
        
        # Verificar condiciones para el plátano
        if self.platano_sembrado:
            # Verificar humedad promedio para el cultivo
            humedades = [sensor['humedad'] for sensor in self.datos_sensores.values()]
            humedad_promedio = sum(humedades) / len(humedades)
            
            if humedad_promedio < self.humedad_ideal_min:
                alertas_nuevas.append("🌱 CULTIVO: Humedad muy baja para el plátano")
            elif humedad_promedio > self.humedad_ideal_max:
                alertas_nuevas.append("🌱 CULTIVO: Humedad muy alta para el plátano")
            
            # Alertas de crecimiento
            if self.etapa_crecimiento == 3:
                alertas_nuevas.append("🎉 ¡PLÁTANOS LISTOS PARA COSECHAR! 🍌")
        
        # Mostrar alertas
        if alertas_nuevas:
            mensaje = "\n".join(alertas_nuevas[:5])  # Máximo 5 alertas
            if len(alertas_nuevas) > 5:
                mensaje += f"\n\n... y {len(alertas_nuevas) - 5} alertas más"
            
            messagebox.showwarning("Alertas del Sistema", mensaje)

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorPlatano(root)
    root.mainloop()