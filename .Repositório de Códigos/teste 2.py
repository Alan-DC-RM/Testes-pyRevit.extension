dic = {
    "par1":{
        "Par 1 - 1ªa fiada - Level X" : [1,2,3]
    },
    "par2":{
        "Par 2 - 1ªa fiada - Level X" : [4,5,6]
    },
    "par3": {
        "Par 3 - 1ªa fiada - Level X": [7, 8, 9]
    },
    "par5": {
        "Par 5 - 1ªa fiada - Level X": [10, 11, 12]
    }
}

for parede in dic:
    for nome in dic[parede]:
        print(nome)
        print(dic[parede][nome])
"""

for parede, nome in dic.items():
    print(parede)
    print(nome.items())
"""