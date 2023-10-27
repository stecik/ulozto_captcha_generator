from string import ascii_lowercase, ascii_uppercase
from captcha.image import ImageCaptcha
from random import choice
from uuid import uuid4


def rand_string(characters, length):
    string = ""
    for i in range(length):
        string += choice(characters)
    return string


def generate_captcha(count, characters):
    for i in range(count):
        cap = ImageCaptcha()
        text = rand_string(characters, 4)
        name = f"{text}_{str(uuid4())}"
        cap.write(text, f"dataset/{name}.png")


if __name__ == "__main__":
    charset = list(ascii_lowercase + ascii_uppercase)
    generate_captcha(100000, charset)
