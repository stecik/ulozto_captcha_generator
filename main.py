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
        cap.write(text, f"dataset10/{name}.png")

charset0 = list(ascii_lowercase + ascii_uppercase)
charset1 = ["B", "p", "q", "b", "d", "g"]
charset2 = ["r", "n", "u", "h", "m", "v"]
charset3 = ["O", "o", "D", "B", "a", "Q"]
charset4 = charset1 + charset2 + charset3
charset5 = ["p", "p", "m", "q", "Q", "h"] + charset0
charset6 = ["p"]

# generate_captcha(15000, charset1)
# generate_captcha(15000, charset2)
# generate_captcha(15000, charset3)
generate_captcha(100000, charset6)
