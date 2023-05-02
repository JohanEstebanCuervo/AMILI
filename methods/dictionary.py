"""
Este Modulo contiene algoritmos para la comparación de diccionarios
que contienen dataframes. pensando en una interfaz que realiza una configuración
a un objeto
"""
import pandas as pd


def compare_dicts(dict1: dict, dict2: dict) -> bool:
    """
    Función que compara si dos diccionarios son iguales
    cuando estos incluyen DataFrames, strings, bool,
    int, floats. No esta pensado para listas.

    Args:
        dict1 (dict): diccionario 1
        dict2 (dict): diccionario 2

    Returns:
        bool: True si son iguales False en caso contrario
    """

    if not isinstance(dict1, dict):
        raise TypeError(f"var dict1 not is dictionary: class {type(dict1)}")
    if not isinstance(dict2, dict):
        raise TypeError(f"var dict2 not is dictionary: class {type(dict2)}")

    if len(dict1) != len(dict2):
        return False

    for key, item in dict1.items():
        if key not in dict2:
            return False

        if isinstance(item, pd.DataFrame):
            if not item.equals(dict2[key]):
                return False

        elif isinstance(item, dict):
            if not compare_dicts(item, dict2[key]):
                return False

        else:
            if item != dict2[key]:
                return False

    return True
