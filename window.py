import tkinter as tk
from PIL import Image, ImageTk
from tkinter import PhotoImage

window=tk.Tk()
window.title("Schrijven")
window.state('zoomed')
window.configure(bg='#3C1722')

icone = PhotoImage(file="pen.png")
window.iconphoto(True, icone)


imagem_original = Image.open("schrijven.png").convert("RGBA")
max_largura = 300
max_altura = 300

largura_original, altura_original = imagem_original.size
proporcao = min(max_largura / largura_original, max_altura / altura_original)
nova_largura = int(largura_original * proporcao)
nova_altura = int(altura_original * proporcao)

imagem_redimensionada = imagem_original.resize((nova_largura, nova_altura), Image.LANCZOS)
fundo = Image.new("RGBA", imagem_redimensionada.size, "#3C1722")
imagem_sem_transparencia = Image.alpha_composite(fundo, imagem_redimensionada)
imagem_tk = ImageTk.PhotoImage(imagem_sem_transparencia)

label = tk.Label(window, image=imagem_tk, bg='#3C1722')
label.place(relx=0.5, rely=0.2, anchor='center')  


name = tk.Entry(window, width=50, font=("Fredoka", 20), bg='white', fg='#3C1722', relief="flat", highlightthickness=2, highlightbackground="#3C1722", highlightcolor="#EFBF6A")
name.pack(pady=10)
name.place(relx=0.5, rely=0.3, anchor='center')  


window.mainloop()