"""
Programmed By: Johan Esteban Cuervo Chica

Este Modulo provee de una API para un iluminar led_multiespectral.
"""
import time
import json
from copy import deepcopy
import serial
import pandas as pd


class MultiSpectralIluminator:
    """
    Class provied API configuration multiespectral iluminator
    """

    def __init__(
        self,
        puerto: str,
        bps: int = 115200,
        time_sleep_c: int = 1,
        time_exposure: int = 1000,
        time_led_on: int = 200,
        num_flash: int = 3,
        virtual_mode: bool = False,
    ):
        print("Iniciando Corona_Multiespectral")

        self.wavelengths = {
            "451 nm": "1",
            "500 nm": "7",
            "525 nm": "5",
            "550 nm": "8",
            "620 nm": "4",
            "660 nm": "3",
            "740 nm": "6",
            "850 nm": "2",
        }
        self.__config_functions = {
            "Tiempo de espera de comunicación": self.set_time_sleepc,
            "Tiempo de exposición": self.set_time_exposure,
            "Tiempo de led encendido": self.set_time_led_on,
            "Número de flash": self.set_num_flash,
            "Captura por board": self.set_capture_board,
            "__boards__": self.set_boards,
            "__wavelengths__": self.set_wavelengths,
            "__pwm__": self.set_pwm,
            "__angle__": self.set_angle,
        }
        self.__correct_tx = b"ACK-END\n"
        self.__comunication_state = False
        self.__timesleepc = time_sleep_c
        self.__num_images = 0
        try:
            self.__comunication = serial.Serial(puerto, bps)
            self.__comunication_state = True

        except serial.SerialException:
            if not virtual_mode:
                print("No se ejecuto el puerto serial")

        wavelengths = list(self.wavelengths.keys())
        wav_dict = dict(zip(wavelengths, [True] * len(wavelengths)))

        boards = self.get_boards()
        pwm_values = [[100] * (len(boards)+1)] * len(wavelengths)
        pwm_boards = list(boards)
        pwm_boards.insert(0, 'Multiple_Board')

        pwm_table = pd.DataFrame(pwm_values, index=wavelengths, columns=pwm_boards)

        angles = dict(zip(boards, [90] * len(boards)))
        self.__config_set = {
            "Tiempo de espera de comunicación": time_sleep_c,
            "Tiempo de exposición": time_exposure,
            "Tiempo de led encendido": time_led_on,
            "Número de flash": num_flash,
            "Captura por board": False,
            "__boards__": boards,
            "__wavelengths__": wav_dict,
            "__pwm__": pwm_table,
            #      "__angle__": angles,
        }

        if self.set_config(self.__config_set):
            print("Error Inicializando Corona")
            return

        print("Corona iniciada correctamente")

    def set_angle(self, angles: dict) -> bool:
        """
        Configura el angulo de las boards

        Args:
            angles (dict): diccionario con los angulos a setear

        Returns:
            bool: True en caso de error False si todo Ok
        """
        for board, angle in angles.items():
            angle = int(angle)
            if angle < 45 or angle > 150:
                return True
            if board not in self.__config_set["__angle__"]:
                return True

            message = "{" + f"ID:{int(board[-1]) - 1},ANGLE:{angle}" + "}"
            if self.tx_msg(message, False):
                return True
            time.sleep(0.3)

            self.__config_set["__angle__"][board] = angle

        return False

    def set_pwm(self, table: pd.DataFrame) -> bool:
        """
        Configura el pwm de las boards

        Args:
            table (pd.DataFrame): table with PWM

        Returns:
            bool: True en caso de error False si todo Ok
        """

        for wave, row_values in table.iterrows():
            for value in row_values:
                pwm_val = int(value)

                if pwm_val < 0 or pwm_val > 100:
                    return True

            if wave not in self.__config_set["__pwm__"].index:
                return True

        self.__config_set["__pwm__"] = table

        return False

    def set_wavelengths(self, value: dict) -> bool:
        """
        Configura el estado de las longitudes de onda activandolas o
        desactivandolas para realizar la captura multiespectral

        Args:
            value (dict): {'wavelenth_name': bool}

        Returns:
            bool: True en caso de error False si todo Ok
        """

        for wave, state in value.items():
            state = bool(state)
            if wave in self.__config_set["__wavelengths__"]:
                self.__config_set["__wavelengths__"][wave] = state

            else:
                return True

        return False

    def set_boards(self, value: dict) -> bool:
        """
        Configura el estado de las boards activandolas o
        desactivandolas para realizar la captura multiespectral

        Args:
            value (dict): {'BOARD ID': bool}

        Returns:
            bool: True en caso de error False si todo Ok
        """

        for board, state in value.items():
            state = bool(state)
            if board in self.__config_set["__boards__"]:
                self.__config_set["__boards__"][board] = state

            else:
                return True

        return False

    def set_capture_board(self, value: bool) -> bool:
        """
        Setea el tipo de captura multiespectral
        Args:
            value (bool): True Captura por cada boar, False Todas las boards
                activas al mismo tiempo

        Returns:
            bool: True en caso de error False si todo Ok
        """
        value = bool(value)
        self.__config_set["Captura por board"] = value

        return False

    def set_num_flash(self, value: int) -> bool:
        """
        Setea el número de flashes
        Args:
            value (int): Tiempo en milisegundos

        Returns:
            bool: True en caso de error False si todo Ok
        """
        value = int(value)

        message = "{" + f"FLASH:{value}" + "}"

        if self.tx_msg(message, False):
            return True

        self.__config_set["Número de flash"] = value
        return False

    def set_time_led_on(self, value: int) -> bool:
        """
        Setea el tiempo En el que los leds estan On en un Flash time.
        Args:
            value (int): Tiempo en milisegundos

        Returns:
            bool: True en caso de error False si todo Ok
        """
        value = int(value)

        message = "{" + f"TL:{value}" + "}"

        if self.tx_msg(message, False):
            return True

        self.__config_set["Tiempo de led encendido"] = value
        return False

    def set_time_exposure(self, value: int) -> bool:
        """
        Setea el tiempo de opturación o trigger del iluminador.
        Args:
            value (int): Tiempo en milisegundos

        Returns:
            bool: True en caso de error False si todo Ok
        """
        value = int(value)

        message = "{" + f"TO:{value}" + "}"

        if self.tx_msg(message, False):
            return True

        self.__config_set["Tiempo de exposición"] = value
        return False

    def set_time_sleepc(self, time_c: int) -> bool:
        """
        Cambia el tiempo de espera en la comunicación

        Args:
            time (int): Nuevo Tiempo

        Returns:
            bool: True en caso de error False si todo Ok
        """
        time_c = int(time_c)
        self.__config_set["Tiempo de espera de comunicación"] = time_c
        self.__timesleepc = time_c

        return False

    def __set_num_images(self) -> bool:
        if self.__config_set["Captura por board"]:
            wav = sum(self.__config_set["__wavelengths__"].values())
            board = sum(self.__config_set["__boards__"].values())

            self.__num_images = wav * board

        else:
            self.__num_images = sum(self.__config_set["__wavelengths__"].values())

        return False

    def get_num_images(self) -> int:
        """
        Muestra el número de imagenes a capturar

        Returns:
            int: Número de imagenes
        """
        return self.__num_images

    def get_boards(self) -> dict:
        """
        Busca las boards conectadas al sistema multiespectral

        Returns:
            dict: con las boards
        """
        if self.tx_msg("{SCAN}", comp=False):
            return
        time.sleep(0.5)

        boards = None
        while self.__comunication.in_waiting > 0:
            boards = self.__comunication.readline()

        if boards is None:
            boards = "{BD:0}"

        print(boards)
        boards = {"BOARD 1": True, "BOARD 2": True, "BOARD 3": True, "BOARD 4": True}

        return boards

    def get_comunication_state(self) -> bool:
        """
        Muestra el estado actual de comunicación si es True
        Todo esta correcto por el momento

        Returns:
            bool: Estado de comunicación
        """
        return self.__comunication_state

    def get_config(self) -> dict:
        """
        Muestra la configuración de la corona

        Returns:
            dict: Diccionario con la configuración
        """

        return deepcopy(self.__config_set)

    def set_config(self, config: dict) -> bool:
        """
        Setea la configuración del iluminador multiespectral

        Se debe enviar la misma estructura que entrega el metodo
        self.get_config()

        Args:
            config (dict): diccionario con la configuración a setear

        Returns:
            bool: True en caso de error False si todo Ok
        """

        for attrib, value in config.items():
            if attrib not in self.__config_functions:
                print(f"Atributo no existente: {attrib}")
                return True

            self.__config_functions[attrib](value)

        self.__set_num_images()

        return False

    def set_correct_tx(self, val: str) -> None:
        """
        Cambia el mensaje para verificar una transmisión correcta

        Args:
            val (str): mensaje ok
        """
        self.__correct_tx = val.encode("utf-8")

    def tx_msg(self, message: str, comp: bool = True, time_sleep: int = None) -> bool:
        """
        Envia un mensaje al iluminador multiespectral. Si la comprobación es True
        comprueba que se reciba la respuesta del atributo self.__correct_tx

        Args:
            message (str): mensaje a enviar string
            comp (bool, optional): Comprobar respuesta de la corona. Defaults to True.

        Returns:
            bool: True en caso que la tranmisión falle, False en caso que funcione correctamente
        """
        print(message)
        if time_sleep is None:
            time_sleep = self.__timesleepc

        if not self.__comunication_state:
            print("Comunicación no iniciada No es posible enviar el mensaje")
            return False

        bandera = False
        # Si no se necesita comprobacion solo ingresa al while 1 vez

        try:
            self.__comunication.write(message.encode("utf-8"))

            if comp:
                time.sleep(time_sleep)

                check = b""

                while self.__comunication.in_waiting > 0:
                    check = self.__comunication.readline()

                if check == self.__correct_tx:
                    bandera = True

        except serial.SerialException:
            print("error en la comunicacion serial")
            self.__comunication_state = False
            return True

        if bandera is False and comp:
            print(f"Comunicación no correcta mensaje recibido: {check.decode('utf-8')}")
            return True

        return False

    def multispectral_capture(self) -> list:
        """
        Realiza la captura multiespectral de acuerdo a la configuración de la corona.

        Returns:
            bool: True en caso que la captura fracase, list names images si todo ok
        """
        time_sleep = (
            self.__config_set["Tiempo de exposición"] / 1000
            + self.__config_set["Tiempo de espera de comunicación"]
        )
        name_capture = []
        if self.__config_set["Captura por board"] is False:
            id_boards = ""
            id_name = "bd_"
            for board, state in self.__config_set["__boards__"].items():
                if state:
                    if id_boards != "":
                        id_boards += ","

                    id_b = int(board[-1]) - 1
                    id_boards += f"ID:{id_b}"
                    id_name += f"{id_b}"

            column = 'Multiple_Board'
            for wav, state in self.__config_set["__wavelengths__"].items():
                if not state:
                    continue

                led_id = f"LED:{self.wavelengths[wav]}"
                duty = f'DUTY:{self.__config_set["__pwm__"].loc[wav, column]}'

                message = "{" + f"{id_boards},{led_id},{duty},START" + "}"
                name_capture.append(f"{id_name}_{wav}")
                if self.tx_msg(message, time_sleep=time_sleep):
                    return True

            return name_capture

        for board, state in self.__config_set["__boards__"].items():
            if not state:
                continue

            id_b = int(board[-1]) - 1
            id_boards = f"ID:{id_b}"

            for wav, state in self.__config_set["__wavelengths__"].items():
                if not state:
                    continue

                led_id = f"LED:{self.wavelengths[wav]}"
                duty = f'DUTY:{self.__config_set["__pwm__"].loc[wav, board]}'

                message = "{" + f"{id_boards},{led_id},{duty},START" + "}"
                name_capture.append(f"bd_{id_b}_{wav}")
                if self.tx_msg(message, time_sleep=time_sleep):
                    return True

        return name_capture

    def __str__(self):
        """
        Retorna un json con la configuración de la corona
        """
        return json.dumps(self.__config_set, indent=4)

    def __del__(self):
        """
        Termina la comunicación Serial
        """
        if self.__comunication_state:
            self.__comunication.close()

        print("Comunicación Terminada")
