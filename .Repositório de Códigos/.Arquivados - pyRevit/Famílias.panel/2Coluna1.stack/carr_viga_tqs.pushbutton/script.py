# -*- coding: utf-8 -*-
__title__ = "Viga Retangular TQS"
__doc__ = "Viga sem setinha"

from Autodesk.Revit.DB import Document, Transaction
from System.IO import Path

# Caminho direto da família desejada
fampath = r"N:\Engenharia\BIM\02-Familias\02-Biblioteca TQS\2022 (principal) - 2023 - 2024\Families\TQS - Viga retangular.rfa"

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
