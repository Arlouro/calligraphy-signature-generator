import tkinter as tk
from PIL import Image, ImageTk
from tkinter import PhotoImage

window=tk.Tk()
window.title("Schrijven")
window.geometry("700x700")
icone = PhotoImage(file="pen.png")
window.iconphoto(True, icone)

window.configure(bg='#3C1722')


imagem_original = Image.open("schrijven.png").convert("RGBA")
fundo = Image.new("RGBA", imagem_original.size, "#3C1722")
imagem_sem_transparencia = Image.alpha_composite(fundo, imagem_original)

imagem_tk = ImageTk.PhotoImage(imagem_sem_transparencia)
label = tk.Label(window, image=imagem_tk, bg='#3C1722')
label.pack()



window.mainloop()