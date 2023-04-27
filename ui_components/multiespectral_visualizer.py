"""
Modulo Para visualizar imagenes multiespectrales mediante una tkinter.Toplevel
y el modulo matplotlib
"""
import os
import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure
import cv2
import numpy as np


class MultiSpectralVisualizer(tk.Toplevel):
    """
    Clase para visualizar imagenes multiespectrales
    """

    def __init__(self, master, path: str = None):
        super().__init__(master=master)

        self.title("Visualizador de Captura")
        self.images = []
        self.names_images = []
        self.index = 0
        self.__create_widgets()

        if path is not None:
            self.command_bt_charge_capture(path)

        self.attributes("-topmost", True)
        self.mainloop()

    def __create_widgets(self):
        """
        Create Widgets Windows Visualization
        """
        self.mp_figure = Figure(figsize=(5, 4), dpi=100)
        self.mp_axes = self.mp_figure.add_subplot(111)
        self.mp_figure.subplots_adjust(0, 0, 1, 1, 0, 0)
        self.mp_axes.axis("off")
        self.fg_canvas = FigureCanvasTkAgg(self.mp_figure, master=self)
        self.tk_canvas = self.fg_canvas.get_tk_widget()

        self.mp_toolbar = NavigationToolbar2Tk(self.fg_canvas, self)
        self.mp_toolbar.pack_forget()
        self.mp_toolbar.pack(side="top", fill="both")
        self.tk_canvas.pack(side="top", fill="both", expand=1)
        self.mp_toolbar.update()

        self.save_button = self.mp_toolbar.children["!button5"]
        self.save_button.config(command=self.command_save_capture)
        self.mp_toolbar.children["!button4"].pack_forget()

        self.lb_name_imag = tk.Label(self.mp_toolbar, text="Nombre Imagen")
        self.lb_name_imag.pack(side="left", fill="both", expand=1)

        self.fr_control_buttons = tk.Frame(self)
        self.fr_control_buttons.pack(side="bottom", fill="both")

        self.bt_charge_capture = tk.Button(
            self.fr_control_buttons,
            text="Cargar Captura",
            command=self.command_bt_charge_capture,
        )
        self.bt_charge_capture.pack(side="left", fill="both", expand=1)

        self.bt_next_image = tk.Button(
            self.fr_control_buttons,
            text="Siguiente Imagen",
            command=lambda: self.charge_image(self.index + 1),
        )
        self.bt_next_image.pack(side="left", fill="both", expand=1)

        self.bt_after_image = tk.Button(
            self.fr_control_buttons,
            text="Anterior Imagen",
            command=lambda: self.charge_image(self.index - 1),
        )
        self.bt_after_image.pack(side="left", fill="both", expand=1)

    def command_save_capture(self):
        """
        Save MultiEspectral Capture
        """
        cant_imag = len(self.images)
        if cant_imag == 0:
            return

        self.attributes("-topmost", False)
        path = filedialog.askdirectory(master=self, title="Carpeta de la captura")
        self.attributes("-topmost", True)
        if path == "":
            return

        for index, name_image in enumerate(self.names_images):
            path_file = os.path.join(path, name_image)
            cv2.imwrite(path_file, np.flip(self.images[index], axis=2))

    def command_bt_charge_capture(self, path: str = None):
        """
        Carga una captura Multiespectral
        """
        if path is None:
            self.attributes("-topmost", False)
            path = filedialog.askdirectory(master=self, title="Carpeta de la captura")
            self.attributes("-topmost", True)

        if path == "":
            return

        self.mp_axes.clear()
        self.mp_axes.axis("off")
        self.fg_canvas.draw()
        self.lb_name_imag["text"] = ""
        self.mp_toolbar.update()

        self.images = []
        self.names_images = []
        for image_name in os.listdir(path):
            image = cv2.imread(os.path.join(path, image_name))

            if not np.shape(image):
                continue

            if len(np.shape(image)) == 3:
                image = np.flip(image, axis=2)

            self.images.append(image)
            self.names_images.append(image_name)

        self.charge_image(0)

    def charge_image(self, index):
        """
        Carga la imagen en el visualizador de acuerdo a la lista
        de imagenes y un indice
        """
        cant_imag = len(self.images)
        if cant_imag == 0:
            return

        if index >= cant_imag:
            index = 0

        elif index < 0:
            index = cant_imag - 1

        self.mp_axes.clear()
        self.mp_axes.imshow(self.images[index], vmin=0, vmax=255)
        self.mp_axes.axis("off")
        self.fg_canvas.draw()
        self.lb_name_imag["text"] = self.names_images[index]
        self.mp_toolbar.update()

        self.index = index


if __name__ == "__main__":
    MultiSpectralVisualizer(None, "temp")
