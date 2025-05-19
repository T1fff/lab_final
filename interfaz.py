
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from red import RedEnergia

class AplicacionRed:
    def __init__(self, root):
        self.root = root
        self.root.title("Red de Energía Renovable")
        self.red = RedEnergia()
        self.canvas_frame = None
        self.ruta_nodos = tk.StringVar()
        self.ruta_conexiones = tk.StringVar()
        self.nodo_inicio = tk.StringVar()
        self.nodo_fin = tk.StringVar()
        self.estrategia = tk.StringVar(value="sostenibilidad")
        self._crear_interfaz()

    def _crear_interfaz(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Archivo de Nodos CSV").pack()
        ttk.Entry(frame, textvariable=self.ruta_nodos, width=50).pack()
        ttk.Button(frame, text="Seleccionar", command=self._cargar_nodos).pack()

        ttk.Label(frame, text="Archivo de Conexiones CSV").pack()
        ttk.Entry(frame, textvariable=self.ruta_conexiones, width=50).pack()
        ttk.Button(frame, text="Seleccionar", command=self._cargar_conexiones).pack()

        ttk.Button(frame, text="Cargar Red", command=self._cargar_red).pack(pady=10)

        ttk.Label(frame, text="Nodo Inicio").pack()
        self.combo_inicio = ttk.Combobox(frame, textvariable=self.nodo_inicio)
        self.combo_inicio.pack()

        ttk.Label(frame, text="Nodo Fin").pack()
        self.combo_fin = ttk.Combobox(frame, textvariable=self.nodo_fin)
        self.combo_fin.pack()

        ttk.Label(frame, text="Estrategia").pack()
        for val in ["sostenibilidad", "perdida", "produccion"]:
            ttk.Radiobutton(frame, text=val.capitalize(), value=val, variable=self.estrategia).pack(anchor="w")

        ttk.Button(frame, text="Calcular Ruta Óptima", command=self._calcular_ruta).pack(pady=10)

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill="both", expand=True)

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
            self._visualizar(ruta, estrategia)
        else:
            messagebox.showwarning("Sin Ruta", "No se encontró una ruta válida.")

    def _visualizar(self, ruta=None, estrategia=None):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        self.red.visualizar_red(self.canvas_frame, ruta, estrategia)
