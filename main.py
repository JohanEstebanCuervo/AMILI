"""
AMILI
Adcquisition MultiSpectral Images with Ilumination Led
"""
import os
from datetime import datetime
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd
import PySpin as Ps
import cv2

from ui_components.tkinter_form import Form
from ui_components.tkinter_form_dialog import form_dialog
from ui_components.multiespectral_visualizer import MultiSpectralVisualizer
from api.Flea3Cam_API import Camera_PySpin
from api.multiespectral_iluminator import MultiSpectralIluminator
from methods.adquisition_functions import serial_port_select
from methods.recognition import check_median, detect_spectralon
from methods.color_checker_detection import color_checker_detection
from methods.dictionary import compare_dicts


class App(tk.Tk):
    """
    Main App
    """

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

        self.fm_control = ttk.Frame(self)

        self.bt_capture = ttk.Button(
            self.fm_control,
            text="Captura Multiespectral",
            command=lambda: self.multispectral_capture(True),
        )
        self.bt_capture.pack(side="top", fill="both", expand=1)

        self.bt_calibrate_spectralon = ttk.Button(
            self.fm_control,
            text="Calibrar Reflactante",
            command=self.command_bt_calibrate_spectralon,
        )
        self.bt_calibrate_spectralon.pack(side="left", fill="both", expand=1)

        self.bt_calibrate_white = ttk.Button(
            self.fm_control,
            text="Calibrar Color Checker",
            command=self.command_bt_calibrate_white,
        )
        self.bt_calibrate_white.pack(side="left", fill="both", expand=1)

        self.charge_duty = ttk.Button(
            self.fm_control, text="Cargar PWM", command=self.command_charge_duty
        )
        self.charge_duty.pack(side="left", fill="both", expand=1)

        self.bt_save_duty = ttk.Button(
            self.fm_control, text="Guardar PWM", command=self.command_save_duty
        )
        self.bt_save_duty.pack(side="left", fill="both", expand=1)

        self.bt_rep_cap = ttk.Button(
            self.fm_control, text="Repetibilidad", command=self.command_bt_rep_cap
        )
        self.bt_rep_cap.pack(side="left", fill="both", expand=1)

    def __compare_form(self):
        """
        Compara si se han realizado cambios en el formulario
        de entrada y estos no han sido guardados
        """
        dict1 = self.iluminator.get_config()
        dict2 = self.form.get()

        if compare_dicts(dict1, dict2):
            return

        res = messagebox.askyesno(
            "Configuración No Actualizada",
            "No se han realizado los cambios en el iluminador multiespectral ¿Desea Realizarlos?",
        )

        if res is True:
            self.iluminator.set_config(dict2)

        else:
            self.form.set(dict1)

    def command_bt_rep_cap(self):
        """
        Realiza N capturas iguales
        """
        self.__compare_form()

        struct = {
            "Número de capturas: ": 15,
        }

        result = form_dialog(struct, self, "aceptar")

        value = result["Número de capturas: "]
        if value <= 0 or value > 100:
            return

        for _ in range(value):
            self.multispectral_capture()
            now = datetime.now()
            date = (
                f"{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}"
            )
            folder = f"imgs/{date}"
            os.mkdir(folder)
            for name_image in os.listdir("./temp"):
                original = "temp/" + name_image
                target = folder + "/" + name_image
                shutil.move(original, target)

    def command_bt_calibrate_white(self, num_patch: int = 19, ideal_value: int = 243):
        """
        Calibra valores de pwm para la color_checker
        """
        config = self.form.get()

        keys = ["__boards__", "__pwm__", "__wavelengths__", "Captura por board"]
        values = map(config.get, keys)
        config = dict(zip(keys, values))

        mask = None
        for board in config["__pwm__"].columns.values.tolist():
            if board == "Multiple_Board":
                config["__boards__"] = dict(
                    zip(config["__boards__"], [True] * len(config["__boards__"]))
                )
                config["Captura por board"] = False
            else:
                break  # Comentar para que calibre los demas
                config["__boards__"] = dict(
                    zip(config["__boards__"], [False] * len(config["__boards__"]))
                )
                config["__boards__"][board] = True
                config["Captura por board"] = True

            for wav in config["__wavelengths__"]:
                config["__wavelengths__"] = dict(
                    zip(
                        config["__wavelengths__"],
                        [False] * len(config["__wavelengths__"]),
                    )
                )
                config["__wavelengths__"][wav] = True

                searching_value = True
                checked_led_pwm = 100
                delta_pwm = 10
                while searching_value is True:
                    if checked_led_pwm > 100:
                        # configure_single_LED(comunicacion, led , list_led_duty_values[0] )
                        checked_led_pwm = 100
                        break
                    config["__pwm__"].loc[wav][board] = checked_led_pwm

                    self.form.set(config)
                    self.update()
                    if self.iluminator.set_config(config):
                        raise ValueError("Error seteando el iluminador")

                    self.multispectral_capture()

                    path_image = "temp/" + os.listdir("temp")[0]

                    if mask is None:
                        image = cv2.imread(path_image, cv2.IMREAD_GRAYSCALE)
                        mask = color_checker_detection([image], "end")[num_patch - 1]

                    median = check_median(path_image, mask, ideal_value=ideal_value)

                    print(f"The median value is: {median}")
                    if median < ideal_value and delta_pwm == 1:
                        searching_value = False
                        print(f"The final value is {checked_led_pwm}")

                    elif median < ideal_value and delta_pwm == 10:
                        checked_led_pwm += 9
                        delta_pwm = 1

                        if checked_led_pwm > 100:
                            searching_value = False
                            print(f"The final value is {checked_led_pwm}")
                    else:
                        checked_led_pwm -= delta_pwm

    def command_bt_calibrate_spectralon(self, ideal_value: float = 252.45):
        """
        Calibra valores de pwm para el spectralon
        """
        if ideal_value > 255 or ideal_value < 0:
            raise ValueError(
                f"El valor de calibración debe estar entre 0 y 255. Valor: {ideal_value}"
            )

        config = self.form.get()

        keys = ["__boards__", "__pwm__", "__wavelengths__", "Captura por board"]
        values = map(config.get, keys)
        config = dict(zip(keys, values))

        mask = None
        for board in config["__pwm__"].columns.values.tolist():
            if board == "Multiple_Board":
                config["__boards__"] = dict(
                    zip(config["__boards__"], [True] * len(config["__boards__"]))
                )
                config["Captura por board"] = False
            else:
                break  # Comentar para que calibre los demas
                config["__boards__"] = dict(
                    zip(config["__boards__"], [False] * len(config["__boards__"]))
                )
                config["__boards__"][board] = True
                config["Captura por board"] = True

            for wav in config["__wavelengths__"]:
                config["__wavelengths__"] = dict(
                    zip(
                        config["__wavelengths__"],
                        [False] * len(config["__wavelengths__"]),
                    )
                )
                config["__wavelengths__"][wav] = True

                searching_value = True
                checked_led_pwm = 100
                delta_pwm = 10
                while searching_value is True:
                    if checked_led_pwm > 100:
                        checked_led_pwm = 100
                        break
                    config["__pwm__"].loc[wav][board] = checked_led_pwm

                    self.form.set(config)
                    self.update()
                    if self.iluminator.set_config(config):
                        raise ValueError("Error seteando el iluminador")

                    self.multispectral_capture()

                    path_image = "temp/" + os.listdir("temp")[0]

                    if mask is None:
                        mask = detect_spectralon(path_image, "end")

                    median = check_median(path_image, mask, ideal_value)

                    print(f"The median value is: {median}")
                    if median < ideal_value and delta_pwm == 1:
                        searching_value = False
                        print(f"The final value is {checked_led_pwm}")

                    elif median < ideal_value and delta_pwm == 10:
                        checked_led_pwm += 9
                        delta_pwm = 1

                        if checked_led_pwm > 100:
                            searching_value = False
                            print(f"The final value is {checked_led_pwm}")
                    else:
                        checked_led_pwm -= delta_pwm

    def command_charge_duty(self):
        """
        cargar pwms
        """
        path = filedialog.askopenfilename(
            title="Cargar PWM", defaultextension="csv", filetypes=[("csv file", ".csv")]
        )

        data_frame = pd.read_csv(path, index_col=0)

        conf = {"__pwm__": data_frame}

        self.form.set(conf)

    def command_save_duty(self):
        """
        Guarda los PWM en formato csv
        """
        path = filedialog.asksaveasfilename(
            title="Guardar PWM",
            defaultextension="csv",
            filetypes=[("csv file", ".csv")],
        )

        if path == "":
            return

        data_pwm = self.form.get()["__pwm__"]

        data_pwm.to_csv(path)

    def init_illuminator(self):
        """
        Open Illuminator
        """
        self.iluminator = MultiSpectralIluminator(self.port_var.get())

        struct = self.iluminator.get_config()

        self.form = Form(self, name_form="Iluminador multiespectral", form_dict=struct)

        renames = {
            "Tiempo de espera de comunicación": "Tiempo Comunicación (S)",
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

        # angle = self.form.widgets["__angle__"]
        # angle.grid(row=5, column=2, columnspan=1, sticky="nesw")

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

        self.fm_control.grid(row=3, column=0, columnspan=3, sticky="nesw")

    def multispectral_capture(self, visualizer: bool = False):
        """
        Capture MultiSpectral Images
        """
        self.__compare_form()

        for ima in os.listdir("temp"):
            os.remove(f"temp/{ima}")

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

        if visualizer is True:
            MultiSpectralVisualizer(self, "temp")


if __name__ == "__main__":
    App()
