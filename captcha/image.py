# coding: utf-8
"""
    captcha.image
    ~~~~~~~~~~~~~

    Generate Image CAPTCHAs, just the normal image CAPTCHAs you are using.
"""

import os
import random
from PIL import Image, ImageOps
from PIL import ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
from pathlib import Path
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO
try:
    from wheezy.captcha import image as wheezy_captcha
except ImportError:
    wheezy_captcha = None

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
DEFAULT_FONTS = [os.path.join(DATA_DIR, 'DroidSansMono.ttf')]
print(DEFAULT_FONTS)
FONT_DIR = Path("./fonts/")
MY_FONTS = list(map(str, list(FONT_DIR.glob("*.ttf"))))
print(MY_FONTS)

if wheezy_captcha:
    __all__ = ['ImageCaptcha', 'WheezyCaptcha']
else:
    __all__ = ['ImageCaptcha']


table  =  []
for  i  in  range( 256 ):
    table.append( int(i * 1.97) )


class _Captcha(object):
    def generate(self, chars, format='png'):
        """Generate an Image Captcha of the given characters.

        :param chars: text to be generated.
        :param format: image file format
        """
        im = self.generate_image(chars)
        out = BytesIO()
        im.save(out, format=format)
        out.seek(0)
        return out

    def write(self, chars, output, format='png'):
        """Generate and write an image CAPTCHA data to the output.

        :param chars: text to be generated.
        :param output: output destination.
        :param format: image file format
        """
        im = self.generate_image(chars)
        return im.save(output, format=format)


class WheezyCaptcha(_Captcha):
    """Create an image CAPTCHA with wheezy.captcha."""
    def __init__(self, width=350, height=140, fonts=None):
        self._width = width
        self._height = height
        self._fonts = fonts or MY_FONTS

    def generate_image(self, chars):
        text_drawings = [
            wheezy_captcha.warp(),
            wheezy_captcha.rotate(),
            wheezy_captcha.offset(),
        ]
        fn = wheezy_captcha.captcha(
            drawings=[
                wheezy_captcha.background(),
                wheezy_captcha.text(fonts=self._fonts, drawings=text_drawings),
                wheezy_captcha.curve(),
                wheezy_captcha.noise(),
                wheezy_captcha.smooth(),
            ],
            width=self._width,
            height=self._height,
        )
        return fn(chars)


class ImageCaptcha(_Captcha):
    """Create an image CAPTCHA.

    Many of the codes are borrowed from wheezy.captcha, with a modification
    for memory and developer friendly.

    ImageCaptcha has one built-in font, DroidSansMono, which is licensed under
    Apache License 2. You should always use your own fonts::

        captcha = ImageCaptcha(fonts=['/path/to/A.ttf', '/path/to/B.ttf'])

    You can put as many fonts as you like. But be aware of your memory, all of
    the fonts are loaded into your memory, so keep them a lot, but not too
    many.

    :param width: The width of the CAPTCHA image.
    :param height: The height of the CAPTCHA image.
    :param fonts: Fonts to be used to generate CAPTCHA images.
    :param font_sizes: Random choose a font size from this parameters.
    """
    def __init__(self, width=350, height=140, fonts=None, font_sizes=None):
        self._width = width
        self._height = height
        self._fonts = fonts or MY_FONTS
        self._font_sizes = font_sizes or (71, 83, 90)
        self._truefonts = []

    @property
    def truefonts(self):
        if self._truefonts:
            return self._truefonts
        self._truefonts = tuple([
            truetype(n, s)
            for n in self._fonts
            for s in self._font_sizes
        ])
        return self._truefonts

    def create_noise_curve(self, image, color, line_width):
        w, h = image.size
        offset_choice = [random.randint(10, 100), 0]
        finished = False
        chance = random.randint(0, 3)
        w_margin = 100
        h_margin = 50
        x1, x2 = self._set_x_coord(offset_choice, chance, h_margin, w_margin, h, w)
        while not finished:
            y1, y2, finished = self._set_y_coord(chance, x1, x2, w, h)
            Draw(image).line(((x1, x2), (y1, y2)), fill=color, width=line_width)
            x1 = y1
            x2 = y2

        return image

    def _set_x_coord(self, offset_choice, chance, h_margin, w_margin, h, w):
        if chance == 0:
            x1 = 0 + offset_choice[random.randint(0,1)]
            x2 = random.randint(0, h - h_margin)
        elif chance == 1:
            x1 = random.randint(w_margin, w)
            x2 = 0 + offset_choice[random.randint(0,1)]
        elif chance == 2:
            x1 = w - offset_choice[random.randint(0,1)]
            x2 = random.randint(0, h - h_margin)
        else:
            x1 = random.randint(0, w - w_margin)
            x2 = h - offset_choice[random.randint(0,1)]

        return x1, x2

    def _set_y_coord(self, chance, x1, x2, w, h):
        finished = False
        rand_w = random.randint(4, 20)
        rand_h = random.randint(1, 10)
        if chance == 0:
            y1 = x1 + rand_w
            y2 = x2 + rand_h
            if y1 >= w:
                y1 = w
                finished = True
            if y2 >= h:
                y2 = h
                finished = True
        elif chance == 1:
            y1 = x1 - rand_w
            y2 = x2 + rand_h
            if y1 <= 0:
                y1 = 0
                finished = True
            if y2 >= h:
                y2 = h
                finished = True
        elif chance == 2:
            y1 = x1 - rand_w
            y2 = x2 - rand_h
            if y1 <= 0:
                y1 = 0
                finished = True
            if y2 <= 0:
                y2 = 0
                finished = True
        else:
            y1 = x1 + rand_w
            y2 = x2 - rand_h
            if y1 >= w:
                y1 = w
                finished = True
            if y2 <= 0:
                y2 = 0
                finished = True

        return y1, y2, finished

    def create_noise_dots(self, image, color, max_width=2, number=600):
        draw = Draw(image)
        w, h = image.size
        while number:
            width = random.randint(1, max_width)
            x1 = random.randint(0, w)
            y1 = random.randint(0, h)
            draw.line(((x1, y1), (x1 + random.randint(-2, 2), y1 + random.randint(-2,2))), fill=color, width=width)
            draw.line(((x1 + random.randint(-2, 2), y1 + random.randint(-2, 2)), (x1, y1)), fill=color, width=width)
            number -= 1
        return image

    def create_captcha_image(self, chars, color, background):
        """Create the CAPTCHA image itself.

        :param chars: text to be generated.
        :param color: color of the text.
        :param background: color of the background.

        The color should be a tuple of 3 numbers, such as (0, 255, 255).
        """
        image = Image.new('RGBA', (self._width, self._height), background)
        draw = Draw(image)

        def _draw_character(c):
            font = random.choice(self.truefonts)
            w, h = draw.textsize(c, font=font)

            dx = random.randint(0, 4)
            dy = random.randint(0, 6)
            im = Image.new('RGBA', (w + dx, h + dy))

            Draw(im).text((dx, dy), c, font=font, fill=color)

            # rotate
            im = im.crop(im.getbbox())
            im = im.rotate(random.uniform(-10, 10), Image.BILINEAR, expand=1)

            # warp
            dx = w * random.uniform(0.1, 0.3)
            dy = h * random.uniform(0.2, 0.3)
            x1 = int(random.uniform(-dx, dx))
            y1 = int(random.uniform(-dy, dy))
            x2 = int(random.uniform(-dx, dx))
            y2 = int(random.uniform(-dy, dy))
            w2 = w + abs(x1) + abs(x2)
            h2 = h + abs(y1) + abs(y2)
            data = (
                x1, y1,
                -x1, h2 - y2,
                w2 + x2, h2 + y2,
                w2 - x2, -y1,
            )
            im = im.resize((w2, h2))
            im = im.transform((w, h), Image.QUAD, data)
            return im

        images = []
        images.append(_draw_character(" "))
        for c in chars:
            images.append(_draw_character("  "))
            images.append(_draw_character(c))

        # for c in chars:
        #     if random.random() > 0.5:
        #         images.append(_draw_character(" "))
        #     images.append(_draw_character(c))

        text_width = sum([im.size[0] for im in images])

        width = max(text_width, self._width)
        image = image.resize((width, self._height))

        average = int(text_width / len(chars))
        rand = int(0.25 * average)
        offset = int(average * 0.1)

        for im in images:
            w, h = im.size
            mask = im.convert('L').point(table)
            image.paste(im, (offset, int((self._height - h) / 2)), mask)
            offset = offset + w + random.randint(-rand, 0)

        if width > self._width:
            image = image.resize((self._width, self._height))

        return image

    def generate_image(self, chars):
        """Generate the image of the given characters.

        :param chars: text to be generated.
        """
        background = random_color(238, 255)
        color = random_color(10, 200, 255)
        # color = (255,0,0,255)
        # print(color)
        im = self.create_captcha_image(chars, color, background)
        self.create_noise_dots(im, color, number=900, max_width=3)
        self.create_noise_dots(im, self.add_opacity_to_color(color, 50), number=250, max_width=2)
        for i in range(random.randint(4, 9)):
            self.create_noise_curve(im, color, line_width=random.randint(2, 8))
        im = im.filter(ImageFilter.SMOOTH)
        im = self.to_b_and_W(im)
        im.thumbnail((175,70), Image.Resampling.NEAREST)
        return im

    def to_b_and_W(self, im):
        im = ImageOps.grayscale(im)
        w, h = im.size
        for x in range(w):
            for y in range(h):
                pixel = im.getpixel((x, y))
                if pixel > 200:
                    im.putpixel((x, y), (255))
                else:
                    im.putpixel((x, y), (0))
        return im

    def add_opacity_to_color(self, color, opacity):
        r,g,b,o = color
        return (r,g,b,opacity)

def random_color(start, end, opacity=None):
    red = random.randint(start, end)
    green = random.randint(start, end)
    blue = random.randint(start, end)
    if opacity is None:
        return (red, green, blue, 255)
    return (red, green, blue, opacity)
