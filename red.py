

import csv
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class NodoEnergia:
    def __init__(self, nombre, produccion, perdida, sostenibilidad):
        self.nombre = nombre
        self.produccion = float(produccion)
        self.perdida = float(perdida)
        self.sostenibilidad = float(sostenibilidad)

    def __str__(self):
        return f"{self.nombre} (Prod: {self.produccion}kW, Pérd: {self.perdida}%, Sost: {self.sostenibilidad})"


class RedEnergia:
    def __init__(self):
        self.nodos = {}
        self.conexiones = {}

    def agregar_nodo(self, nodo):
        self.nodos[nodo.nombre] = nodo
        if nodo.nombre not in self.conexiones:
            self.conexiones[nodo.nombre] = []

    def agregar_conexion(self, nodo1, nodo2):
        if nodo1 in self.nodos and nodo2 in self.nodos:
            if nodo2 not in self.conexiones[nodo1]:
                self.conexiones[nodo1].append(nodo2)
            if nodo1 not in self.conexiones[nodo2]:
                self.conexiones[nodo2].append(nodo1)

    def obtener_peso_arista(self, nodo1, nodo2, estrategia):
        n1 = self.nodos[nodo1]
        n2 = self.nodos[nodo2]

        if estrategia == "sostenibilidad":
            return 200 - (n1.sostenibilidad + n2.sostenibilidad) / 2
        elif estrategia == "perdida":
            return (n1.perdida + n2.perdida) / 2
        elif estrategia == "produccion":
            prod_total = n1.produccion + n2.produccion
            return 1000 / (prod_total + 1) if prod_total > 0 else 1000
        return 1

    def encontrar_ruta_optima(self, inicio, fin, estrategia):
        dist = {nodo: float("inf") for nodo in self.nodos}
        dist[inicio] = 0
        padre = {nodo: None for nodo in self.nodos}
        cola = [(0, inicio)]

        while cola:
            costo, actual = heapq.heappop(cola)
            if actual == fin:
                break
            for vecino in self.conexiones[actual]:
                peso = self.obtener_peso_arista(actual, vecino, estrategia)
                nuevo_costo = costo + peso
                if nuevo_costo < dist[vecino]:
                    dist[vecino] = nuevo_costo
                    padre[vecino] = actual
                    heapq.heappush(cola, (nuevo_costo, vecino))

        if dist[fin] == float("inf"):
            return None, None

        ruta = []
        nodo = fin
        while nodo:
            ruta.append(nodo)
            nodo = padre[nodo]
        ruta.reverse()
        return ruta, dist[fin]

    def cargar_desde_csv(self, archivo_nodos, archivo_conexiones):
        self.nodos = {}
        self.conexiones = {}

        with open(archivo_nodos, "r", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                nodo = NodoEnergia(fila["Nombre"], fila["Produccion"], fila["Pérdida"], fila["Sostenibilidad"])
                self.agregar_nodo(nodo)

        with open(archivo_conexiones, "r", encoding="utf-8") as f:
            lector = csv.reader(f)
            nombres = next(lector)[1:]
            for fila in lector:
                origen = fila[0]
                for i, val in enumerate(fila[1:]):
                    if val == "1":
                        self.agregar_conexion(origen, nombres[i])
        return True

    def visualizar_red(self, canvas_widget=None, ruta_optima=None, estrategia=None):
        G = nx.Graph()
        for nombre, nodo in self.nodos.items():
            G.add_node(nombre)
        for nodo, vecinos in self.conexiones.items():
            for vecino in vecinos:
                peso = self.obtener_peso_arista(nodo, vecino, estrategia) if estrategia else 1
                G.add_edge(nodo, vecino, weight=peso)

        plt.clf()
        fig = plt.figure(figsize=(10, 7))
        pos = nx.kamada_kawai_layout(G)
        colores = []
        for nodo in G.nodes:
            n = self.nodos[nodo]
            if n.produccion > 0:
                colores.append("green")
            elif "Residencial" in nodo:
                colores.append("red")
            elif "Almacenamiento" in nodo:
                colores.append("blue")
            elif "Subestacion" in nodo:
                colores.append("orange")
            else:
                colores.append("gray")

        nx.draw(G, pos, with_labels=True, node_color=colores, node_size=700)
        if estrategia:
            edge_labels = {(u, v): f"{G[u][v]['weight']:.1f}" for u, v in G.edges()}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        if ruta_optima:
            edges_ruta = [(ruta_optima[i], ruta_optima[i+1]) for i in range(len(ruta_optima)-1)]
            nx.draw_networkx_edges(G, pos, edgelist=edges_ruta, edge_color="red", width=3)

        if canvas_widget:
            canvas = FigureCanvasTkAgg(fig, master=canvas_widget)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            return canvas
        else:
            plt.show()
