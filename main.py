import tkinter as tk
from tkinter import ttk
import PySpin as Ps
from ui_components.tkinter_form import Form
from api.Flea3Cam_API import Camera_PySpin
from api.multiespectral_iluminator import MultiSpectralIluminator
from methods.adquisition_functions import serial_port_select


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.form = None
        self.iluminator = None

        self.__create_widgets()

        init_camera = True
        if init_camera:
            system = Ps.System.GetInstance()
            cam_list = system.GetCameras()
            print(cam_list)
            self.camera = Camera_PySpin(cam_list[0])
            self.camera.Set_Trigger_Mode(True)

        else:
            self.camera = None

        self.mainloop()

    def __create_widgets(self):
        for index in range(3):
            tk.Grid.columnconfigure(self, index, weight=1)
        for index in range(3):
            tk.Grid.rowconfigure(self, index, weight=1)

        self.lb_port = ttk.Label(self, text="Puerto:")
        self.lb_port.grid(row=0, column=0)

        list_ports = serial_port_select(terminal=False)
        self.port_var = tk.StringVar()
        self.cb_port = ttk.Combobox(
            self, state="readonly", values=list_ports, textvariable=self.port_var
        )
        self.port_var.set(list_ports[0])
        self.cb_port.grid(row=0, column=1)

        self.bt_port = ttk.Button(
            self, text="Iniciar Corona", command=self.init_illuminator
        )
        self.bt_port.grid(row=0, column=2)

    def init_illuminator(self):
        """
        Open Illuminator
        """
        self.iluminator = MultiSpectralIluminator(self.port_var.get())

        struct = self.iluminator.get_config()

        self.form = Form(self, name_form="Iluminador multiespectral", form_dict=struct)

        renames = {
            "Tiempo de espera de comunicación": "Tiempo Comunicación",
            "__boards__": {
                "__form__": "Tarjetas",
                "BOARD 1": "Tarjeta 1",
                "BOARD 2": "Tarjeta 2",
                "BOARD 3": "Tarjeta 3",
                "BOARD 4": "Tarjeta 4",
            },
            "__wavelengths__": {"__form__": "Longitudes de onda"},
        }
        self.form.set_labels_text(renames)

        wavs = self.form.widgets["__boards__"]
        wavs.grid(row=5, column=0, columnspan=1, sticky="nesw")

        wavs = self.form.widgets["__wavelengths__"]
        wavs.grid(row=5, column=1, columnspan=1, sticky="nesw")

        pwm = self.form.widgets["__pwm__"]
        pwm.grid(row=6, column=0, columnspan=2, sticky="nesw")

        self.form.button.config(
            command=lambda: self.iluminator.set_config(self.form.get())
        )
        self.form.button.grid(row=7, column=0, columnspan=2, sticky="nesw")
        self.form.grid(row=1, column=0, columnspan=3, sticky="nesw")

        self.bt_port.config(state=tk.DISABLED)
        self.cb_port.config(state=tk.DISABLED)

        self.bt_capture = ttk.Button(
            self,
            text="Captura Multiespectral",
            command=self.multispectral_capture,
        )
        self.bt_capture.grid(row=2, column=0, columnspan=3, sticky="nesw")

    def multispectral_capture(self):
        num_images = self.iluminator.get_num_images()
        print(f"Numero imagenes: {num_images}")

        if self.camera:
            self.camera.Set_Trigger_Mode(False)
            if self.camera.Set_Buffer_Count(num_images):
                print("Error seteando Buffer Count")
                return
            self.camera.Set_Trigger_Mode(True)
            self.camera.Init_Acquisition()

        names = self.iluminator.multispectral_capture()

        if names is True:
            print("Error en la captura")
            return

        for name_image in names:
            print(name_image)
            if self.camera:
                self.camera.Acquire_Image(name_image)

        if self.camera:
            self.camera.End_Acquisition()


if __name__ == "__main__":
    App()
