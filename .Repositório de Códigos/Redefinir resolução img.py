from PIL import Image
import os

nome_arquivo_imagem = "icon.png"
try:
    img = Image.open(nome_arquivo_imagem)
    img = img.resize((96, 96))  # novo tamanho em pixels
    img.save("icon.png", dpi=(500, 500))  # define DPI
    print("\nSucesso!\n\nArquivo PNG icon criado/sobreescrito!")
except FileNotFoundError:
    print("\n***\n\nNão encontrou!\n\n***")
'''
Para usar esse script:
    - Coloque ele no mesmo diretório da imagem;
    - Altere o valor da variável "nome_arquivo_imagem" (se necessário)
    - rode o script
    - Uma nova imagem será salva com o nome 'new_icon.png';
    - Apague a antiga imagem manualmente e renomeie a nova
    - Pronto
'''
os.startfile(os.path.dirname(os.path.abspath(__file__)))
