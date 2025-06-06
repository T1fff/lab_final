
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from red import RedEnergia
from PIL import Image, ImageTk

class AplicacionRed:
    def __init__(self, root):
        self.root = root
        self.root.title("Red de Energía Renovable")
        self.root.geometry("1152x648")
        self.red = RedEnergia()
        self.canvas_frame = None
        self.ruta_nodos = tk.StringVar()
        self.ruta_conexiones = tk.StringVar()
        self.nodo_inicio = tk.StringVar()
        self.nodo_fin = tk.StringVar()
        self.estrategia = tk.StringVar(value="sostenibilidad")
        
        self.frames = {}
        self.crear_frames()
        self.estilo_boton_ttk()
        self.mostrar_frames("inicio")
        
    def crear_frames(self):
        frame_inicio = self.crear_frame_inicio()
        frame_redFlujo = self.crear_frame_red()
        
        self.frames["inicio"] = frame_inicio
        self.frames["Red Flujo"] = frame_redFlujo
        
        for frame in self.frames.values():
            frame.place(relwidth=1, relheight=1)
            
    def mostrar_frames(self, nombre_frame):
        frame = self.frames[nombre_frame]
        frame.tkraise()
        
    def estilo_boton_ttk(self):
        style = ttk.Style()

        style.configure("estilo.TButton",
                        font=("Segoe Ui", 10, "bold"),
                        padding = 10,
                        background="#007ACC",
                        foreground="black")
        style.map("estilo.TButton",
                   background=[
            ("active", "#005F9E"),
            ("pressed", "#004C80")
        ],
        foreground=[
            ("pressed", "black"),
            ("active", "black")
        ])
        
    def crear_frame_inicio(self):
        frame = tk.Frame(self.root)
        
        # fondo
        image1 = Image.open("assets/image1_inicio.png")
        fondo = ImageTk.PhotoImage(image1)
        fondo_label = tk.Label(frame, image=fondo)
        fondo_label.image = fondo  # mantener referencia
        fondo_label.place(relwidth=1, relheight=1)
        
        boton_start = tk.Button(frame, 
                                text="Start", 
                                font = ("Arial", 18, "bold"),
                                width = 15,
                                height = 2,
                                bg="#f1fbff",               
                                fg="black",                 # Color de texto normal
                                activebackground="#e3f7ff", # Color al presionar
                                activeforeground="black",   # Texto al presionar
                                relief="raised",            # Relieve inicial
                                bd=5,  
                                command=lambda: self.mostrar_frames("Red Flujo"))
        boton_start.place(relx=0.5, rely=0.7, anchor="center")
        
        return frame
    
    def crear_frame_red(self):
        frame = tk.Frame(self.root)
        
        image2 = Image.open("assets/image2_red.png")
        fondo = ImageTk.PhotoImage(image2)
        fondo_label = tk.Label(frame, image=fondo)
        fondo_label.image = fondo  # mantener referencia
        fondo_label.place(relwidth=1, relheight=1)
        
        # seleccionar archivo de nodos
        ttk.Entry(frame, textvariable=self.ruta_nodos, width=50).place(x=90, y=200)
        ttk.Button(frame, text="Seleccionar", style="estilo.TButton", command=self._cargar_nodos).place(x=190, y=230)
        
        # seleccionar archivo de conexiones
        ttk.Entry(frame, textvariable=self.ruta_conexiones, width=50).place(x=700, y=70)
        ttk.Button(frame, text="Seleccionar", style="estilo.TButton" ,command=self._cargar_conexiones).place(x=800, y=100)
        
        # botón de cargar ruta (tengo q ver como rayos hago esto)
        ttk.Button(frame, text="Cargar Red", style="estilo.TButton",command=self._cargar_red).place(x=800, y=200)
        
        # seleccionar nodo inicio
        self.combo_inicio = ttk.Combobox(frame, textvariable=self.nodo_inicio)
        self.combo_inicio.place(x=120, y=330, width= 200)
        
        # seleccionar nodo final
        self.combo_fin = ttk.Combobox(frame, textvariable=self.nodo_fin)
        self.combo_fin.place(x=735, y=330, width=200)
        
        # escoger estrategia
        pos_y = 450
        pos_x = 20
        for val in ["1", "2", "3"]:
            ttk.Radiobutton(frame, text=val.capitalize(), value=val, variable=self.estrategia).place(x=pos_x, y=pos_y)
            pos_y += 40

        # calcular ruta óptima
        ttk.Button(frame, text="Calcular Ruta Óptima", style="estilo.TButton", command=self._calcular_ruta).place(x=750, y=400)
        
        return frame
    
    def _cargar_nodos(self):
        archivo = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if archivo:
            self.ruta_nodos.set(archivo)

    def _cargar_conexiones(self):
        archivo = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if archivo:
            self.ruta_conexiones.set(archivo)

    def _cargar_red(self):
        if not self.ruta_nodos.get() or not self.ruta_conexiones.get():
            messagebox.showerror("Error", "Selecciona ambos archivos.")
            return

        if self.red.cargar_desde_csv(self.ruta_nodos.get(), self.ruta_conexiones.get()):
            nodos = list(self.red.nodos.keys())
            self.combo_inicio["values"] = nodos
            self.combo_fin["values"] = nodos
            if nodos:
                self.nodo_inicio.set(nodos[0])
                self.nodo_fin.set(nodos[-1])
            self._visualizar()

    def _calcular_ruta(self):
        inicio = self.nodo_inicio.get()
        fin = self.nodo_fin.get()
        estrategia = self.estrategia.get()
        if not inicio or not fin:
            messagebox.showerror("Error", "Selecciona nodos de inicio y fin.")
            return
        ruta, costo = self.red.encontrar_ruta_optima(inicio, fin, estrategia)
        if ruta:
            messagebox.showinfo("Ruta Óptima", f"Ruta: {' → '.join(ruta)}\nCosto: {costo:.2f}")
            self._mostrar_popup_grafo(ruta, estrategia)
        else:
            messagebox.showwarning("Sin Ruta", "No se encontró una ruta válida.")

    def _visualizar(self, ruta=None, estrategia=None):
        if self.canvas_frame:
            self.canvas_frame.destroy()

        self.canvas_frame = tk.Toplevel(self.root)
        self.canvas_frame.title("Visualización de Red")
        self.canvas_frame.geometry("900x600")

        self.red.visualizar_red(self.canvas_frame, ruta, estrategia)
    
    
    
    def _mostrar_popup_grafo(self, ruta, estrategia):
        ventana = tk.Toplevel(self.root)
        ventana.title("Visualización de Ruta Óptima")
        ventana.geometry("800x600")

        # Crear frame para el canvas
        frame_canvas = tk.Frame(ventana)
        frame_canvas.pack(fill="both", expand=True)

        # Visualizar red en ese frame
        self.red.visualizar_red(frame_canvas, ruta, estrategia)

