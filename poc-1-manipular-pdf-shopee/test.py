import re

# Sua string de entrada
input_string = '[1] Product Name:Chinelo Nuvem Em Eva Masculino e Feminino Chinelo Slide em Eva; Variation Name:Verde Militar,43/44 (Medida de 29,5 cm); Price: R$ 52.90; Quantity: 1; SKU Reference No.: CH200/202-VMM-44; Parent SKU Reference No.: CH200/202-1; '

# Usando uma expressão regular para dividir a string em partes
parts = re.split(r'(?=\[\d+\])', input_string)

# Limpando partes vazias, se houver
parts = [part.strip() for part in parts if part.strip()]

# Exibindo o resultado
for part in parts:
    print(part)
    print()