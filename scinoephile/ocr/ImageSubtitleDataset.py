#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.ImageSubtitleDataset.py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile import SubtitleDataset
from scinoephile.ocr import ImageSubtitleSeries
from IPython import embed


################################### CLASSES ###################################
class ImageSubtitleDataset(SubtitleDataset):
    """
    Represents a collection of image-based subtitles

    TODO:
      - [ ] Document
    """

    # region Instance Variables
    help_message = ("Represents a collection of image-based subtitles")
    series_class = ImageSubtitleSeries

    # endregion

    # region Builtins
    def __init__(self, image_mode=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if image_mode is not None:
            self.image_mode = image_mode

    # endregion

    # region Public Properties

    @property
    def image_mode(self):
        """str: Image mode"""
        if not hasattr(self, "_image_mode"):
            self._image_mode = "1 bit"
        return self._image_mode

    @image_mode.setter
    def image_mode(self, value):
        if value is not None:
            if not isinstance(value, str):
                try:
                    value = str(value)
                except Exception:
                    raise ValueError(self._generate_setter_exception(value))
            if value == "8 bit":
                pass
            elif value == "1 bit":
                pass
            else:
                raise ValueError(self._generate_setter_exception(value))
        # TODO: If changed, change on self.subtitles

        self._image_mode = value

    @property
    def subtitles(self):
        """pandas.core.frame.DataFrame: Subtitles"""
        if not hasattr(self, "_subtitles"):
            self._subtitles = self.series_class(image_mode=self.image_mode,
                                                verbosity=self.verbosity)
        return self._subtitles

    @subtitles.setter
    def subtitles(self, value):
        if value is not None:
            if not isinstance(value, self.series_class):
                raise ValueError()
        self._subtitles = value

    # endregion

    # region Public Methods

    def load(self, infile=None):
        from os.path import expandvars

        # Process arguments
        if infile is not None:
            infile = expandvars(infile)
        elif self.infile is not None:
            infile = self.infile
        else:
            raise ValueError()

        # Load infile
        if self.verbosity >= 1:
            print(f"Reading subtitles from '{infile}'")
        self.subtitles = self.series_class.load(infile,
                                                image_mode=self.image_mode,
                                                verbosity=self.verbosity)
        self.subtitles.verbosity = self.verbosity

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    ImageSubtitleDataset.main()