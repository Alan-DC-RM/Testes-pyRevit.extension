# -*- coding: utf-8 -*-
__title__ = "Comparador Paredes Iguais"
from Autodesk.Revit.DB import *
from pyrevit import revit, forms
import sys

'''
A ideia desse código é, basicamente, ter 2 loops principais e subloops dentro deles, criando dicionários e verificações.
1º Loop vai ser em todos os Generic Models do modelo:
    - Ele gera um dicionário e um "subdicionário" dentro desse dicionário maior (ou macro dicionário)
    - O macro dicionário contem como chaves a string no formato [PAVIMENTO] - [PAREDE]
    - O micro dicionário contem, para cada chave do macro que é a parede e seu pavimento, todos os elementos da parede e suas contagens
    - As chaves do micro dicionário é uma concatenação do Family Name + Type Name e o valor de cada chave é o count
    - Contamos via loop respeitando uma ordem hierárquica necessária para fazer a lógica funcionar
2º Loop vai ser no JSON do parâmetro 'Paredes Iguais':
    - Usando "eval" eu pego a string do valor do parâmetro e interpreto ela, gerando dicionários, subdicionários e listas, conforme formatação do JSON
    - Com isso eu consigo loopar
    - A ideia do loop é passar por todas as Childs
    - Na hierarquia maior do JSON eu tenho o Pavimento, que vai ser a primeira string para compor minha chave de acesso ao 1º macro dicionário que criei, explicado acima
    - Na hierarquia seguinte do JSON, eu tenho o valor da Parede Master. Tendo o pavimento e isso, eu componho minha chave para acessar o dicionário dos Generic Models do modelo
    - Nessa mesma hierarquia da Master, eu tenho um item que é a lista de Childs
    - Loopando as Childs, eu crio as chaves junto ao Pavimento que tenho
    - Usando as chaves de acesso de Master e Childs, eu consigo ter o subdicionário de cada parede-pavimento
    - Com esse subdicionário, eu tenho todos os elementos e a contagem deles
    - Comparando isso, eu consigo saber a diferença
    - Assim eu consigo apontar divergências em larga escala
'''

doc = __revit__.ActiveUIDocument.Document   #type: UIDocument

if __name__ == '__main__':

    pj_info = doc.ProjectInformation                                                # pegando projetcinfo para pegar info de Paredes Iguais (abaixo). Daria para pegar com o FilteredElement, ele é uma categoria e passar para .ToElements(), mas essa é uma opção melhor

    try:
        par_iguais_json = pj_info.LookupParameter("ParedesIguais").AsString()       # Aqui eu tento pegar o valor do parâmetro
    except:
        forms.alert(msg="Parâmetro 'ParedesIguais' não carregado no projeto",
                    title="Atenção!")                                               # Se não tiver dou o aviso de que ele não está no projeto
        sys.exit()                                                                  # e finalizo o código

    gen_models = FilteredElementCollector(doc) \
        .OfCategory(BuiltInCategory.OST_GenericModel) \
        .WhereElementIsNotElementType() \
        .ToElements()                                                               # Pegando todos os Generic Models do modelo, vou usar no loop abaixo

    elementos_paredes = {}                                                          # Dicionário vazio, a ser populado com o loop abaixo
    elem_sem_nivel = []                                                             # Lista vazia auxiliar para popular com os nomes de famílias Generic Model com Parede preenchido, mas sem Level

    if par_iguais_json != "" and par_iguais_json:                                   # A condição do loop é justamente se o ParedesIguais já tem valor e não é nada ("")
        for gen in gen_models:                                                      # O loop vai passar por todos os Generic Models do modelo, pegos anteriormente
            par = gen.LookupParameter("Parede").AsString()                          # Pegar o valor do parâmetro Parede de cada um. Como está carregado ao projeto, o parâmetro vai existir em todos, mas só terá valor nos que forem preenchidos
            if par:                                                                 # Verificar se o parâmetro tem algum valor (Generic Model sem Parede preenchido vai pular, otimizando o processamento)
                try:
                    pav = doc.GetElement(gen.LevelId).Name                          # Tentar pegar o Level
                except:
                    pav = "Sem Level"                                               # Ainda vai criar a key no dicionário (Sem Level - ParXX), mas ela não será usada no loop do JSON
                    elem_sem_nivel.append(gen.Name)                                 # Se não der, adicionar à lista de elemento sem Level.
                type_name = gen.Name                                                # Pego o nome do Type
                fam_name = doc.GetElement(gen.GetTypeId()).FamilyName               # Pego o nome da Família
                if type_name != fam_name:                                           # Somente se os nomes não forem iguais da Família e Type, eu concateno.
                    nome = fam_name + " - " + type_name                             # Isso é especialmente importante para diferenciar ferros (horizontais e verticais) que têm o mesmo nome dos Types (Ø5, Ø6,3...)
                else:
                    nome = fam_name                                                 # No caso de serem iguais, eu mantenho apenas o Family Name, isso porque para blocos é o mesmo, assim eu evito a repetição do nome do bloco na lista de output (bloco 14x19x19 - bloco14x19x19, por exemplo é isso que eu quero evitar)
                key = pav + " - " + par                                             # Criando a key do dicionário que é o nome do level junto com o valor da identificação da Parede
                if key not in elementos_paredes:                                    # Verificar se o valor do parâmetro já existe no dicionário
                    elementos_paredes[key] = {nome: 1}                              # Para os primeiros (quando não existir ainda no loop), vamos adicionar um subdicionário com o nome da família (ou família + tipo) junto com o valor 1
                                                                                    # Eu já adiciono o nome:1 aqui porque se a chave "macro" não existe, não adianta eu criar apenas ela, preciso criar a subchave já nesse if, se não criar o elemento inicial só servirá para criar a macrochave, todas as outras aparições da macrochave terão subchaves criadas, menos a primeira que acompanhou e gerou a criação da macrochave
                else:                                                               # Nesse else, a key já consta no dicionário principal.
                    if nome not in elementos_paredes[key]:                          # Então eu tenho um if adicional, verifica se o nome do elemento não consta nas chaves do subdicionário do pavimento + parede, é isso que eu faço quando escrevo "elementos_paredes[key]", estou acessando o subdcionário de elementos de uma parede em um pavimento (key) dentro do macro dicionário de pavimento + paredes (elementos_paredes).
                        elementos_paredes[key][nome] = 1                            # Caso o elemento não exista ainda (if atendido), eu crio a nova subchave com o valor de 1
                    else:
                        elementos_paredes[key][nome] += 1                           # Caso o elemento exista, eu somo 1 no valor da subchave já
    else:
        forms.alert(msg = "Paredes não foram igualadas", title = "Atenção!")        # Se não tiver valor no parâmetro ParedesIguais, não roda o loop e ainda sai do código evitando erros posteriores
        sys.exit()

    data = eval(par_iguais_json)                                                    # eval é um método do próprio Python que interpreta uma string, por exemplo, "["ab", "b"]" e retorna uma interpretação dela, no caso do exemplo, iria retornar a lista ["ab","b"] como lista, não mais como string. Quando usamos isso em uma string em formatação JSON, ele traz em formato de dicionários e listas, respeitando a hierarquia da escrita dos dados

    par_erradas = []                                                                # Lista vazia a ser populada com as paredes que diferem da Master

    for block in data:                                                              # O loop será para cada "bloco" do JSON. O bloco é a estrutura hierarquica maior do texto, composto por Pavimento, Id do pavimento, lista de Walls (obsoleta que fica da memória do código do Igualar Paredes) e um subbloco "GroupWalls" que carrega a informação das paredes Master e Childs. É nessa iteração que vamos subiterar e verificar isso.
        pav = block["Pavimento"]                                                    # Não usei o método .get (que é do Python), para acessar dicionários, porque ele preve o caso de não encontrar, como nosso JSON é padrão, sempre vamos ter o Pavimento como block. O eval criou 2 grandes grupos hierárquicos de dicionários com base no JSON, o maior é dos pavimentos e os menores são dos grupos de paredes
        for group in block.get("GroupsWalls", []):                                  # Estamos acessando no primeiro loop o pavimento. Nesse segundo loop, entamos acessando todos os dicionários do item "GroupsWalls" do dicionário do pavimento, basicamente contem Master, Child e DisplayName
            master = group["Master"]                                                # Então, pegamos o valor da chave "Master" (que é apenas uma string). Sempre vai ter, não precisa usar .get
            childs = group.get("Childs", [])                                        # E o valor da chave "Childs" que é uma lista. Usei .get porque pode ser que a parede não seja igualada a nada, ou seja, não terá Childs, então eu retorno uma lista vazia para não bugar mais para frente
            key_check_m = pav + " - " + master                                      # Eu crio a chave de acesso da Master do JSON concatenando o pavimento e o nome da parede, isso vai me dar a formatação exata para entrar no dicionário construído com os elementos do modelo, acessando a quantidade de elementos da Master (subdicionário do modelo)
            if key_check_m in elementos_paredes:                                    # Só vou acessar o dicionário se a chave consta nele, evitando erros
                dyc_master = elementos_paredes[key_check_m]                         # Acessando o subdicionário da Master (que tem os elementos e suas contagens)
                for child in childs:                                                # Subloop dentro do bloco GroupWalls do JSON, loopando a lista de childs. Para cada parede igualada (Child) eu tenho uma iteração do loop, dentro da iteração do bloco maior que tenho a Master, ou seja, para cada subloop, a Child muda, mas a Master é a mesma
                    key_check_c = pav + " - " + child                               # Criando a chave de acesso ao dicionário de elementos do projeto, para as Childs
                    dyc_child = elementos_paredes.get(key_check_c, {})              # Acessando o dicionário com a chave criada. Usei get porque se não tiver, retorno um dicionário vazio, evitando erros ao comparar abaixo (acho que não precisa, mas foi um caminho mais safe)
                    verif = dyc_master == dyc_child                                 # Verificando se o dicionário da Master é igual ao da Child, ou seja, se a contagem de cada Family + Type de elemento é igual na master e na child
                    if not verif:                                                   # Se não for igual, precisamos verificar o que não é igual
                        for elem in set(dyc_master) | set(dyc_child):               # Set vai me retornar um SET (que é diferente de lista ou dicionário) de valores únicos entre os subdicionários da master e da child (operador " | " faz a união dos dois, evitando repetições. Eu farei um loop para cada elem único nessa união de chaves dos dois dicionários, ou seja, se um elemento existir só na Master ou só na Child, ele é considerado.
                            q_m = dyc_master.get(elem, 0)                           # Aqui eu pego a quantidade de cada elemento da master (cada iteração do loop é um elemento). Cada iteração me dará a quantidade do mesmo elemento em ambos os dicionários, fazendo uma comparação igual para ambas paredes.
                            q_c = dyc_child.get(elem, 0)                            # Quantidade de cada elemento da child. Tem que usar .get para retornar 0 se não houver em qualquer uma das paredes (por exemplo, um bloco que só tem na Master, ou só na Child, isso faz com que não quebre o código.
                            dif = q_m - q_c                                         # Diferença entre quantidade do mesmo elemento entre a Master e a Child da vez do loop
                            if dif == 0:                                            # Se não houver diferença em um dos elementos, eu passo
                                pass
                            elif dif > 0:                                           # Se a diferença for positiva, a Child está com elementos faltando
                                par_erradas.append(                                 # Eu adiciono esse texto concatenado na lista que vou soltar no final do código
                                    key_check_c +
                                    " está com " +                                  # Uma possível melhoria no futuro é formatar isso para CSV, separando com ; e já pensando em uma sequência padrão de informações, mais fácil de jogar no Excel (se precisarem)
                                    str(dif) +
                                    " " +
                                    elem +
                                    " faltando comparada à " +
                                    master
                                )
                            else:                                                   # Se a diferença for negativa, a Child está com elementos a mais
                                par_erradas.append(
                                    key_check_c +
                                    " está com " +
                                    str(abs(dif)) +
                                    " " +
                                    elem +
                                    " a mais comparada à " +
                                    master
                                )
            else:                                                                   # Se a key de verificação da Master não consta no dicionário criado pelos elementos do modelo, ela consta no JSON, mas não existe mais no modelo (pode ter sido apagada, paredes renumeradas ou outro motivo), mostrando incompatibilidade entre o valor do 'ParedesIguais' e o que está modelado no projeto. Provalvemente igualou e depois mudou o projeto.
                par_erradas.append(                                                 # Nesse caso, eu ainda adiciono à lista de paredes erradas, mas com uma mensagem diferente, sem contar elementos.
                    "** " +
                    key_check_m +                                                   # Quebrei o texto para manter alinhamento de comentários
                    " não encontrada no projeto, mas consta no paredes igualadas." +
                    "Atualize as paredes iguais para considerar corretamente **"
                )

    if not par_erradas and not elem_sem_nivel:                                      # Para dar a saída ao usuário, eu verifico se não temos elementos em par_erradas nem elem_sem_nivel
        forms.alert(msg = "Todas as paredes do projeto estão OK!",
                    title = "Parabéns!")                                            # Se não tiver, eu falo que ta tudo OK
    else:                                                                           # Se tiver, eu dou uma caixa de diálogo com duas opções, clicar Sim ou Não.
        escolha = forms.alert(msg = "Deseja salvar um arquivo TXT para visualizar?",
                              title = "Relatório de Elementos de Paredes Iguais",
                              sub_msg = "'Sim' - arquivo será salvo na pasta RevitProjects do seu usuário.\n'Não' será apenas exibido em um popup as inconformidades.",
                              yes=True,
                              no=True
                              )
        if escolha:                                                                 # Com base na escolha do usuário, ou eu crio o TXT e abro ele, ou eu simplesmente mostro o popup com as paredes erradas
            import os, codecs
            user_name = os.environ['USERNAME']                                      # Pegar usuário do Windows, para usar no caminho da pasta

            full_doc_path = doc.PathName                                            # ex.: C:\Projetos\RM1234_Modelo.rvt
            name_file = os.path.basename(full_doc_path)                             # RM1234_Modelo.rvt
            name_modelo = os.path.splitext(name_file)[0]                            # RM1234_Modelo

            caminho_s = os.path.join("C:\\RevitProjects",                           # Criando o caminho para salvar, em RevitProjects, na pasta do usuário
                                     user_name,
                                     "Relatório Elementos de Paredes Iguais - " +
                                     name_modelo +
                                     ".txt"
                                     )
            with codecs.open(caminho_s, 'w', 'utf-8') as f:
                f.write("Arquivo salvo na pasta RevitProjects, no C: deste computador, em: \n" +
                        caminho_s +
                        "\n\n" +
                        "\n".join(par_erradas))                                     # Escrevendo no arquivo TXT
            os.startfile(caminho_s)                                                 # Abrir o txt
        else:
            forms.alert(msg = "\n".join(par_erradas + elem_sem_nivel),
                        title="Lista de inconformidades: [PAVIMENTO] - [PAREDE] - [QUANTIDADE] - [ELEMENTO] - [+ ou -]")