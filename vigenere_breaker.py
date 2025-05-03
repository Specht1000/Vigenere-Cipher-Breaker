#!/usr/bin/env python3
"""
Quebra a cifra de Vigenère usando análise de Kasiski e de frequência.

Uso:
    python vigenere_breaker.py <cipher_file> <freq_file> [max_key_len]
Exemplo:
    python vigenere_breaker.py 2977-4.txt frequencia.txt 20

- <cipher_file>: caminho para o arquivo de texto cifrado
- <freq_file>: arquivo com as frequências de letras (ex.: frequencia.txt)
- [max_key_len]: comprimento máximo de chave a testar (padrão: 20)
"""

import sys      # acesso a argumentos de linha de comando e saída do sistema
import string   # contém lista de letras ASCII maiúsculas
from collections import Counter  # para contar ocorrências de caracteres

# Carrega e limpa o texto cifrado: mantém apenas letras A–Z em maiúsculo
def load_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    # Filtra caracteres não alfabéticos e converte para maiúsculas
    return ''.join(c for c in text.upper() if c.isalpha())

# Carrega distribuição de frequência de letras de um arquivo
def load_frequencies(filename):
    freqs = {}  # dicionário para armazenar frequência de cada letra
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()           # remove espaços em branco
            if not line:                  # ignora linhas vazias
                continue
            parts = line.split(':')       # formato esperado 'A:12.34%'
            letter = parts[0].upper()      # chave de letra (A–Z)
            # remove '%' e converte porcentagem para fração
            value = float(parts[1].strip().strip('%')) / 100.0
            freqs[letter] = value         # armazena no dicionário
    # Garante que todas as letras maiúsculas estejam presentes (0.0 se ausente)
    for l in string.ascii_uppercase:
        freqs.setdefault(l, 0.0)
    return freqs

# Calcula o Índice de Coincidência (IC) para um segmento de texto
def index_of_coincidence(text):
    N = len(text)             # número total de letras
    freqs = Counter(text)     # conta frequência de cada letra
    if N < 2:                 # evita divisão por zero
        return 0.0
    # Fórmula do IC: sum(f_i * (f_i - 1)) / (N * (N - 1))
    return sum(f * (f - 1) for f in freqs.values()) / (N * (N - 1))

# Calcula o IC médio para um dado comprimento de chave
def avg_ic_for_keylen(text, keylen):
    ics = []  # lista para armazenar IC de cada segmento
    for i in range(keylen):
        segment = text[i::keylen]           # pega cada keylen-ésima letra
        ics.append(index_of_coincidence(segment))
    return sum(ics) / len(ics)  # média dos valores de IC

# Estima o comprimento da chave comparando IC médio ao IC alvo (~0.07797)
def find_key_length(text, max_len=20, target_ic=0.07797):
    ic_table = {}  # mapeia comprimento de chave para IC médio
    for k in range(1, max_len + 1):
        ic_table[k] = avg_ic_for_keylen(text, k)
    # seleciona o comprimento cuja IC está mais próxima do valor alvo
    best_k = min(ic_table, key=lambda k: abs(ic_table[k] - target_ic))
    return best_k, ic_table

# Calcula estatística qui-quadrado entre frequências observadas e esperadas
def chi_squared_stat(segment, freqs):
    N = len(segment)
    obs = Counter(segment)  # contagens observadas de cada letra
    chi2 = 0.0
    for l in string.ascii_uppercase:
        observed = obs.get(l, 0)
        expected = freqs.get(l, 0.0) * N  # contagem esperada pelo modelo
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected
    return chi2

# Determina a chave de Vigenère minimizando qui-quadrado em cada segmento
def find_key(text, keylen, freqs):
    key = []  # lista para construir as letras da chave
    for i in range(keylen):
        segment = text[i::keylen]  # segmento cifrado por mesma letra de chave
        # testa todos os 26 deslocamentos; escolhe o de menor qui-quadrado
        best_shift = min(
            range(26),
            key=lambda s: chi_squared_stat(
                ''.join(
                    chr((ord(c) - ord('A') - s) % 26 + ord('A'))
                    for c in segment
                ), freqs
            )
        )
        key.append(chr(best_shift + ord('A')))  # converte deslocamento para letra
    return ''.join(key)

# Decripta todo o texto usando a chave encontrada
def decrypt(text, key):
    plaintext = []
    shifts = [ord(c) - ord('A') for c in key]  # deslocamentos numéricos da chave
    for i, c in enumerate(text):
        k = shifts[i % len(shifts)]             # ciclo de deslocamento pela chave
        # aplica deslocamento inverso para obter a letra
        p = chr((ord(c) - ord('A') - k) % 26 + ord('A'))
        plaintext.append(p)
    return ''.join(plaintext)

def main():
    if len(sys.argv) < 3:  # requer pelo menos arquivo cifrado e de frequências
        print(__doc__)
        sys.exit(1)
    cipher_file = sys.argv[1]                # caminho do texto cifrado
    freq_file = sys.argv[2]                  # caminho do arquivo de frequências
    max_key_len = int(sys.argv[3]) if len(sys.argv) > 3 else 20  # comprimento máximo

    text = load_text(cipher_file)            # carrega e limpa o texto cifrado
    freqs = load_frequencies(freq_file)      # carrega modelo de frequência

    best_k, ic_table = find_key_length(text, max_key_len)  # estima tamanho da chave
    print(f"Estimated key length: {best_k}")
    print("IC values for tested key lengths:")
    for k, v in sorted(ic_table.items()):
        print(f"  Length {k}: IC = {v:.5f}")

    key = find_key(text, best_k, freqs)    # descobre a chave
    print(f"Estimated key: {key}")
    plaintext = decrypt(text, key)          # decripta o texto

    # grava texto decifrado em arquivo
    with open('decrypted.txt', 'w', encoding='utf-8') as f:
        f.write(plaintext)
    print("Decrypted text written to decrypted.txt")

# executa main quando chamado como script
if __name__ == '__main__':
    main()
