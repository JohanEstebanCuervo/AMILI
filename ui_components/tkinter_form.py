"""
Programmed By Johan Esteban Cuervo Chica

This code generates a tkinter form automatically from a base dictionary.
from a base dictionary. Returning a tk.Frame object
with some additional attributes.
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd


class CreateWidgets:
    """
    Clas contain the creation widgets. and validation types
    """

    def __init__(self) -> None:
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

    def create_label(
        self, text: str, row: int, column: int = 0, padx: int = 2, pady: int = 2
    ) -> ttk.Label:
        """
        Create Label item in the master

        Args:
            text (str): text label
            row (int): row position grid in master
            column (int, optional): column position grid in master. Defaults to 0.

        Returns:
            ttk.Label: Label object create
        """
        label = ttk.Label(self, text=text)
        label.grid(row=row, column=column, sticky="nes", padx=padx, pady=pady)

        return label

    def create_widget(
        self, value, variable, row: int, column: int = 1, padx: int = 2, pady: int = 2
    ) -> object:
        """
        Create entry object tkinter

        Args:
            value (Any): Value for widget
            variable (Any): Variable create for widget
            row (int): row position widget in master
            column (int, optional): column position widget in master. Defaults to 1.

        Returns:
            object: widget ttk
        """
        type_value = str(type(value))[8:-2]

        widget = self.__type_widgets[type_value](self)
        tk.Grid.columnconfigure(self, 1, weight=1)
        widget.grid(row=row, column=column, sticky="nesw", padx=padx, pady=pady)

        tk.Grid.columnconfigure(self, 0, weight=1)

        config = self.__configure_widgets[type_value]

        config(widget, variable, value)

        return widget

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


class Table(ttk.LabelFrame, CreateWidgets):
    """
    Table class for ttk from pandas.DataFrame
    """

    def __init__(self, master: object, table: pd.DataFrame, text: str) -> None:
        ttk.LabelFrame.__init__(self, master, text=text)
        CreateWidgets.__init__(self)

        self.__type_vars = {
            "float": tk.DoubleVar,
            "int": tk.IntVar,
            "str": tk.StringVar,
            "bool": tk.BooleanVar,
            "list": tk.StringVar,
        }

        self.__create_widgets(table)

    def __create_widgets(self, table: pd.DataFrame) -> None:
        """
        Create form widgets

        Args:
            form_dict (dict): form dict base
            name_config (str): name_config
            button (bool): button_config
        """
        self.columns = []
        self.indexs = []
        self.widgets = []
        self.__vars = []

        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(self, 0, weight=1)
        for index, name in enumerate(table.columns):
            tk.Grid.columnconfigure(self, index + 1, weight=1)
            label = self.create_label(name, 0, index + 1, padx=0)
            self.columns.append(label)

        for index, name in enumerate(table.index):
            tk.Grid.rowconfigure(self, index + 1, weight=1)
            label = self.create_label(name, index + 1, 0, pady=0)
            self.indexs.append(label)

        for index_row, row_data in enumerate(table.iterrows()):
            row_widgets = []
            row_vars = []
            for index_col, value in enumerate(row_data[1]):
                type_value = str(type(value))[8:-2]

                variable = self.__type_vars[type_value]()
                row_vars.append(variable)

                widget = self.create_widget(
                    value, variable, index_row + 1, index_col + 1, padx=0, pady=0
                )
                row_widgets.append(widget)

            self.widgets.append(row_widgets)
            self.__vars.append(row_vars)

    def get(self) -> pd.DataFrame:
        """
        Return Dataframe with values entry

        Returns:
            pd.DataFrame: dataframe result
        """

        columns = [label["text"] for label in self.columns]
        indexs = [index["text"] for index in self.indexs]

        values = []

        for row_vars in self.__vars:
            row_vals = [var.get() for var in row_vars]

            values.append(row_vals)

        return pd.DataFrame(values, columns=columns, index=indexs)


class Form(ttk.LabelFrame, CreateWidgets):
    """
    Form is a ttk.LabelFrame containing a form from a python dictionary with the
    from a Python dictionary with the additional methods
    additional methods:

    self.get()
    self.set()
    self.set_labels_text()
    self.widgets
    self.button

    Args:
        master (object): tk container
        name_form (str): Form Name
        form_dict (dict): base dictionary of the form
        name_config (str, optional): Name of the button that performs an action with the form..
            Defaults to "configure".
        button (bool, optional): Action button. Defaults to True.
    """

    def __init__(
        self,
        master: object,
        name_form: str,
        form_dict: dict,
        name_config: str = "configure",
        button: bool = True,
    ) -> None:
        ttk.LabelFrame.__init__(self, master, text=name_form)
        CreateWidgets.__init__(self)

        self.__type_vars = {
            "float": tk.DoubleVar,
            "int": tk.IntVar,
            "str": tk.StringVar,
            "bool": tk.BooleanVar,
            "list": tk.StringVar,
        }

        tk.Grid.columnconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)

        self.button = None
        self.__create_widgets(form_dict, name_config, button)

    def __create_widgets(self, form_dict: dict, name_config: str, button: bool) -> None:
        """
        Create form widgets

        Args:
            form_dict (dict): form dict base
            name_config (str): name_config
            button (bool): button_config
        """
        self.widgets = {}
        self.__vars = {}
        for index, dict_vals in enumerate(form_dict.items()):
            name_key = dict_vals[0]
            value = dict_vals[1]

            type_value = str(type(value))[8:-2]
            tk.Grid.rowconfigure(self, index, weight=1)
            if type_value == "dict":
                widget = Form(self, name_key, value, button=False)
                widget.grid(row=index, column=0, columnspan=2, sticky="nesw")

                self.__vars[name_key] = widget
                self.widgets[name_key] = widget

                continue

            if type_value == "pandas.core.frame.DataFrame":
                widget = Table(self, value, name_key)
                widget.grid(row=index, column=0, columnspan=2, sticky="nesw")

                self.__vars[name_key] = widget
                self.widgets[name_key] = widget

                continue

            variable = self.__type_vars[type_value]()
            self.__vars[name_key] = variable

            label = self.create_label(name_key, index)
            widget = self.create_widget(value, variable, index)
            self.widgets[name_key] = [label, widget]

        ult_val = index

        if button is True:
            self.button = ttk.Button(
                self, text=name_config, command=lambda: print(self.get())
            )
            self.button.grid(row=ult_val + 1, column=0, columnspan=2, sticky="nesw")

    def get(self) -> dict:
        """
        returns a dictionary with the values entered in the form.
        in the form.

        Returns:
            dict: dictionary with the structure of the form
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
        Change the values of the form

        Args:
            set_dict (dict): values to be set

        """
        for key, var in set_dict.items():
            self.__vars[key].set(var)

    def set_labels_text(self, set_labels: dict) -> None:
        """
        Edit text labels Interfaces

        Args:
            set_labels (dict): labels to_edit
        """
        for key, var_name in set_labels.items():
            if key == "__form__":
                self.config(text=var_name)
                continue
            if isinstance(var_name, dict):
                self.widgets[key].set_labels_text(var_name)
                continue
            if isinstance(var_name, pd.DataFrame):
                self.widgets[key].set_labels_text(var_name)
                continue
            self.widgets[key][0].config(text=var_name)
