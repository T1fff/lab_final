import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import heapq

# -------------------------------
# MODELO DE DATOS
# -------------------------------

class NodoEnergia:
    def __init__(self, nombre, produccion, perdida, sostenibilidad):
        self.nombre = nombre
        self.produccion = float(produccion)
        self.perdida = float(perdida)
        self.sostenibilidad = float(sostenibilidad)

class RedEnergia:
    def __init__(self):
        self.nodos = {}  # nombre -> NodoEnergia
        self.grafo = {}  # nombre -> [vecinos]
        self.estrategia = "perdida"

    def cargar_nodos(self, path):
        self.nodos.clear()
        with open(path, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                nodo = NodoEnergia(row["Nombre"], row["Produccion"], row["Pérdida"], row["Sostenibilidad"])
                self.nodos[nodo.nombre] = nodo
        print(f"[INFO] Cargados {len(self.nodos)} nodos")

    def cargar_adyacencia(self, path):
        self.grafo.clear()
        with open(path, newline='') as file:
            reader = csv.reader(file)
            headers = next(reader)
            matrix = list(reader)

        for i, row in enumerate(matrix):
            nodo_origen = row[0]
            self.grafo[nodo_origen] = []
            for j, val in enumerate(row[1:]):
                if int(val) == 1:
                    self.grafo[nodo_origen].append(headers[j + 1])
        print("[INFO] Grafo cargado correctamente")

    def establecer_estrategia(self, estrategia):
        if estrategia in ["perdida", "sostenibilidad", "produccion"]:
            self.estrategia = estrategia
        else:
            raise ValueError("Estrategia inválida")

    def _peso_arista(self, nodo_actual, vecino):
        n1 = self.nodos[nodo_actual]
        n2 = self.nodos[vecino]
        if self.estrategia == "perdida":
            return (n1.perdida + n2.perdida) / 2
        elif self.estrategia == "sostenibilidad":
            return 100 - ((n1.sostenibilidad + n2.sostenibilidad) / 2)
        elif self.estrategia == "produccion":
            return -(n1.produccion + n2.produccion) / 2  # Negativo para maximizar

    def camino_optimo(self, origen, destino):
        if origen not in self.grafo or destino not in self.grafo:
            raise ValueError("Nodo de origen o destino no existe")

        heap = [(0, origen, [])]
        visitados = set()

        while heap:
            costo, actual, camino = heapq.heappop(heap)
            if actual in visitados:
                continue
            camino = camino + [actual]
            if actual == destino:
                return camino, costo
            visitados.add(actual)

            for vecino in self.grafo.get(actual, []):
                if vecino not in visitados:
                    peso = self._peso_arista(actual, vecino)
                    heapq.heappush(heap, (costo + peso, vecino, camino))
        return None, float('inf')

# -------------------------------
# INTERFAZ GRÁFICA
# -------------------------------

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Red Energética Sostenible")
        self.red = RedEnergia()

        # Archivos
        self.btn_nodos = tk.Button(root, text="Cargar Nodos CSV", command=self.cargar_nodos)
        self.btn_matriz = tk.Button(root, text="Cargar Matriz Adyacencia CSV", command=self.cargar_matriz)
        self.btn_nodos.pack(pady=5)
        self.btn_matriz.pack(pady=5)

        # Estrategia
        self.var_estrategia = tk.StringVar(value="perdida")
        tk.Label(root, text="Estrategia:").pack()
        opciones = ["perdida", "sostenibilidad", "produccion"]
        for op in opciones:
            tk.Radiobutton(root, text=op.capitalize(), variable=self.var_estrategia, value=op).pack(anchor='w')

        # Selección de nodos
        self.origen = tk.StringVar()
        self.destino = tk.StringVar()
        tk.Label(root, text="Origen:").pack()
        self.entry_origen = tk.Entry(root, textvariable=self.origen)
        self.entry_origen.pack()
        tk.Label(root, text="Destino:").pack()
        self.entry_destino = tk.Entry(root, textvariable=self.destino)
        self.entry_destino.pack()

        self.btn_calcular = tk.Button(root, text="Calcular Ruta Óptima", command=self.calcular_ruta)
        self.btn_calcular.pack(pady=10)

        self.text_resultado = tk.Text(root, height=10, width=60)
        self.text_resultado.pack()

    def cargar_nodos(self):
        path = filedialog.askopenfilename(title="Seleccionar CSV de Nodos")
        if path:
            try:
                self.red.cargar_nodos(path)
                messagebox.showinfo("Éxito", "Nodos cargados correctamente.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def cargar_matriz(self):
        path = filedialog.askopenfilename(title="Seleccionar CSV de Matriz")
        if path:
            try:
                self.red.cargar_adyacencia(path)
                messagebox.showinfo("Éxito", "Matriz cargada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def calcular_ruta(self):
        origen = self.origen.get()
        destino = self.destino.get()
        estrategia = self.var_estrategia.get()
        try:
            self.red.establecer_estrategia(estrategia)
            camino, costo = self.red.camino_optimo(origen, destino)
            if camino:
                self.text_resultado.delete("1.0", tk.END)
                self.text_resultado.insert(tk.END, f"Estrategia: {estrategia}\n")
                self.text_resultado.insert(tk.END, f"Camino: {' -> '.join(camino)}\n")
                self.text_resultado.insert(tk.END, f"Costo total: {costo:.2f}\n")
            else:
                self.text_resultado.insert(tk.END, "No se encontró camino.\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# -------------------------------
# EJECUCIÓN
# -------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()