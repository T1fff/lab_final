import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import heapq
import math
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class NodoEnergia:
    """
    Clase que representa un nodo en la red de energía.
    Puede ser un generador, almacenamiento o consumidor.
    """
    def __init__(self, nombre, produccion, perdida, sostenibilidad):
        self.nombre = nombre
        self.produccion = float(produccion)  # kW de energía generada
        self.perdida = float(perdida)  # % de pérdida en transmisión
        self.sostenibilidad = float(sostenibilidad)  # 0-100, siendo 100 el más sostenible
    
    def __str__(self):
        return f"{self.nombre} (Prod: {self.produccion}kW, Pérd: {self.perdida}%, Sost: {self.sostenibilidad})"


class RedEnergia:
    """
    Clase que representa la red de energía como un grafo.
    Los nodos son instancias de NodoEnergia y las aristas representan conexiones.
    """
    def __init__(self):
        self.nodos = {}  # Diccionario de nodos por nombre
        self.conexiones = {}  # Diccionario de adyacencia
        
    def agregar_nodo(self, nodo):
        """Agrega un nodo a la red"""
        self.nodos[nodo.nombre] = nodo
        if nodo.nombre not in self.conexiones:
            self.conexiones[nodo.nombre] = []
    
    def agregar_conexion(self, nodo1_nombre, nodo2_nombre):
        """Agrega una conexión bidireccional entre dos nodos"""
        if nodo1_nombre in self.nodos and nodo2_nombre in self.nodos:
            if nodo2_nombre not in self.conexiones[nodo1_nombre]:
                self.conexiones[nodo1_nombre].append(nodo2_nombre)
            if nodo1_nombre not in self.conexiones[nodo2_nombre]:
                self.conexiones[nodo2_nombre].append(nodo1_nombre)
            return True
        return False
    
    def obtener_peso_arista(self, nodo1_nombre, nodo2_nombre, estrategia):
        """
        Calcula el peso de una arista según la estrategia seleccionada
        """
        nodo1 = self.nodos[nodo1_nombre]
        nodo2 = self.nodos[nodo2_nombre]
        
        if estrategia == "sostenibilidad":
            # Menor peso = mayor sostenibilidad
            return 200 - (nodo1.sostenibilidad + nodo2.sostenibilidad) / 2
        
        elif estrategia == "perdida":
            # Menor peso = menor pérdida
            return (nodo1.perdida + nodo2.perdida) / 2
        
        elif estrategia == "produccion":
            # Menor peso = mayor producción
            if nodo1.produccion + nodo2.produccion > 0:
                return 1000 / (nodo1.produccion + nodo2.produccion + 1)
            else:
                return 1000
        
        return 1  # Peso predeterminado
    
    def encontrar_ruta_optima(self, inicio, fin, estrategia):
        """
        Implementación del algoritmo de Dijkstra para encontrar la ruta más óptima
        según la estrategia seleccionada
        """
        if inicio not in self.nodos or fin not in self.nodos:
            return None, None
        
        # Inicializar distancias
        distancias = {nodo: float('infinity') for nodo in self.nodos}
        distancias[inicio] = 0
        
        # Inicializar padres para reconstruir la ruta
        padres = {nodo: None for nodo in self.nodos}
        
        # Cola de prioridad para nodos no visitados
        no_visitados = [(0, inicio)]
        
        while no_visitados:
            # Obtener nodo con menor distancia
            distancia_actual, nodo_actual = heapq.heappop(no_visitados)
            
            # Si encontramos el destino, terminamos
            if nodo_actual == fin:
                break
            
            # Si la distancia es mayor que la conocida, saltamos
            if distancia_actual > distancias[nodo_actual]:
                continue
            
            # Revisar todos los vecinos
            for vecino in self.conexiones[nodo_actual]:
                peso = self.obtener_peso_arista(nodo_actual, vecino, estrategia)
                distancia = distancia_actual + peso
                
                # Actualizar si encontramos un camino más corto
                if distancia < distancias[vecino]:
                    distancias[vecino] = distancia
                    padres[vecino] = nodo_actual
                    heapq.heappush(no_visitados, (distancia, vecino))
        
        # Reconstruir el camino
        if distancias[fin] == float('infinity'):
            return None, None  # No hay camino
        
        # Reconstruir la ruta óptima
        ruta = []
        nodo_actual = fin
        while nodo_actual:
            ruta.append(nodo_actual)
            nodo_actual = padres[nodo_actual]
        
        # Invertir para que vaya desde el inicio
        ruta.reverse()
        
        return ruta, distancias[fin]
    
    def cargar_desde_csv(self, archivo_nodos, archivo_conexiones):
        """
        Carga los nodos y conexiones desde archivos CSV
        """
        # Limpiar datos existentes
        self.nodos = {}
        self.conexiones = {}
        
        # Cargar nodos
        try:
            with open(archivo_nodos, 'r', newline='', encoding='utf-8') as f:
                lector = csv.DictReader(f)
                for fila in lector:
                    try:
                        nombre = fila['Nombre']
                        produccion = fila['Produccion']
                        perdida = fila['Pérdida'] if 'Pérdida' in fila else fila['Perdida']
                        sostenibilidad = fila['Sostenibilidad']
                        
                        nodo = NodoEnergia(nombre, float(produccion), float(perdida), float(sostenibilidad))
                        self.agregar_nodo(nodo)
                    except (KeyError, ValueError) as e:
                        print(f"Error en fila: {e}")
                        return False
        except Exception as e:
            print(f"Error al cargar nodos: {e}")
            return False
        
        # Cargar conexiones
        try:
            with open(archivo_conexiones, 'r', newline='', encoding='utf-8') as f:
                lector = csv.reader(f)
                # Primera fila contiene los nombres de los nodos (excepto la primera celda)
                primera_fila = next(lector, None)
                if not primera_fila or len(primera_fila) <= 1:
                    print("Formato de archivo de conexiones inválido")
                    return False
                    
                nombres_nodos = primera_fila[1:]  # Ignorar la primera celda
                
                for fila in lector:
                    if len(fila) <= 1:
                        continue
                    
                    nodo_origen = fila[0]
                    if nodo_origen not in self.nodos:
                        continue
                    
                    # Procesar cada conexión en la fila
                    for i, valor in enumerate(fila[1:]):
                        if i >= len(nombres_nodos):
                            break
                            
                        if valor == '1':
                            nodo_destino = nombres_nodos[i]
                            if nodo_destino in self.nodos:
                                self.agregar_conexion(nodo_origen, nodo_destino)
        except Exception as e:
            print(f"Error al cargar conexiones: {e}")
            return False
            
        return True
        
    def visualizar_red(self, canvas_widget=None, ruta_optima=None, estrategia=None):
        """
        Visualiza la red usando NetworkX y Matplotlib
        Muestra información detallada de los nodos y pesos de las aristas
        """
        G = nx.Graph()
        
        # Agregar nodos con atributos
        for nombre, nodo in self.nodos.items():
            G.add_node(nombre, 
                    produccion=nodo.produccion, 
                    perdida=nodo.perdida, 
                    sostenibilidad=nodo.sostenibilidad)
        
        # Agregar aristas con pesos
        for nodo, vecinos in self.conexiones.items():
            for vecino in vecinos:
                # Calcular peso según estrategia (si se proporciona)
                if estrategia:
                    peso = self.obtener_peso_arista(nodo, vecino, estrategia)
                    G.add_edge(nodo, vecino, weight=peso)
                else:
                    G.add_edge(nodo, vecino)
        
        # Crear figura
        plt.clf()
        fig = plt.figure(figsize=(10, 8))
        
        # Definir colores por tipo de nodo
        colores = []
        for nodo in G.nodes():
            if self.nodos[nodo].produccion > 0:
                colores.append('green')  # Generadores
            elif "Almacenamiento" in nodo:
                colores.append('blue')   # Almacenamiento
            elif "Residencial" in nodo:
                colores.append('red')    # Consumidores
            elif "Subestacion" in nodo:
                colores.append('orange') # Subestaciones
            else:
                colores.append('gray')   # Otros
        
        # Definir el layout - usar kamada_kawai para mejor distribución visual
        pos = nx.kamada_kawai_layout(G)
        
        # Dibujar nodos
        nx.draw_networkx_nodes(G, pos, node_color=colores, node_size=700, alpha=0.8)
        
        # Dibujar etiquetas de nodos (solo nombres)
        nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
        
        # Dibujar conexiones normales
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
        
        # Dibujar pesos en las aristas si se proporcionó estrategia
        if estrategia:
            edge_labels = {}
            for u, v in G.edges():
                peso = self.obtener_peso_arista(u, v, estrategia)
                edge_labels[(u, v)] = f"{peso:.1f}"
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
        
        # Dibujar ruta óptima si existe
        if ruta_optima and len(ruta_optima) > 1:
            edges = [(ruta_optima[i], ruta_optima[i+1]) for i in range(len(ruta_optima)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=edges, width=3, edge_color='red')
        
        # Añadir información de nodos como anotaciones
        for nodo in G.nodes():
            x, y = pos[nodo]
            datos_nodo = self.nodos[nodo]
            # Crear texto con los atributos del nodo
            info = f"P:{datos_nodo.produccion:.1f} L:{datos_nodo.perdida:.1f}% S:{datos_nodo.sostenibilidad:.1f}"
            plt.annotate(info, 
                        xy=(x, y), 
                        xytext=(0, 15),  # Desplazamiento vertical
                        textcoords="offset points",
                        ha='center', 
                        va='center',
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7),
                        fontsize=7)
        
        # Añadir leyenda de colores
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Generador'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Almacenamiento'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Consumidor'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Subestación'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Otros')
        ]
        plt.legend(handles=legend_elements, loc='upper left', title="Tipos de nodos")
        
        # Añadir leyenda para los atributos
        plt.figtext(0.02, 0.02, "P: Producción (kW), L: Pérdida (%), S: Sostenibilidad (0-100)", 
                wrap=True, horizontalalignment='left', fontsize=8)
        
        # Ajustar los márgenes para que todo quepa
        plt.tight_layout()
        
        # Mostrar en ventana o en widget
        if canvas_widget:
            canvas = FigureCanvasTkAgg(fig, master=canvas_widget)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            return canvas
        else:
            plt.show()


class AplicacionRed:
    """
    Interfaz gráfica para la aplicación de simulación de la red de energía
    """
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Simulación de Red de Energía Renovable")
        self.ventana.geometry("1200x700")
        self.red = RedEnergia()
        self.canvas_grafo = None
        
        # Variables para almacenar rutas de archivos
        self.ruta_archivo_nodos = tk.StringVar()
        self.ruta_archivo_conexiones = tk.StringVar()
        
        # Variables para almacenar selecciones
        self.nodo_inicio = tk.StringVar()
        self.nodo_fin = tk.StringVar()
        self.estrategia = tk.StringVar(value="sostenibilidad")
        
        # Crear interfaz
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        # Crear frame principal
        frame_principal = ttk.Frame(self.ventana, padding="10")
        frame_principal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frames para controles y visualización
        frame_controles = ttk.LabelFrame(frame_principal, text="Controles", padding="10")
        frame_controles.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        frame_visualizacion = ttk.LabelFrame(frame_principal, text="Visualización de la Red", padding="10")
        frame_visualizacion.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        frame_resultados = ttk.LabelFrame(frame_principal, text="Resultados", padding="10")
        frame_resultados.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Configurar expansión
        self.ventana.columnconfigure(0, weight=1)
        self.ventana.rowconfigure(0, weight=1)
        frame_principal.columnconfigure(1, weight=3)
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.rowconfigure(0, weight=1)
        frame_principal.rowconfigure(1, weight=1)
        
        # Controles para cargar archivos
        ttk.Label(frame_controles, text="Archivo de Nodos (CSV):").grid(column=0, row=0, sticky=tk.W, pady=5)
        ttk.Entry(frame_controles, textvariable=self.ruta_archivo_nodos, width=30).grid(column=0, row=1, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(frame_controles, text="Examinar...", command=self._cargar_archivo_nodos).grid(column=1, row=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(frame_controles, text="Archivo de Conexiones (CSV):").grid(column=0, row=2, sticky=tk.W, pady=5)
        ttk.Entry(frame_controles, textvariable=self.ruta_archivo_conexiones, width=30).grid(column=0, row=3, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(frame_controles, text="Examinar...", command=self._cargar_archivo_conexiones).grid(column=1, row=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Button(frame_controles, text="Cargar Datos", command=self._cargar_datos).grid(column=0, row=4, columnspan=2, pady=10)
        
        # Separador
        ttk.Separator(frame_controles, orient=tk.HORIZONTAL).grid(column=0, row=5, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Controles para simulación
        ttk.Label(frame_controles, text="Nodo de inicio:").grid(column=0, row=6, sticky=tk.W, pady=5)
        self.combo_inicio = ttk.Combobox(frame_controles, textvariable=self.nodo_inicio, state="readonly")
        self.combo_inicio.grid(column=0, row=7, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(frame_controles, text="Nodo de destino:").grid(column=0, row=8, sticky=tk.W, pady=5)
        self.combo_fin = ttk.Combobox(frame_controles, textvariable=self.nodo_fin, state="readonly")
        self.combo_fin.grid(column=0, row=9, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(frame_controles, text="Estrategia de optimización:").grid(column=0, row=10, sticky=tk.W, pady=5)
        opciones_estrategia = ttk.Frame(frame_controles)
        opciones_estrategia.grid(column=0, row=11, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Radiobutton(opciones_estrategia, text="Maximizar sostenibilidad", variable=self.estrategia, value="sostenibilidad").pack(anchor=tk.W)
        ttk.Radiobutton(opciones_estrategia, text="Minimizar pérdidas", variable=self.estrategia, value="perdida").pack(anchor=tk.W)
        ttk.Radiobutton(opciones_estrategia, text="Maximizar producción", variable=self.estrategia, value="produccion").pack(anchor=tk.W)
        
        ttk.Button(frame_controles, text="Calcular Ruta Óptima", command=self._calcular_ruta).grid(column=0, row=12, columnspan=2, pady=10)
        
        # Frame para visualización del grafo
        self.frame_grafo = ttk.Frame(frame_visualizacion)
        self.frame_grafo.pack(fill=tk.BOTH, expand=True)
        
        # Frame para resultados
        self.texto_resultados = tk.Text(frame_resultados, height=12, wrap=tk.WORD)
        self.texto_resultados.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.texto_resultados, command=self.texto_resultados.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.texto_resultados.config(yscrollcommand=scrollbar.set)
        self.texto_resultados.config(state=tk.DISABLED)
    
    def _cargar_archivo_nodos(self):
        """Abre un diálogo para seleccionar el archivo de nodos"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de nodos",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.ruta_archivo_nodos.set(archivo)
    
    def _cargar_archivo_conexiones(self):
        """Abre un diálogo para seleccionar el archivo de conexiones"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de conexiones",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.ruta_archivo_conexiones.set(archivo)
    
    def _cargar_datos(self):
        """Carga los datos de los archivos CSV a la red"""
        if not self.ruta_archivo_nodos.get() or not self.ruta_archivo_conexiones.get():
            messagebox.showerror("Error", "Debes seleccionar ambos archivos CSV")
            return
        
        try:
            # Cargar datos desde archivos CSV
            exito = self.red.cargar_desde_csv(self.ruta_archivo_nodos.get(), self.ruta_archivo_conexiones.get())
            
            if not exito:
                messagebox.showerror("Error", "Hubo un problema al cargar los archivos. Verifica el formato.")
                return
            
            # Actualizar listas desplegables
            nombres_nodos = list(self.red.nodos.keys())
            self.combo_inicio['values'] = nombres_nodos
            self.combo_fin['values'] = nombres_nodos
            
            if nombres_nodos:
                # Seleccionar por defecto nodos iniciales que puedan ser interesantes
                # Por ejemplo, un generador y un consumidor
                generadores = [n for n in nombres_nodos if self.red.nodos[n].produccion > 0]
                consumidores = [n for n in nombres_nodos if "Residencial" in n]
                
                if generadores:
                    self.nodo_inicio.set(generadores[0])
                else:
                    self.nodo_inicio.set(nombres_nodos[0])
                    
                if consumidores:
                    self.nodo_fin.set(consumidores[0])
                elif len(nombres_nodos) > 1:
                    self.nodo_fin.set(nombres_nodos[-1])
                else:
                    self.nodo_fin.set(nombres_nodos[0])
            
            # Visualizar la red
            self._visualizar_red()
            
            # Mostrar información de los nodos y conexiones cargados
            info = "Datos cargados correctamente\n\nNodos en la red:\n"
            for nombre, nodo in self.red.nodos.items():
                info += f"- {nombre}: Prod={nodo.produccion}kW, Pérd={nodo.perdida}%, Sost={nodo.sostenibilidad}\n"
            
            info += "\nConexiones:\n"
            for nodo, vecinos in self.red.conexiones.items():
                if vecinos:
                    info += f"- {nodo} conectado con: {', '.join(vecinos)}\n"
            
            self._actualizar_texto_resultados(info)
            
            messagebox.showinfo("Éxito", f"Datos cargados correctamente. {len(self.red.nodos)} nodos y {sum(len(v) for v in self.red.conexiones.values())/2} conexiones.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            import traceback
            traceback.print_exc()  # Mostrar traza de error en la consola
    
    def _calcular_ruta(self):
        """Calcula la ruta óptima según la estrategia seleccionada"""
        if not self.red.nodos:
            messagebox.showerror("Error", "No hay datos cargados")
            return
        
        inicio = self.nodo_inicio.get()
        fin = self.nodo_fin.get()
        estrategia = self.estrategia.get()
        
        if not inicio or not fin:
            messagebox.showerror("Error", "Debes seleccionar nodos de inicio y destino")
            return
        
        # Calcular ruta óptima
        ruta, costo = self.red.encontrar_ruta_optima(inicio, fin, estrategia)
        
        if ruta is None:
            messagebox.showwarning("Advertencia", "No se encontró ruta entre los nodos seleccionados")
            self._actualizar_texto_resultados("No se encontró una ruta posible entre los nodos seleccionados.")
            self._visualizar_red()  # Actualizar sin ruta
            return
        
        # Visualizar ruta pasando la estrategia para mostrar los pesos
        self._visualizar_red(ruta, estrategia)
        
        # Calcular métricas de la ruta
        energia_total = 0
        perdida_total = 0
        sostenibilidad_media = 0
        
        for i in range(len(ruta)):
            nodo_actual = self.red.nodos[ruta[i]]
            
            # Sumar producción
            energia_total += nodo_actual.produccion
            
            # Calcular pérdida acumulada
            if energia_total > 0:
                perdida_total += energia_total * (nodo_actual.perdida / 100)
            
            # Acumular sostenibilidad
            sostenibilidad_media += nodo_actual.sostenibilidad
        
        # Calcular promedios
        if len(ruta) > 0:
            sostenibilidad_media /= len(ruta)
        
        # Actualizar resultados
        resultado = f"Ruta óptima según la estrategia '{estrategia}':\n"
        resultado += " -> ".join(ruta) + "\n\n"
        resultado += f"Longitud de la ruta: {len(ruta)} nodos\n"
        resultado += f"Valor de costo: {costo:.2f}\n"
        resultado += f"Energía producida total: {energia_total:.2f} kW\n"
        resultado += f"Pérdida estimada total: {perdida_total:.2f} kW ({(perdida_total/energia_total*100 if energia_total > 0 else 0):.2f}%)\n"
        resultado += f"Sostenibilidad media: {sostenibilidad_media:.2f}/100"
        
        self._actualizar_texto_resultados(resultado)
    
    def _visualizar_red(self, ruta_optima=None, estrategia=None):
        """Visualiza la red en la interfaz"""
        # Limpiar visualización anterior
        for widget in self.frame_grafo.winfo_children():
            widget.destroy()
        
        if not self.red.nodos:
            return
        
        # Visualizar red con la ruta óptima y estrategia (para mostrar pesos)
        self.canvas_grafo = self.red.visualizar_red(self.frame_grafo, ruta_optima, estrategia)
    
    def _actualizar_texto_resultados(self, texto):
        """Actualiza el texto en el área de resultados"""
        self.texto_resultados.config(state=tk.NORMAL)
        self.texto_resultados.delete(1.0, tk.END)
        self.texto_resultados.insert(tk.END, texto)
        self.texto_resultados.config(state=tk.DISABLED)


def main():
    # Crear la ventana principal
    ventana = tk.Tk()
    app = AplicacionRed(ventana)
    
    # Para facilitar las pruebas, puedes incluir rutas de ejemplos
    # app.ruta_archivo_nodos.set("nodos.csv")
    # app.ruta_archivo_conexiones.set("conexiones.csv")
    
    # Ejecutar la aplicación
    ventana.mainloop()

if __name__ == "__main__":
    main()