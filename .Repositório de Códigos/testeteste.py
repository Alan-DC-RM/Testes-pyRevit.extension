lista = [1, 2, 3, 4]

for num in lista:
    print(lista)
    if num < 4:
        lista.append(num + 10)

print(lista)