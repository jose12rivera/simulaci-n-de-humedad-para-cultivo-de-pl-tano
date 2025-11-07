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
                'estado': 'Normal'
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
        
        # Panel izquierdo - Controles y sensores
        left_panel = tk.Frame(content_frame, bg='#3a6519', relief=tk.RAISED, bd=3)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        # Panel derecho - Gráficos
        right_panel = tk.Frame(content_frame, bg='#3a6519', relief=tk.RAISED, bd=3)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        
        self.crear_controles(left_panel)
        self.crear_graficos(right_panel)
    
    def crear_controles(self, parent):
        # Frame de controles superiores
        controles_frame = tk.Frame(parent, bg='#3a6519')
        controles_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Información del mes actual
        info_frame = tk.LabelFrame(controles_frame, text="📅 INFORMACIÓN DEL MES ACTUAL", 
                                  font=('Arial', 12, 'bold'), bg='#4a7c1f', fg='white',
                                  padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.mes_label = tk.Label(info_frame, text="Mes: Enero", font=('Arial', 14, 'bold'),
                                 bg='#4a7c1f', fg='yellow')
        self.mes_label.pack(anchor=tk.W)
        
        self.clima_label = tk.Label(info_frame, text="Lluvia: 40mm | Temp: 28°C | Sequía: 20%",
                                   font=('Arial', 11), bg='#4a7c1f', fg='white')
        self.clima_label.pack(anchor=tk.W)
        
        # Controles de simulación
        control_buttons = tk.Frame(controles_frame, bg='#3a6519')
        control_buttons.pack(fill=tk.X, pady=10)
        
        tk.Button(control_buttons, text="⏭️ AVANZAR MES", command=self.avanzar_mes,
                 bg='#ff6b35', fg='white', font=('Arial', 12, 'bold'),
                 relief=tk.RAISED, bd=3, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_buttons, text="🔄 REINICIAR SIMULACIÓN", command=self.reiniciar_simulacion,
                 bg='#2196f3', fg='white', font=('Arial', 12, 'bold'),
                 relief=tk.RAISED, bd=3, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Frame para sensores con scroll
        sensores_container = tk.Frame(parent, bg='#3a6519')
        sensores_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas y scrollbar para sensores
        canvas = tk.Canvas(sensores_container, bg='#3a6519', highlightthickness=0)
        scrollbar = tk.Scrollbar(sensores_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#3a6519')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.crear_vista_sensores()
    
    def crear_vista_sensores(self):
        """Crea la visualización de los sensores por áreas"""
        # Limpiar frame existente
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Crear visualización de áreas
        for area in range(self.num_areas):
            area_frame = tk.LabelFrame(self.scrollable_frame, 
                                     text=f"📍 ÁREA {area + 1}", 
                                     font=('Arial', 10, 'bold'),
                                     bg='#5a8c2f', fg='white', padx=10, pady=5)
            area_frame.pack(fill=tk.X, padx=5, pady=3)
            
            # Sensores del área
            for sensor_idx in range(self.sensores_por_area):
                sensor_id = area * self.sensores_por_area + sensor_idx
                sensor_data = self.datos_sensores[sensor_id]
                
                sensor_frame = tk.Frame(area_frame, bg='#5a8c2f')
                sensor_frame.pack(fill=tk.X, pady=2)
                
                # Icono según estado
                estado_color = '#4caf50'  # Normal - verde
                if sensor_data['humedad'] < self.humedad_ideal_min:
                    estado_color = '#ff9800'  # Baja - naranja
                elif sensor_data['humedad'] > self.humedad_ideal_max:
                    estado_color = '#f44336'  # Alta - rojo
                
                tk.Label(sensor_frame, text="🔍", font=('Arial', 12),
                        bg='#5a8c2f', fg=estado_color).pack(side=tk.LEFT)
                
                info_text = f"Sensor {sensor_id + 1}: {sensor_data['humedad']}%"
                tk.Label(sensor_frame, text=info_text, font=('Arial', 9),
                        bg='#5a8c2f', fg='white').pack(side=tk.LEFT, padx=5)
                
                estado_text = f"({sensor_data['estado']})"
                tk.Label(sensor_frame, text=estado_text, font=('Arial', 9, 'bold'),
                        bg='#5a8c2f', fg=estado_color).pack(side=tk.LEFT, padx=5)
    
    def crear_graficos(self, parent):
        # Notebook para diferentes gráficos
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Estilo para el notebook
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'))
        
        # Pestaña 1: Gráfico de barras - Humedad por áreas
        self.bar_frame = tk.Frame(notebook, bg='#2d5016')
        notebook.add(self.bar_frame, text='📊 Humedad por Áreas')
        
        # Pestaña 2: Gráfico de pastel - Distribución de estados
        self.pie_frame = tk.Frame(notebook, bg='#2d5016')
        notebook.add(self.pie_frame, text='🥧 Estados de Sensores')
        
        # Pestaña 3: Predicción
        self.pred_frame = tk.Frame(notebook, bg='#2d5016')
        notebook.add(self.pred_frame, text='🔮 Predicción')
        
        # Pestaña 4: Estadísticas detalladas
        self.stats_frame = tk.Frame(notebook, bg='#2d5016')
        notebook.add(self.stats_frame, text='📈 Estadísticas')
        
        # Canvas para gráficos
        self.bar_canvas = tk.Canvas(self.bar_frame, bg='#2d5016', highlightthickness=0)
        self.bar_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.pie_canvas = tk.Canvas(self.pie_frame, bg='#2d5016', highlightthickness=0)
        self.pie_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.pred_canvas = tk.Canvas(self.pred_frame, bg='#2d5016', highlightthickness=0)
        self.pred_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.stats_canvas = tk.Canvas(self.stats_frame, bg='#2d5016', highlightthickness=0)
        self.stats_canvas.pack(fill=tk.BOTH, expand=True)
    
    def avanzar_mes(self):
        """Avanza al siguiente mes en la simulación"""
        self.mes_actual = (self.mes_actual + 1) % 12
        self.actualizar_simulacion()
    
    def reiniciar_simulacion(self):
        """Reinicia la simulación a su estado inicial"""
        self.mes_actual = 0
        self.historial_humedad = []
        self.historial_riego = []
        self.alertas = []
        self.inicializar_datos()
        self.actualizar_simulacion()
        messagebox.showinfo("Reinicio", "Simulación reiniciada correctamente")
    
    def actualizar_simulacion(self):
        """Actualiza toda la simulación con los datos del mes actual"""
        self.simular_clima()
        self.actualizar_controles()
        self.actualizar_graficos()
        self.crear_vista_sensores()
        self.verificar_alertas()
    
    def simular_clima(self):
        """Simula los efectos del clima en la humedad del suelo"""
        mes_nombre = self.meses[self.mes_actual]
        clima = self.patrones_clima[mes_nombre]
        
        # Calcular efecto neto en humedad
        efecto_lluvia = clima['lluvia'] * 0.1  # Cada 10mm de lluvia aumenta 1% humedad
        efecto_sequia = clima['sequia'] * 0.2  # Cada 5% de sequía reduce 1% humedad
        efecto_temperatura = (clima['temperatura'] - 25) * 0.5  # Temperatura base 25°C
        
        cambio_humedad_neto = efecto_lluvia - efecto_sequia - efecto_temperatura
        
        # Aplicar cambios a cada sensor con variación aleatoria
        for sensor_id in self.datos_sensores:
            variacion = random.uniform(-5, 5)
            nueva_humedad = self.datos_sensores[sensor_id]['humedad'] + cambio_humedad_neto + variacion
            
            # Mantener humedad entre límites razonables
            nueva_humedad = max(30, min(95, nueva_humedad))
            
            self.datos_sensores[sensor_id]['humedad'] = round(nueva_humedad, 1)
            
            # Actualizar estado del sensor
            if nueva_humedad < self.humedad_ideal_min:
                self.datos_sensores[sensor_id]['estado'] = 'BAJA'
            elif nueva_humedad > self.humedad_ideal_max:
                self.datos_sensores[sensor_id]['estado'] = 'ALTA'
            else:
                self.datos_sensores[sensor_id]['estado'] = 'IDEAL'
        
        # Registrar datos para historial
        humedades = [sensor['humedad'] for sensor in self.datos_sensores.values()]
        humedad_promedio = sum(humedades) / len(humedades)
        self.historial_humedad.append(humedad_promedio)
        
        # Simular riego automático si es necesario
        areas_con_riego = self.calcular_riego()
        self.historial_riego.append(areas_con_riego)
    
    def calcular_riego(self):
        """Calcula qué áreas necesitan riego"""
        areas_con_riego = 0
        
        for area in range(self.num_areas):
            sensores_area = [self.datos_sensores[area * self.sensores_por_area + i] 
                           for i in range(self.sensores_por_area)]
            
            # Promedio de humedad en el área
            humedades = [sensor['humedad'] for sensor in sensores_area]
            humedad_promedio = sum(humedades) / len(humedades)
            
            # Si el promedio está por debajo del ideal, activar riego
            if humedad_promedio < self.humedad_ideal_min:
                areas_con_riego += 1
                # Aplicar riego a los sensores de esta área
                for sensor in sensores_area:
                    sensor['humedad'] = min(85, sensor['humedad'] + random.uniform(10, 20))
        
        return areas_con_riego
    
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
        self.actualizar_estadisticas()
    
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
        canvas_width = 700
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
                                   text="--- Mín Ideal", fill='blue', font=('Arial', 9))
        self.bar_canvas.create_text(canvas_width - 100, margin, 
                                   text="--- Máx Ideal", fill='red', font=('Arial', 9))
    
    def actualizar_grafico_pastel(self):
        """Actualiza el gráfico de pastel de estados de sensores"""
        self.pie_canvas.delete("all")
        
        # Contar estados
        estados = {'IDEAL': 0, 'BAJA': 0, 'ALTA': 0}
        for sensor in self.datos_sensores.values():
            estados[sensor['estado']] += 1
        
        total_sensores = self.total_sensores
        if total_sensores == 0:
            return
        
        # Configuración
        canvas_width = 700
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
            self.pred_canvas.create_text(350, 250, 
                                       text="Se necesitan más datos\npara la predicción", 
                                       font=('Arial', 14, 'bold'), fill='white',
                                       justify=tk.CENTER)
            return
        
        # Configuración
        canvas_width = 700
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
                                   text="--- Mín Ideal", fill='blue', font=('Arial', 9))
        self.pred_canvas.create_text(canvas_width - 100, margin, 
                                   text="--- Máx Ideal", fill='red', font=('Arial', 9))
        self.pred_canvas.create_text(canvas_width - 100, margin + 20, 
                                   text="● Histórico", fill='#4caf50', font=('Arial', 9))
        self.pred_canvas.create_text(canvas_width - 100, margin + 40, 
                                   text="● Predicción", fill='#ff6b35', font=('Arial', 9))
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas detalladas"""
        self.stats_canvas.delete("all")
        
        if not self.historial_humedad:
            self.stats_canvas.create_text(350, 250, 
                                        text='No hay datos suficientes\npara mostrar estadísticas', 
                                        font=('Arial', 14, 'bold'), fill='white',
                                        justify=tk.CENTER)
            return
        
        # Calcular estadísticas
        humedad_actual = self.historial_humedad[-1]
        humedad_min = min(self.historial_humedad)
        humedad_max = max(self.historial_humedad)
        humedad_promedio = sum(self.historial_humedad) / len(self.historial_humedad)
        
        # Contar sensores por estado
        estados = {'IDEAL': 0, 'BAJA': 0, 'ALTA': 0}
        for sensor in self.datos_sensores.values():
            estados[sensor['estado']] += 1
        
        # Texto de estadísticas
        stats_text = f"""ESTADÍSTICAS DETALLADAS

Humedad Actual: {humedad_actual:.1f}%
Humedad Mínima Histórica: {humedad_min:.1f}%
Humedad Máxima Histórica: {humedad_max:.1f}%
Humedad Promedio: {humedad_promedio:.1f}%

SENSORES:
• Ideales: {estados['IDEAL']}/{self.total_sensores}
• Baja Humedad: {estados['BAJA']}/{self.total_sensores}
• Alta Humedad: {estados['ALTA']}/{self.total_sensores}

RIEGO:
Áreas regadas este mes: {self.historial_riego[-1] if self.historial_riego else 0}
Total áreas: {self.num_areas}

RANGO IDEAL: {self.humedad_ideal_min}% - {self.humedad_ideal_max}%"""
        
        # Dibujar fondo del panel
        self.stats_canvas.create_rectangle(50, 50, 650, 450, 
                                          fill='#4a7c1f', outline='#2d5016', width=3)
        
        # Dibujar texto
        lines = stats_text.split('\n')
        for i, line in enumerate(lines):
            y_pos = 80 + i * 25
            self.stats_canvas.create_text(100, y_pos, text=line, 
                                         font=('Arial', 11, 'bold'), 
                                         fill='white', anchor=tk.W)
        
        # Título
        self.stats_canvas.create_text(350, 30, 
                                     text="📈 ESTADÍSTICAS DETALLADAS", 
                                     font=('Arial', 16, 'bold'), fill='white')
    
    def verificar_alertas(self):
        """Verifica y muestra alertas si es necesario"""
        alertas_nuevas = []
        
        # Verificar sensores con humedad crítica
        for sensor_id, data in self.datos_sensores.items():
            if data['humedad'] < 50:  # Humedad muy baja crítica
                alertas_nuevas.append(f"🚨 CRÍTICO: Sensor {sensor_id + 1} con humedad MUY BAJA ({data['humedad']}%)")
            elif data['humedad'] > 90:  # Humedad muy alta crítica
                alertas_nuevas.append(f"⚠️ ALERTA: Sensor {sensor_id + 1} con humedad MUY ALTA ({data['humedad']}%)")
        
        # Mostrar alertas si hay nuevas
        if alertas_nuevas:
            mensaje_alerta = "\n".join(alertas_nuevas[:3])  # Mostrar máximo 3 alertas
            if len(alertas_nuevas) > 3:
                mensaje_alerta += f"\n\n... y {len(alertas_nuevas) - 3} alertas más"
            
            messagebox.showwarning("Alertas del Sistema", mensaje_alerta)

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorPlatano(root)
    root.mainloop()