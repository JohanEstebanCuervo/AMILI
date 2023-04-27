import tkinter as tk
from ui_components.tkinter_form import Form


class FormDialog(tk.Tk, tk.Toplevel):
    """
    Form Dialog
    """

    def __init__(self, struct: dict, master=None, name_button: str = "submit"):
        if master is None:
            tk.Tk.__init__(self)

        else:
            tk.Toplevel.__init__(self, master)

        self.master = master
        self.values = None
        self.form = Form(self, "", struct, name_config=name_button)

        self.form.button.config(command=self.__submit__)

        self.form.pack()
        # self.bind("<Return>", self.__submit__)
        self.lift()
        self.attributes("-topmost", True)

    def __submit__(self):
        self.values = self.form.get()
        self.destroy()

    def execute(self):
        if self.master is None:
            self.mainloop()
        else:
            self.grab_set()
            self.master.wait_window(self)

        return self.values


def form_dialog(struct: dict, master=None, name_button: str = "submit") -> dict:
    window = FormDialog(struct, master, name_button)

    return window.execute()


if __name__ == "__main__":

    def bt_f():
        struct = {
            "val 1": 2,
            "val 2": 3,
        }

        result = form_dialog(struct, window)
        print(result)

    window = tk.Tk()

    bt = tk.Button(window, text="form", command=bt_f)
    bt.pack()

    window.mainloop()
