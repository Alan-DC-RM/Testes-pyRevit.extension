import os
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))   # Diretório onde esta salvo o script zipper

for entry in os.scandir(base_dir):                      # Para cada item do base_dir, vamos fazer um loop
    # scandir() é superior ao listdir() porque retorna a entidade da entry, enquanto a 2a opção retorna strings do nome
    if os.path.isdir(entry):                            # Se for um diretório (pasta) eu continuo para fazer o zip
        path_pasta = entry.path                         # Pegando o diretório completo da pasta a ser zipada
        shutil.make_archive(                            # Função do módulo nativo Python Shutil (ver + na doc oficial)
            path_pasta,                                 # Indicando o nome do arquivo com o path completo ate ele
            # coincidentemente é o mesmo que o path_pasta porque estou criando uma cópia
            "zip",                               # formato do arquivo novo criado (zip, no caso)
            root_dir=path_pasta                         # Mesmo path. All conteudo será copiado para o novo arquivo zip
        )
