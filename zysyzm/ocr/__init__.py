#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.__init__.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################## FUNCTIONS ##################################
def convert_8bit_grayscale_to_2bit(image):
    """
    Sets palette of a four-color grayscale image to [0, 85, 170, 255]

    Args:
        image(PIL.Image.Image): 4-color grayscale source image

    Returns (PIL.Image.Image): image with [0, 85, 170, 255] palette

    """
    import numpy as np
    from PIL import Image

    raw = np.array(image)
    raw[raw < 42] = 0
    raw[np.logical_and(raw >= 42, raw < 127)] = 85
    raw[np.logical_and(raw >= 127, raw <= 212)] = 170
    raw[raw > 212] = 255

    image = Image.fromarray(raw, mode=image.mode)
    return image


def adjust_2bit_grayscale_palette(image):
    """
    Sets palette of a four-color grayscale image to [0, 85, 170, 255]

    Args:
        image(PIL.Image.Image): 4-color grayscale source image

    Returns (PIL.Image.Image): image with [0, 85, 170, 255] palette

    """
    import numpy as np
    from PIL import Image

    raw = np.array(image)
    input_shades = np.where(np.bincount(raw.flatten()) != 0)[0]
    output_shades = [0, 85, 170, 255]

    for input_shade, output_shade in zip(input_shades, output_shades):
        raw[raw == input_shade] = output_shade

    image = Image.fromarray(raw, mode=image.mode)
    return image


def trim_image(image, background_color=None):
    """
    Trims outer rows and columns of an image based on background color

    Args:
        image (PIL.Image.Image): source image

    Returns (PIL.Image.Image): trimmed image

    """
    from PIL import Image, ImageChops

    if background_color is None:
        background_color = image.getpixel((0, 0))

    background = Image.new(image.mode, image.size, background_color)
    diff = ImageChops.difference(image, background)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()

    if bbox:
        return image.crop(bbox)


def resize_image(image, new_size, x_offset=0, y_offset=0):
    """
    Resizes an image, keeping current contents centered

    Args:
        image (PIL.Image.Image): source image
        new_size (tuple(int, int)): New width and height

    Returns (PIL.Image.Image): resized image

    """
    import numpy as np
    from PIL import Image

    x = int(np.floor((new_size[0] - image.size[0]) / 2))
    y = int(np.floor((new_size[1] - image.size[1]) / 2))
    new_image = Image.new(image.mode, new_size, image.getpixel((0, 0)))
    new_image.paste(image, (x + x_offset,
                            y + y_offset,
                            x + image.size[0] + x_offset,
                            y + image.size[1] + y_offset))

    return new_image
