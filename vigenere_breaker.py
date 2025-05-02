#!/usr/bin/env python3
"""
Break Vigenère cipher using Kasiski and frequency analysis.

Usage:
    python vigenere_breaker.py <cipherfile> <freqfile> [max_key_len]
Example:
    python vigenere_breaker.py 2977-4.txt frequencia.txt 20

- <cipherfile>: path to the cipher text file
- <freqfile>: path to the letter frequency file (e.g., frequencia.txt)
- [max_key_len]: optional maximum key length to test (default: 20)
"""

import sys      
import string  
from collections import Counter

# Load and clean ciphertext: keep only A–Z letters in uppercase
def load_text(filename):
    # Read entire file content with UTF-8 encoding
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
      
    # Filter out non-alphabetic characters and convert to uppercase
    return ''.join(c for c in text.upper() if c.isalpha())

# Load letter frequency distribution from file
def load_frequencies(filename):
    freqs = {}  # dictionary to store frequency for each letter
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()           # remove leading/trailing whitespace
            if not line:                  # skip empty lines
                continue
            parts = line.split(':')       # expect format 'A:12.34%'
            letter = parts[0].upper()     # letter key (A–Z)
          
            # remove '%' and convert percentage to fraction
            value = float(parts[1].strip().strip('%')) / 100.0
            freqs[letter] = value         # store in dictionary
          
    # Ensure every uppercase letter has an entry (default 0.0)
    for l in string.ascii_uppercase:
        freqs.setdefault(l, 0.0)
      
    return freqs

# Compute Index of Coincidence (IC) for a text segment
def index_of_coincidence(text):
    N = len(text)             # total number of letters
    freqs = Counter(text)     # count frequency of each letter
    
    if N < 2:                 # avoid division by zero
        return 0.0
    
    # IC formula: sum(f_i * (f_i - 1)) / (N * (N - 1))
    return sum(f * (f - 1) for f in freqs.values()) / (N * (N - 1))

# Compute average IC across all segments for a given key length
def avg_ic_for_keylen(text, keylen):
    ics = []  # list to store IC of each segment
    for i in range(keylen):
        segment = text[i::keylen]           # take every keylen-th letter starting at i
        ics.append(index_of_coincidence(segment))
    
    return sum(ics) / len(ics) # average of IC values

# Estimate key length by comparing average IC to target IC (~0.07797 for English)
def find_key_length(text, max_len=20, target_ic=0.07797):
    ic_table = {}                               # map: key length -> average IC
    
    for k in range(1, max_len + 1):
        ic_table[k] = avg_ic_for_keylen(text, k)  # compute and store IC
    
    # choose the key length whose IC is closest to typical English IC
    best_k = min(ic_table, key=lambda k: abs(ic_table[k] - target_ic))
    return best_k, ic_table

# Compute chi-squared statistic between observed and expected frequencies
def chi_squared_stat(segment, freqs):
    N = len(segment)
    obs = Counter(segment)  # observed counts for each letter in the segment
    chi2 = 0.0
    
    for l in string.ascii_uppercase:
        observed = obs.get(l, 0)
        expected = freqs.get(l, 0.0) * N  # expected count based on language model
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected
    
    return chi2


# Determine the Vigenère key by minimizing chi-squared for each segment
def find_key(text, keylen, freqs):
    key = []  # list to build the key letters
    for i in range(keylen):
        segment = text[i::keylen]  # letters encrypted by the same key character
        # test all 26 shifts; pick the one with lowest chi-squared value
        best_shift = min(
            range(26),
            key=lambda s: chi_squared_stat(
                ''.join(
                    chr((ord(c) - ord('A') - s) % 26 + ord('A'))
                    for c in segment
                ), freqs
            )
        )
        key.append(chr(best_shift + ord('A')))  # convert shift back to letter
    return ''.join(key)

# Decrypt full ciphertext using the found key
def decrypt(text, key):
    plaintext = []
    shifts = [ord(c) - ord('A') for c in key]  # numeric shifts for each key letter
    
    for i, c in enumerate(text):
        k = shifts[i % len(shifts)]             # key shift cycles through key
        # reverse shift to get plaintext letter
        p = chr((ord(c) - ord('A') - k) % 26 + ord('A'))
        plaintext.append(p)
    
    return ''.join(plaintext)

def main():
    # require at least ciphertext and frequency files
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    cipherfile = sys.argv[1]                # path to cipher text
    freqfile = sys.argv[2]                  # path to letter frequency file
    max_key_len = int(sys.argv[3]) if len(sys.argv) > 3 else 20  # optional max key length

    # Load data
    text = load_text(cipherfile)            # cleaned ciphertext
    freqs = load_frequencies(freqfile)      # language frequency model

    # Guess key length
    best_k, ic_table = find_key_length(text, max_key_len)
    print(f"Estimated key length: {best_k}")
    print("IC values for tested key lengths:")
    for k, v in sorted(ic_table.items()):
        print(f"  Length {k}: IC = {v:.5f}")

    # Find key and decrypt
    key = find_key(text, best_k, freqs)
    print(f"Estimated key: {key}")
    plaintext = decrypt(text, key)

    # Write decrypted text to file
    with open('decrypted.txt', 'w', encoding='utf-8') as f:
        f.write(plaintext)
    print("Decrypted text written to decrypted.txt")

# run main if executed as a script
if __name__ == '__main__':
    main()