import pandas as pd
import tkinter as tk
from ui_components.tkinter_form import Form

PandasTable = pd.DataFrame(
    {
        "AAA": [4, 5, 6, 7],
        "BBB": [10, 20.4, 30, 40],
        "CCC": [100, 50, -30, -50],
        "DDD": ["asdf1", "asdf2", "asdf3", "asdf4"],
    },
    index=["450 nm", "470 nm", "480 nm", "490 nm"],
)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        estruct = {"table": PandasTable}
        self.form = Form(
            self,
            name_form="calculations of a rectangle",
            form_dict=estruct,
            name_config="calculate",
            button=True,
        )
        self.form.pack(fill="both", expand=1)

        self.mainloop()


if __name__ == "__main__":
    App()
