import sys
import os
from PIL import Image


def ascii_welcome():
    # Open the LPD logo image file
    scriptDir = os.path.dirname(os.path.realpath("control_app.py"))
    img = Image.open(scriptDir + os.path.sep + 'extras/icons/LPD_LOGO.jpeg')

    # Resize the image to fit perfectly inside the user's terminal screen
    width, height = img.size
    aspect_ratio = height/width
    new_width = int(os.get_terminal_size()[0])
    new_height = aspect_ratio * new_width * 0.5
    img = img.resize((new_width, int(new_height)))

    # Convert image to greyscale format
    img = img.convert('L')
    pixels = img.getdata()

    # Replace each pixel with a character
    new_pixels = [" " if pixel == 0 else "@" for pixel in pixels]
    new_pixels = ''.join(new_pixels)

    # Split string of chars into multiple strings of length equal to new width and create a list
    new_pixels_count = len(new_pixels)
    ascii_image = [new_pixels[index:index + new_width] for index in range(0, new_pixels_count, new_width)]
    ascii_image = "\n".join(ascii_image)

    # Printing the full welcome text
    print("*"*os.get_terminal_size()[0])
    print("*"*os.get_terminal_size()[0], '\n')
    print(ascii_image, '\n\n\n')
    print(" * AUTHOR: ------------- PEDRO V. PINHO")
    print(" * CONTACT: ------------ ppinho@ifi.unicamp.br")
    print(" * DOCUMENTATION: ------ https://github.com/PedroPinh0/Suruga-Controller \n")
    print("      *** HAVE FUN *** \n")
    print("\n SURUGA CONTROLLER LOG: \n _____________________")
    print("")
ascii_welcome()
