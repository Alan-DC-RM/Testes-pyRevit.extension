# -*- coding: utf-8 -*-
__title__ = "Blocos Padrão"
__doc__ = '''
Esse código serve para carregar as famílias especificadas no diretório de blocos padrão.
'''

from System.IO import Directory, SearchOption, Path                                                                     # Permite acessar diretórios e buscar arquivos .NET, não é nativo do Python (apesar que daria para fazer só com Python, acredito eu)
from Autodesk.Revit.DB import Document, Transaction                                                                     # Importa classes da API do Revit, só as que usamos

doc = __revit__.ActiveUIDocument.Document  #type: UIDocument

# Lista de diretórios para buscar as famílias
direct = r"N:\Engenharia\BIM\02-Familias\01-Biblioteca RM\Blocos Alvenaria\Concreto\Blocos padrão"                      # Não fizemos listas porque é um diretório só. Se optarmos por mudar, temos que fazer lista e um loop "for dir in dirs:" na lógica abaixo

searchstring = "*.rfa"                                                                                                  # O "*" indica que deve conter isso na string. Buscamos todos os files que contenham ".rfa", ou seja, arquivos de famílias
foundfiles = []                                                                                                         # Lista onde serão armazenados os caminhos contendo os arquivos das famílias encontradas dentro do caminho dirs

if Directory.Exists(direct):                                                                                            # Verifica se o diretório existe
    dirfiles = Directory.GetFiles(direct, searchstring, SearchOption.TopDirectoryOnly)                                  # SearchOption.TopDirectoryOnly não busca subpastas! Seria o input "deep search" do Node do Crumple no Dynamo
    foundfiles.extend(dirfiles)                                                                                         # Adiciona os arquivos encontrados à lista que vamos usar para carregar os arquivos
else:                                                                                                                   # Se mudarmos o caminho, o código vai avisar isso e a próxima vez que rodar alguém vai nos avisar para atualizarmos ele.
    print("Diretório não encontrado! Provavelmente foi alterado ou renomeado. Informe a equipe BIM.")

t = Transaction(doc, __title__)                                                                                         # Começando uma nova transaction, para carregar as famílias de fato
t.Start()
for fampath in foundfiles:                                                                                              # Loop em cada arquivo de família encontrado
    try:                                                                                                                # Usamos try para não "descarregar" as famílias carregados caso uma delas de erro
        print("\nCarregando família: " + Path.GetFileName(fampath.split(".rfa")[0]))                                    # Mensagem de início do carregamento
        doc.LoadFamily(fampath)                                                                                         # Aqui de fato carregamos no projeto, é um método da Document Class da API, que passamos a string do path do file da família, nos retorna True ou False apenas
        print("Família carregada com sucesso!")                                                                         # Mensagem de final do carregamento + sucesso!
    except:
        print("\n\n***\n\nFalha ao carregar a família.\n\n***\n\n")                                                     # Mensagem de erro quando não der para carregar qualquer família da lista
print("\n\n" + "_" * 50 + "\n\n\nCarregamento concluído.\n\n" + "_" * 50)
t.Commit()                                                                                                              # Finaliza a transação
