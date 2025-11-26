# -*- coding: utf-8 -*-
__title__ = "Viga Retangular RM"
__doc__ = "Viga com setinha"

from Autodesk.Revit.DB import Document, Transaction
from System.IO import Path

# Caminho direto do arquivo da família desejada - Alterar aqui, caso mude!
fampath = r"N:\Engenharia\BIM\02-Familias\01-Biblioteca RM\Concreto In-Loco\RM - Viga retangular.rfa"

doc = __revit__.ActiveUIDocument.Document  # type: UIDocument

t = Transaction(doc, __title__)
t.Start()
try:
    print("Carregando família: " + Path.GetFileName(fampath.split(".rfa")[0]))
    doc.LoadFamily(fampath)
    print("Família carregada com sucesso!")
except:
    print("Falha ao carregar a família.")
t.Commit()
