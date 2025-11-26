import tkinter as tk

def finisher():
    global texto
    texto = entrada.get()
    janela.destroy()


janela = tk.Tk()
janela.title("Zipper")
janela.geometry("300x150")

label = tk.Label(janela, text="Forneça o caminho do diretório\nonde estão as pastas a serem zipadas")
label.pack(pady=5)

entrada = tk.Entry(janela, width=30)
entrada.pack(pady=10)

botao = tk.Button(janela, text="OK", command=finisher)
botao.pack(pady=10)


janela.mainloop()

print(texto)