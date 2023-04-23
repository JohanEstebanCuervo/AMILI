"""
Programmed By Johan Esteban Cuervo Chica

Este Código genera un formulario de tkinter automaticamente
apartir de un diccionario base. Retornando un tk.Frame object
con unos atributos adicionales.
"""

import tkinter as tk
from tkinter import ttk


class Form(ttk.LabelFrame):
    """
    TK.Frame que contiene un formulario a partir
    de un diccionario de python con los metodos
    adicionales:

    self.get()
    self.set()
    self.widgets
    self.button

    Args:
        master (object): tk contenedor
        name_form (str): Nombre del Formulario
        form_dict (dict): diccionario base del formulario
        name_config (str, optional): Nombre del botón que realiza una acción con el formulario.
            Defaults to "configure".
        button (bool, optional): Boton de acción. Defaults to True.
    """

    def __init__(
        self,
        master: object,
        name_form: str,
        form_dict: dict,
        name_config: str = "configure",
        button: bool = True,
    ) -> None:
        """_summary_

        Args:
            master (object): _description_
            form_dict (dict): _description_
            name_config (str, optional): _description_. Defaults to "configure".

        """
        super().__init__(master, text=name_form)

        self.__type_vars = {
            "float": tk.DoubleVar,
            "int": tk.IntVar,
            "str": tk.StringVar,
            "bool": tk.BooleanVar,
            "list": tk.StringVar,
        }

        self.__configure_widgets = {
            "float": self.__configure_float,
            "int": self.__configure_int,
            "str": self.__configure_str,
            "bool": self.__configure_bool,
            "list": self.__configure_list,
        }

        self.__type_widgets = {
            "float": ttk.Entry,
            "int": ttk.Entry,
            "str": ttk.Entry,
            "bool": ttk.Checkbutton,
            "list": ttk.Combobox,
        }

        self.__create_widgets(form_dict, name_config, button)

    def __validate_float(self, new_text: str) -> bool:
        """
        Validate Float number in tk.entry

        Args:
            new_text (str): entry text

        Returns:
            bool: True si es Float, False si no es float
        """
        try:
            float(new_text)
            return True
        except ValueError:
            if new_text == "":
                return True

            return False

    def __validate_int(self, new_text: str) -> bool:
        """
        Validate Int number in tk.entry

        Args:
            new_text (str): entry text

        Returns:
            bool: True si es int, False si no es int
        """
        try:
            int(new_text)
            return True
        except ValueError:
            if new_text == "":
                return True

            return False

    def __configure_list(
        self, widget: ttk.Combobox, variable: tk.StringVar, value: str
    ) -> None:
        """
        Configure form value list

        Args:
            widget (ttk.Entry): ttk entry
            variable (tk.DoubleVar): var dict
            value (str): value set variable
        """
        variable.set(value[0])
        widget.config(state="readonly", values=value, textvariable=variable)

    def __configure_bool(
        self, widget: ttk.Checkbutton, variable: tk.BooleanVar, value: bool
    ) -> None:
        """
        Configure form value float

        Args:
            widget (ttk.Entry): ttk entry
            variable (tk.DoubleVar): var dict
            value (bool): value set variable
        """
        variable.set(value)
        widget.config(variable=variable)

    def __configure_float(
        self, widget: ttk.Entry, variable: tk.DoubleVar, value: float
    ) -> None:
        """
        Configure form value float

        Args:
            widget (ttk.Entry): ttk entry
            variable (tk.DoubleVar): var dict
            value (float): value set variable
        """
        variable.set(value)
        reg_fun = (self.register(self.__validate_float), "%P")

        widget.config(validate="key", validatecommand=reg_fun, textvariable=variable)

    def __configure_str(
        self, widget: ttk.Entry, variable: tk.StringVar, value: str
    ) -> None:
        """
        Configure form value str

        Args:
            widget (ttk.Entry): ttk entry
            variable (tk.StringVar): var dict
            value (str): value set variable
        """
        variable.set(value)
        widget.config(textvariable=variable)

    def __configure_int(
        self, widget: ttk.Entry, variable: tk.IntVar, value: int
    ) -> None:
        """
        Configure form value int

        Args:
            widget (ttk.Entry): ttk entry
            variable (tk.IntVar): var dict
            value (int): value set variable
        """
        variable.set(value)
        reg_fun = (self.register(self.__validate_int), "%P")

        widget.config(validate="key", validatecommand=reg_fun, textvariable=variable)

    def __create_widgets(self, form_dict: dict, name_config: str, button: bool) -> None:
        """
        Crea los widgets del formulario

        Args:
            form_dict (dict): _description_
            name_config (str): _description_
            button (bool): _description_
        """
        self.widgets = {}
        self.__vars = {}
        for index, dict_vals in enumerate(form_dict.items()):
            name_key = dict_vals[0]
            value = dict_vals[1]

            type_value = str(type(value))[8:-2]

            if type_value == "dict":
                widget = Form(self, name_key, value, button=False)
                widget.grid(row=index, column=0, columnspan=2, sticky="nesw")

                self.__vars[name_key] = widget
                self.widgets[name_key] = widget

                continue

            variable = self.__type_vars[type_value]()
            self.__vars[name_key] = variable
            widget = self.__type_widgets[type_value](self)
            widget.grid(row=index, column=1, sticky="nesw", padx=2, pady=2)
            label = ttk.Label(self, text=name_key)
            label.grid(row=index, column=0, sticky="nes", padx=2, pady=2)

            config = self.__configure_widgets[type_value]

            config(widget, variable, value)

            self.widgets[name_key] = [label, widget]

            ult_val = index

        if button is True:
            self.button = ttk.Button(
                self, text=name_config, command=lambda: print(self.get())
            )
            self.button.grid(row=ult_val + 1, column=0, columnspan=2, sticky="nesw")

    def get(self) -> dict:
        """
        Genera un diccionario con los valores ingresados
        en el formulario.

        Returns:
            dict: diccionario con la estructura del formulario
        """
        plain_dict = {}

        for key, var in self.__vars.items():
            try:
                value = var.get()

            except tk.TclError:
                value = "0"
                var.set(0)

            plain_dict[key] = value

        return plain_dict

    def set(self, set_dict: dict) -> None:
        """
        Cambia los valores del formulario

        Args:
            set_dict (dict): valores a setear

        """
        for key, var in set_dict.items():
            if isinstance(var, dict):
                self.__vars[key].set(var)
                continue
            self.__vars[key].set(var)
