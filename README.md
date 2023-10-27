# Modification of python captcha library <br>
Original project available here: https://github.com/lepture/captcha
## Modification
The purpose of this modification is to generate similar CAPTCHA images to those used by server uloz.to in order to train a model.
## Use
In main.py in function generate_captcha you need to specify number of pictures and a character set. The program will create a dataset directory and store all generated images inside in png format. The number of characters or the image format can be easily modified inside the generate_captcha function if needed.
