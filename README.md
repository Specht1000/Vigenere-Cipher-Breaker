# Vigenère Cipher Breaker

Este script em Python implementa a quebra de cifras de Vigenère usando análise do Índice de Coincidência e estatística qui-quadrado.

## Requisitos

* Python 3.x instalado no sistema.

## Uso

### Windows

Abra o Prompt de Comando e execute:

```bash
python vigenere_breaker.py <cipherfile> <freqfile> [max_key_len]
```

### Linux e macOS

Abra o terminal e execute:

```bash
python3 vigenere_breaker.py <cipherfile> <freqfile> [max_key_len]
```

* `<cipherfile>`: caminho para o arquivo de texto cifrado (ex.: `2977-4.txt`).
* `<freqfile>`: arquivo com frequências de letras (ex.: `frequencia.txt`).
* `[max_key_len]`: comprimento máximo de chave a testar (opcional, padrão: 20).

## Exemplo

```bash
# Windows
python vigenere_breaker.py 2977-4.txt frequencia.txt 20

# Linux/macOS
$ python3 vigenere_breaker.py 2977-4.txt frequencia.txt 20
```

## Saída

* Exibe no console o tamanho de chave estimado, valores de IC e a palavra-chave encontrada.
* Gera o arquivo `decrypted.txt` com o texto decifrado.
