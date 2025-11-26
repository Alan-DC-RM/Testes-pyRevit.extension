# -*- coding: utf-8 -*-
__title__ = "Carregar famílias TQS\n(Todas - Automático)"
__doc__ = '''
Esse código serve para carregar todas as famílias padrão do TQS que foram alteradas pela equipe BIM, adequadas
ao nosso processo interno da RM.

Incluí blocos de fundação, pilar retangular, viga retangular
'''

from System.IO import Directory, SearchOption, Path
from Autodesk.Revit.DB import Document, Transaction

# Lista de diretórios para buscar as famílias
dirs = [r"N:\Engenharia\BIM\02-Familias\02-Biblioteca TQS\2022 (principal) - 2023 - 2024\Families"]

# Configurações
searchstring = "*.rfa"
foundfiles = []

for d in dirs:
    if Directory.Exists(d):
        dirfiles = Directory.GetFiles(d, searchstring, SearchOption.TopDirectoryOnly)
        foundfiles.extend(dirfiles)
    else:
        print("Diretório não encontrado! Provavelmente foi alterado ou renomeado. Informe a equipe BIM.")

doc = __revit__.ActiveUIDocument.Document  #type: UIDocument

t = Transaction(doc, __title__)
t.Start()
for fampath in foundfiles:
    try:
        print("\nCarregando família: " + Path.GetFileName(fampath.split(".rfa")[0]))
        doc.LoadFamily(fampath)
        print("Família carregada com sucesso!")
    except:
        print("\n\n***\n\nFalha ao carregar a família.\n\n***\n\n")
t.Commit()
