# -*- coding: utf-8 -*-
__title__ = "Família de 9 (h = 19)"
__doc__= '''
Esse código serve para carregar as famílias de 9cm de largura e 19cm de altura.
'''

from System.IO import Directory, SearchOption, Path
from Autodesk.Revit.DB import Document, Transaction


doc = __revit__.ActiveUIDocument.Document  #type: UIDocument

# Lista de diretórios para buscar as famílias
direct = r"N:\Engenharia\BIM\02-Familias\01-Biblioteca RM\Blocos Alvenaria\Concreto\Família de 9 cm\h=19 cm"

searchstring = "*.rfa"
foundfiles = []

if Directory.Exists(direct):
    dirfiles = Directory.GetFiles(direct, searchstring, SearchOption.TopDirectoryOnly)
    foundfiles.extend(dirfiles)
else:
    print("Diretório não encontrado! Provavelmente foi alterado ou renomeado. Informe a equipe BIM.")

t = Transaction(doc, __title__)
t.Start()
for fampath in foundfiles:
    try:
        print("\nCarregando família: " + Path.GetFileName(fampath.split(".rfa")[0]))
        doc.LoadFamily(fampath)
        print("Família carregada com sucesso!")
    except:
        print("\n\n***\n\nFalha ao carregar a família.\n\n***\n\n")
print("\n\n" + "_" * 50 + "\n\n\nCarregamento concluído.\n\n" + "_" * 50)
t.Commit()
