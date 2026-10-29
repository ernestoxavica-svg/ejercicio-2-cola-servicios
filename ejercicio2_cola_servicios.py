# ejercicio2_cola_servicios.py
# Ejercicio 2: Colas de servicios para una compañía de seguros.
# Interfaz gráfica con Tkinter. No necesita comandos en la terminal.

import tkinter as tk
from tkinter import ttk, messagebox


# ---------------------------------------------------------------
# Clase Cola (FIFO)
# ---------------------------------------------------------------
class Cola:
    def __init__(self):
        self._items = []

    def encolar(self, elemento):
        """Agrega un elemento al final de la cola."""
        self._items.append(elemento)

    def desencolar(self):
        """Retira y devuelve el primer elemento, o None si está vacía."""
        if self.esta_vacia():
            return None
        return self._items.pop(0)

    def esta_vacia(self):
        return len(self._items) == 0

    def a_lista(self):
        """Devuelve una copia de los elementos en espera."""
        return list(self._items)


# ---------------------------------------------------------------
# Sistema de servicios
# ---------------------------------------------------------------
class SistemaServicios:
    def __init__(self):
        self.servicios = {}
        self.siguiente_id = 1

        for nombre in (
            "Pólizas nuevas",
            "Siniestros",
            "Pagos",
            "Cancelaciones",
        ):
            self.agregar_servicio(nombre)

    def agregar_servicio(self, nombre):
        nombre = nombre.strip()

        if not nombre:
            return None

        if any(
            servicio["nombre"].casefold() == nombre.casefold()
            for servicio in self.servicios.values()
        ):
            return None

        numero = self.siguiente_id
        self.servicios[numero] = {
            "nombre": nombre,
            "cola": Cola(),
            "contador": 0,
        }
        self.siguiente_id += 1
        return numero

    def llegada(self, numero):
        servicio = self.servicios[numero]
        servicio["contador"] += 1
        turno = servicio["contador"]
        servicio["cola"].encolar(turno)
        return turno

    def atencion(self, numero):
        return self.servicios[numero]["cola"].desencolar()


# ---------------------------------------------------------------
# Interfaz gráfica
# ---------------------------------------------------------------
class AplicacionServicios:
    def __init__(self, root):
        self.root = root
        self.sistema = SistemaServicios()

        self.root.title("Compañía de seguros | Sistema de atención")
        self.root.geometry("900x620")
        self.root.minsize(760, 540)
        self.root.configure(bg="#f3f5f8")

        self.estilo = ttk.Style()
        try:
            self.estilo.theme_use("clam")
        except tk.TclError:
            pass

        self.estilo.configure("TFrame", background="#f3f5f8")
        self.estilo.configure(
            "Titulo.TLabel",
            background="#17324d",
            foreground="white",
            font=("Segoe UI", 18, "bold"),
            padding=16,
        )
        self.estilo.configure(
            "Subtitulo.TLabel",
            background="#f3f5f8",
            foreground="#263746",
            font=("Segoe UI", 11, "bold"),
        )
        self.estilo.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=(10, 7),
        )
        self.estilo.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=28,
        )
        self.estilo.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
        )

        self.crear_interfaz()
        self.actualizar_servicios()
        self.actualizar_tabla()

    def crear_interfaz(self):
        encabezado = ttk.Label(
            self.root,
            text="SISTEMA DE ATENCIÓN — COMPAÑÍA DE SEGUROS",
            style="Titulo.TLabel",
            anchor="center",
        )
        encabezado.pack(fill="x")

        contenido = ttk.Frame(self.root, padding=18)
        contenido.pack(fill="both", expand=True)

        ttk.Label(
            contenido,
            text="Administración de clientes",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        controles = ttk.Frame(contenido)
        controles.pack(fill="x", pady=(0, 16))

        ttk.Label(
            controles,
            text="Servicio:",
        ).grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)

        self.servicio_seleccionado = tk.StringVar()
        self.combo_servicios = ttk.Combobox(
            controles,
            textvariable=self.servicio_seleccionado,
            state="readonly",
            width=32,
        )
        self.combo_servicios.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Button(
            controles,
            text="Registrar cliente",
            command=self.registrar_cliente,
        ).grid(row=0, column=2, padx=(10, 0), pady=5)

        ttk.Button(
            controles,
            text="Atender siguiente",
            command=self.atender_cliente,
        ).grid(row=0, column=3, padx=(8, 0), pady=5)

        controles.columnconfigure(1, weight=1)

        agregar = ttk.LabelFrame(
            contenido,
            text="Agregar un nuevo servicio",
            padding=10,
        )
        agregar.pack(fill="x", pady=(0, 16))

        self.entrada_servicio = ttk.Entry(agregar)
        self.entrada_servicio.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10),
        )
        self.entrada_servicio.insert(0, "")
        self.entrada_servicio.bind(
            "<Return>",
            lambda evento: self.agregar_servicio(),
        )

        ttk.Button(
            agregar,
            text="Crear servicio",
            command=self.agregar_servicio,
        ).pack(side="right")

        ttk.Label(
            contenido,
            text="Estado de las colas (los turnos se atienden en orden FIFO)",
            style="Subtitulo.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        columnas = ("numero", "servicio", "espera", "siguiente")
        self.tabla = ttk.Treeview(
            contenido,
            columns=columnas,
            show="headings",
            height=9,
        )
        self.tabla.heading("numero", text="N.º")
        self.tabla.heading("servicio", text="Servicio")
        self.tabla.heading("espera", text="Turnos en espera")
        self.tabla.heading("siguiente", text="Siguiente turno")

        self.tabla.column("numero", width=55, anchor="center")
        self.tabla.column("servicio", width=220)
        self.tabla.column("espera", width=330)
        self.tabla.column("siguiente", width=130, anchor="center")

        barra = ttk.Scrollbar(
            contenido,
            orient="vertical",
            command=self.tabla.yview,
        )
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="left", fill="y")

        inferior = ttk.Frame(contenido)
        inferior.pack(fill="x", pady=(12, 0))

        self.estado = tk.StringVar(value="Sistema listo.")
        ttk.Label(
            inferior,
            textvariable=self.estado,
            wraplength=650,
        ).pack(side="left", fill="x", expand=True)

        ttk.Button(
            inferior,
            text="Actualizar vista",
            command=self.actualizar_tabla,
        ).pack(side="right")

        historial_marco = ttk.LabelFrame(
            contenido,
            text="Historial de acciones",
            padding=8,
        )
        historial_marco.pack(fill="x", pady=(14, 0))

        self.historial = tk.Listbox(
            historial_marco,
            height=4,
            font=("Consolas", 9),
            activestyle="none",
        )
        self.historial.pack(fill="x")

    def actualizar_servicios(self):
        """Actualiza las opciones del menú desplegable."""
        opciones = [
            f'{numero} - {datos["nombre"]}'
            for numero, datos in self.sistema.servicios.items()
        ]
        seleccion_anterior = self.servicio_seleccionado.get()

        self.combo_servicios["values"] = opciones

        if seleccion_anterior in opciones:
            self.servicio_seleccionado.set(seleccion_anterior)
        elif opciones:
            self.combo_servicios.current(0)

    def obtener_numero_seleccionado(self):
        seleccion = self.servicio_seleccionado.get()

        if not seleccion:
            messagebox.showwarning(
                "Selecciona un servicio",
                "Primero selecciona el servicio donde deseas realizar la acción.",
            )
            return None

        try:
            return int(seleccion.split(" - ", 1)[0])
        except (ValueError, IndexError):
            messagebox.showerror(
                "Error",
                "No se pudo identificar el servicio seleccionado.",
            )
            return None

    def registrar_cliente(self):
        numero = self.obtener_numero_seleccionado()
        if numero is None:
            return

        turno = self.sistema.llegada(numero)
        nombre = self.sistema.servicios[numero]["nombre"]

        mensaje = f"Cliente registrado en {nombre}. Su turno es el número {turno}."
        self.estado.set(mensaje)
        self.agregar_al_historial(f"Llegada: Servicio {numero} ({nombre}), turno {turno}.")
        self.actualizar_tabla()

        messagebox.showinfo("Cliente registrado", mensaje)

    def atender_cliente(self):
        numero = self.obtener_numero_seleccionado()
        if numero is None:
            return

        turno = self.sistema.atencion(numero)
        nombre = self.sistema.servicios[numero]["nombre"]

        if turno is None:
            mensaje = f"No hay clientes esperando en {nombre}."
            self.estado.set(mensaje)
            self.agregar_al_historial(f"Atención: Servicio {numero} vacío.")
            messagebox.showinfo("Cola vacía", mensaje)
        else:
            mensaje = f"Se está atendiendo el turno {turno} de {nombre}."
            self.estado.set(mensaje)
            self.agregar_al_historial(f"Atención: Servicio {numero} ({nombre}), turno {turno}.")
            messagebox.showinfo("Atención de cliente", mensaje)

        self.actualizar_tabla()

    def agregar_servicio(self):
        nombre = self.entrada_servicio.get()
        numero = self.sistema.agregar_servicio(nombre)

        if numero is None:
            messagebox.showwarning(
                "No se creó el servicio",
                "Escribe un nombre y verifica que no exista otro servicio con ese nombre.",
            )
            self.entrada_servicio.focus_set()
            return

        nombre = nombre.strip()
        self.entrada_servicio.delete(0, tk.END)
        self.actualizar_servicios()
        self.servicio_seleccionado.set(f"{numero} - {nombre}")
        self.actualizar_tabla()

        mensaje = f"Se creó el servicio {numero}: {nombre}."
        self.estado.set(mensaje)
        self.agregar_al_historial(f"Nuevo servicio: {numero} - {nombre}.")
        messagebox.showinfo("Servicio creado", mensaje)

    def actualizar_tabla(self):
        for elemento in self.tabla.get_children():
            self.tabla.delete(elemento)

        for numero, datos in self.sistema.servicios.items():
            turnos = datos["cola"].a_lista()
            espera = ", ".join(map(str, turnos)) if turnos else "(vacía)"
            siguiente = str(turnos[0]) if turnos else "—"

            self.tabla.insert(
                "",
                "end",
                values=(
                    numero,
                    datos["nombre"],
                    espera,
                    siguiente,
                ),
            )

    def agregar_al_historial(self, mensaje):
        self.historial.insert(0, mensaje)
        # Mantiene el historial limitado a 100 acciones.
        while self.historial.size() > 100:
            self.historial.delete(tk.END)


def main():
    root = tk.Tk()
    AplicacionServicios(root)
    root.mainloop()


if __name__ == "__main__":
    main()
