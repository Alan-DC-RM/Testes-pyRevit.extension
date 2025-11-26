# -*- coding: utf-8 -*-
__title__ = "Ativar Dimensões Automáticas"

# __________________________________________________________________________________________________________________________________________

import os, sys, math, datetime, time
from Autodesk.Revit.DB import *
#from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import ObjectType
#from Autodesk.Revit.DB.Structure import *
#from Autodesk.Revit.DB.Architecture import *

from pyrevit import revit, forms
#import clr
#clr.AddReference("System")
#from System.Collections.Generic import List

# Custom Imports
#from collections import defaultdict

# __________________________________________________________________________________________________________________________________________

doc             = __revit__.ActiveUIDocument.Document   #type: UIDocument
uidoc           = __revit__.ActiveUIDocument            #type: Document
selection       = uidoc.Selection                       #type: Selection

# __________________________________________________________________________________________________________________________________________

if __name__ == '__main__':

    # ------------------------------------------------------------------------------
    # Selecionar elementos
    # ------------------------------------------------------------------------------

    reference = uidoc.Selection.PickObject(ObjectType.Element, "Selecione um Ferro ou um Graute")
    seleção = doc.GetElement(reference)
    # Tratando inputs únicos, transformando em lista de 1 índice caso seja único para não crashar o código
    if isinstance(seleção, list):
        element = seleção
    else:
        element = [seleção]

    # ------------------------------------------------------------------------------
    # Definir listas de elementos (instâncias) e Types dos elementos, a serem populadas no loop
    #   - Comentei as linhas das listas de Types, que não usamos nesse código
    # ------------------------------------------------------------------------------

    ferros_horiz = []
    #types_ferros_horiz = []
    ferros_vert = []
    #types_ferros_vert = []
    #grautes_horiz = []
    #types_grautes_horiz = []
    grautes_vert = []
    #types_grautes_vert = []

    # ------------------------------------------------------------------------------
    # Popular listas definidas, separando nos tipos de graute e ferro e prevendo seleção errônea
    #   - Comentei a linha de popular os grautes horizontais porque não são afetados pelo Dim Aut, apesar de terem os parâmetros
    # ------------------------------------------------------------------------------

    for elem in element:
        id_do_type = elem.GetTypeId()
        type_elem = doc.GetElement(id_do_type)
        try:
            valor_tipo_elemento = type_elem.LookupParameter("Tipo de Elemento").AsString()
            if valor_tipo_elemento == "FRH":
                ferros_horiz.append(elem)
                #types_ferros_horiz.append(type_elem)
            elif valor_tipo_elemento == "FRV":
                ferros_vert.append(elem)
                #types_ferros_vert.append(type_elem)
                '''
            elif valor_tipo_elemento == "GRH":
                grautes_horiz.append(elem)
                types_grautes_horiz.append(type_elem)
                '''
            elif valor_tipo_elemento == "GRV":
                grautes_vert.append(elem)
                #types_grautes_vert.append(type_elem)
            else:
                forms.alert("Selecione um Ferro H/V ou Graute V!")
        except:
            forms.alert("Selecione um Generic Model!")

    # ------------------------------------------------------------------------------

    t = Transaction(doc,__title__)
    t.Start()

    # ------------------------------------------------------------------------------
    # Ferros Horizontais
    # ------------------------------------------------------------------------------

    for ferro_horiz in ferros_horiz:

        # ------------------------------------------------------------------------------
        # Deslocamento Ferro Horizontal
        # ------------------------------------------------------------------------------

        cobr_frh = ferro_horiz.LookupParameter("Cobrimento").AsDouble()
        arm_pos_frh = ferro_horiz.LookupParameter("Armadura Positiva").AsInteger()
        if arm_pos_frh == 1:
            desloc_frh = cobr_frh + (2/30.48)
            ferro_horiz.LookupParameter("Deslocamento Ferro Horizontal").Set(desloc_frh)
        else:
            desloc_frh = (19/30.48) - cobr_frh
            ferro_horiz.LookupParameter("Deslocamento Ferro Horizontal").Set(desloc_frh)

        # ------------------------------------------------------------------------------
        # Comprimento Patas Direita e Esquerda
        # ------------------------------------------------------------------------------

        altura_can_frh = ferro_horiz.LookupParameter("Altura Canaleta").AsDouble()
        pata_esq_frh = ferro_horiz.LookupParameter("Pata Esquerda").AsInteger()
        pata_dir_frh = ferro_horiz.LookupParameter("Pata Direita").AsInteger()
        # Cobrimento já foi obtido na seção acima, para o deslocamento do ferro horizontal
        if altura_can_frh == 19 / 30.48:
            pata_aut = 16.5 / 30.48 - cobr_frh
        elif altura_can_frh == 9 / 30.48:
            pata_aut = 6.5 / 30.48 - cobr_frh
        else:
            pata_aut = 0.1 / 30.48
        if pata_esq_frh == 1:
            ferro_horiz.LookupParameter("Comprimento Pata Esquerda").Set(pata_aut)
        else:
            ferro_horiz.LookupParameter("Comprimento Pata Esquerda").Set(0.1 / 30.48)
        if pata_dir_frh == 1:
            ferro_horiz.LookupParameter("Comprimento Pata Direita").Set(pata_aut)
        else:
            ferro_horiz.LookupParameter("Comprimento Pata Direita").Set(0.1 / 30.48)

        # ------------------------------------------------------------------------------
        # Comprimento Ferro Horizontal Direita e Esquerda
        # ------------------------------------------------------------------------------

        compr_graute_esq_frh = ferro_horiz.LookupParameter("Comprimento Graute Esquerda").AsDouble()
        compr_graute_dir_frh = ferro_horiz.LookupParameter("Comprimento Graute Direita").AsDouble()
        compr_transp_esq_frh = ferro_horiz.LookupParameter("Comprimento Transpasse Esquerda").AsDouble()
        compr_transp_dir_frh = ferro_horiz.LookupParameter("Comprimento Transpasse Direita").AsDouble()

        ferro_horiz.LookupParameter("Comprimento Ferro Horizontal Esquerda").Set(compr_graute_esq_frh + compr_transp_esq_frh)
        ferro_horiz.LookupParameter("Comprimento Ferro Horizontal Direita").Set(compr_graute_dir_frh + compr_transp_dir_frh)

        # ------------------------------------------------------------------------------
        # Desabilitar Dimensões Automáticas pós finalizado
        # ------------------------------------------------------------------------------

        ferro_horiz.LookupParameter("Dimensões Automáticas").Set(False)

    # ------------------------------------------------------------------------------
    # Grautes Verticais
    # ------------------------------------------------------------------------------

    for graute_vert in grautes_vert:

        # ------------------------------------------------------------------------------
        # Graute Vertical (só tem 1 parâmetro -> Altura Graute)
        # ------------------------------------------------------------------------------

        alt_pav_grv = graute_vert.LookupParameter("Altura do Pavimento").AsDouble()
        esp_laj_sup_grv = graute_vert.LookupParameter("Espessura da Laje Superior").AsDouble()
        graute_vert.LookupParameter("Altura Graute").Set(alt_pav_grv-esp_laj_sup_grv-(17 / 30.48))

        # ------------------------------------------------------------------------------
        # Desabilitar Dimensões Automáticas pós finalizado
        # ------------------------------------------------------------------------------

        graute_vert.LookupParameter("Dimensões Automáticas").Set(False)

    # ------------------------------------------------------------------------------
    # Ferros Verticais
    # ------------------------------------------------------------------------------

    for ferro_vert in ferros_vert:

        # ------------------------------------------------------------------------------
        # Parâmetros de Type
        # ------------------------------------------------------------------------------
        id_do_type_frv = ferro_vert.GetTypeId()
        type_frv = doc.GetElement(id_do_type_frv)
        diam = type_frv.LookupParameter("Ø").AsDouble()

        # ------------------------------------------------------------------------------
        # Altura Graute
        # ------------------------------------------------------------------------------

        alt_pav_frv = ferro_vert.LookupParameter("Altura do Pavimento").AsDouble()
        esp_laj_sup_frv = ferro_vert.LookupParameter("Espessura da Laje Superior").AsDouble()
        ferro_vert.LookupParameter("Altura Graute").Set(alt_pav_frv-esp_laj_sup_frv-(17 / 30.48))

        # ------------------------------------------------------------------------------
        # Altura 1a Posição Aut.
        # ------------------------------------------------------------------------------

        ferro_vert.LookupParameter("Altura 1a Posição").Set(120 / 30.48 + 40 * diam)

        # ------------------------------------------------------------------------------
        # Altura 2a Posição Aut.
        # ------------------------------------------------------------------------------

        ferro_vert.LookupParameter("Início 2a Posição").Set(120 / 30.48)

        # ------------------------------------------------------------------------------
        # Altura Total Aut.
        # ------------------------------------------------------------------------------

        ferro_vert.LookupParameter("Altura Total").Set(alt_pav_frv)

        # ------------------------------------------------------------------------------
        # Transpasse Inferior
        # ------------------------------------------------------------------------------

        ferro_vert.LookupParameter("Transpasse Inferior").Set(40 * diam)


    t.Commit()

# __________________________________________________________________________________________________________________________________________
