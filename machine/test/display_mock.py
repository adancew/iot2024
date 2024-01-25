import tkinter as tk
from PIL import ImageTk


class DisplayMock:
    width = 96
    height = 64

    def ShowImage(self, image, _x, _y):
        image = image.resize((self.width * 3, self.height * 3))
        im = ImageTk.PhotoImage(image)
        self.label.configure(image=im)
        self.label.pack()

        self.master.update()

    def clear(self):
        pass

    def Init(self):
        self.master = tk.Tk()
        self.master.title("Display")
        self.label = tk.Label(self.master)