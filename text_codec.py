#!/usr/bin/env python3
"""
Assignment 3 - Text Encoder / Decoder
=====================================
A menu-driven program that encodes and decodes text using several
well-known algorithms:

  1. Caesar Cipher      (substitution, shift key)
  2. ROT13              (Caesar with fixed shift of 13)
  3. Atbash Cipher      (reverse-alphabet substitution)
  4. Vigenere Cipher    (polyalphabetic substitution, keyword)
  5. Rail Fence Cipher  (transposition, number of rails)
  6. Morse Code         (dot/dash encoding)
  7. Base64             (binary-to-text encoding)
  8. Binary             (8-bit ASCII/UTF-8 representation)
  9. Hexadecimal        (hex representation)

Run:  python text_codec.py
"""

import base64
import string

UPPER = string.ascii_uppercase
LOWER = string.ascii_lowercase


# --------------------------------------------------------------------------
# 1. Caesar cipher
# --------------------------------------------------------------------------
def _shift_char(ch: str, shift: int) -> str:
    """Shift a single letter by `shift` positions, keeping its case."""
    if ch in UPPER:
        return UPPER[(UPPER.index(ch) + shift) % 26]
    if ch in LOWER:
        return LOWER[(LOWER.index(ch) + shift) % 26]
    return ch  # digits, spaces, punctuation stay unchanged


def caesar_encode(text: str, shift: int) -> str:
    return "".join(_shift_char(c, shift) for c in text)


def caesar_decode(text: str, shift: int) -> str:
    return caesar_encode(text, -shift)


# --------------------------------------------------------------------------
# 2. ROT13 (self-inverse)
# --------------------------------------------------------------------------
def rot13(text: str) -> str:
    return caesar_encode(text, 13)


# --------------------------------------------------------------------------
# 3. Atbash (self-inverse): A<->Z, B<->Y, ...
# --------------------------------------------------------------------------
def atbash(text: str) -> str:
    table = str.maketrans(UPPER + LOWER, UPPER[::-1] + LOWER[::-1])
    return text.translate(table)


# --------------------------------------------------------------------------
# 4. Vigenere cipher
# --------------------------------------------------------------------------
def _vigenere(text: str, key: str, decode: bool) -> str:
    key = "".join(c for c in key.lower() if c.isalpha())
    if not key:
        raise ValueError("Vigenere key must contain at least one letter.")
    result, k = [], 0
    for ch in text:
        if ch.isalpha() and ch in UPPER + LOWER:
            shift = LOWER.index(key[k % len(key)])
            result.append(_shift_char(ch, -shift if decode else shift))
            k += 1  # only advance the key on letters
        else:
            result.append(ch)
    return "".join(result)


def vigenere_encode(text: str, key: str) -> str:
    return _vigenere(text, key, decode=False)


def vigenere_decode(text: str, key: str) -> str:
    return _vigenere(text, key, decode=True)


# --------------------------------------------------------------------------
# 5. Rail Fence cipher
# --------------------------------------------------------------------------
def _rail_pattern(length: int, rails: int):
    """Return the rail index used by each character position (zig-zag)."""
    pattern, rail, step = [], 0, 1
    for _ in range(length):
        pattern.append(rail)
        if rail == 0:
            step = 1
        elif rail == rails - 1:
            step = -1
        rail += step
    return pattern


def rail_fence_encode(text: str, rails: int) -> str:
    if rails < 2 or rails >= max(len(text), 3):
        return text
    pattern = _rail_pattern(len(text), rails)
    return "".join(
        text[i] for r in range(rails) for i in range(len(text)) if pattern[i] == r
    )


def rail_fence_decode(text: str, rails: int) -> str:
    if rails < 2 or rails >= max(len(text), 3):
        return text
    pattern = _rail_pattern(len(text), rails)
    order = sorted(range(len(text)), key=lambda i: pattern[i])  # positions by rail
    result = [""] * len(text)
    for char, pos in zip(text, order):
        result[pos] = char
    return "".join(result)


# --------------------------------------------------------------------------
# 6. Morse code
# --------------------------------------------------------------------------
MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..", "!": "-.-.--", "'": ".----.",
    "/": "-..-.", ":": "---...", "-": "-....-", "(": "-.--.", ")": "-.--.-",
}
MORSE_REVERSE = {v: k for k, v in MORSE.items()}


def morse_encode(text: str) -> str:
    """Letters separated by a space, words separated by ' / '."""
    words = []
    for word in text.upper().split():
        words.append(" ".join(MORSE[c] for c in word if c in MORSE))
    return " / ".join(words)


def morse_decode(code: str) -> str:
    words = code.strip().split(" / ")
    return " ".join(
        "".join(MORSE_REVERSE.get(sym, "?") for sym in word.split())
        for word in words
    )


# --------------------------------------------------------------------------
# 7. Base64
# --------------------------------------------------------------------------
def base64_encode(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def base64_decode(text: str) -> str:
    return base64.b64decode(text.encode("ascii"), validate=True).decode("utf-8")


# --------------------------------------------------------------------------
# 8. Binary (8 bits per byte, UTF-8)
# --------------------------------------------------------------------------
def binary_encode(text: str) -> str:
    return " ".join(f"{b:08b}" for b in text.encode("utf-8"))


def binary_decode(bits: str) -> str:
    chunks = bits.split()
    if any(len(c) != 8 or set(c) - {"0", "1"} for c in chunks):
        raise ValueError("Binary input must be groups of 8 bits (0/1) separated by spaces.")
    return bytes(int(c, 2) for c in chunks).decode("utf-8")


# --------------------------------------------------------------------------
# 9. Hexadecimal
# --------------------------------------------------------------------------
def hex_encode(text: str) -> str:
    return text.encode("utf-8").hex(" ")


def hex_decode(text: str) -> str:
    return bytes.fromhex(text).decode("utf-8")


# --------------------------------------------------------------------------
# Menu / user interface
# --------------------------------------------------------------------------
# name -> (encode_fn, decode_fn, parameter prompt or None, parameter type)
ALGORITHMS = {
    "1": ("Caesar Cipher", caesar_encode, caesar_decode, "Shift (integer)", int),
    "2": ("ROT13", rot13, rot13, None, None),
    "3": ("Atbash Cipher", atbash, atbash, None, None),
    "4": ("Vigenere Cipher", vigenere_encode, vigenere_decode, "Keyword (letters)", str),
    "5": ("Rail Fence Cipher", rail_fence_encode, rail_fence_decode, "Number of rails (>=2)", int),
    "6": ("Morse Code", morse_encode, morse_decode, None, None),
    "7": ("Base64", base64_encode, base64_decode, None, None),
    "8": ("Binary", binary_encode, binary_decode, None, None),
    "9": ("Hexadecimal", hex_encode, hex_decode, None, None),
}


def read_param(prompt: str, kind):
    """Keep asking until the parameter is valid."""
    while True:
        raw = input(f"  {prompt}: ").strip()
        try:
            return kind(raw)
        except ValueError:
            print("  Invalid value, please try again.")


def show_menu() -> None:
    print("\n" + "=" * 44)
    print("        TEXT ENCODER / DECODER")
    print("=" * 44)
    for key, (name, *_rest) in ALGORITHMS.items():
        print(f"  {key}. {name}")
    print("  0. Exit")


def main() -> None:
    while True:
        show_menu()
        choice = input("\nChoose an algorithm: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        if choice not in ALGORITHMS:
            print("Invalid choice, try again.")
            continue

        name, enc, dec, param_prompt, param_type = ALGORITHMS[choice]
        mode = input("Encode or Decode? (e/d): ").strip().lower()
        if mode not in ("e", "d"):
            print("Please enter 'e' or 'd'.")
            continue

        text = input("Enter text: ")
        try:
            args = (read_param(param_prompt, param_type),) if param_prompt else ()
            func = enc if mode == "e" else dec
            result = func(text, *args)
            print(f"\n[{name} - {'Encoded' if mode == 'e' else 'Decoded'}]")
            print(result)
        except Exception as exc:  # bad input for the chosen algorithm
            print(f"\nError: {exc}")


if __name__ == "__main__":
    main()
