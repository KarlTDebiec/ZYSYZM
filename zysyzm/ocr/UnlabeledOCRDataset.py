#!/usr/bin/python
# -*- coding: utf-8 -*-
#   zysyzm.ocr.UnlabeledOCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from zysyzm.ocr import OCRDataset
from IPython import embed


################################### CLASSES ###################################
class UnlabeledOCRDataset(OCRDataset):
    """
    Represents a collection of unlabeled character images

    Todo:
      - [x] Read image directory
      - [x] Add images
      - [x] Write hdf5
      - [x] Read hdf5
      - [ ] Write image directory
      - [ ] Document
    """

    # region Instance Variables

    help_message = ("Represents a collection of unlabeled character images")

    # endregion

    # region Builtins

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.input_image_directory = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/magnificent_mcdull"
        # self.input_hdf5 = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/magnificent_mcdull/unlabeled.h5"
        # self.output_hdf5 = \
        #     "/Users/kdebiec/Desktop/docs/subtitles/magnificent_mcdull/unlabeled.h5"

    def __call__(self):
        """ Core logic """

        # Input
        if self.input_hdf5 is not None:
            self.read_hdf5()
        if self.input_image_directory is not None:
            self.read_image_directory()

        # Output
        if self.output_hdf5 is not None:
            self.write_hdf5()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)

    # endregion

    # region Properties

    @property
    def char_image_spec_columns(self):
        """list(str): Character image specification columns"""

        if hasattr(self, "_char_image_specs"):
            return self.char_image_specs.columns.values
        else:
            return ["path"]

    # endregion

    # Private Methods

    def _read_hdf5_spec_formatter(self, columns):
        """Formats spec for compatibility with both numpy and h5py"""
        columns = list(columns)

        if "path" in columns:
            path_index = columns.index("path")

            def func(x):
                x = list(x)
                x[path_index] = x[path_index].decode("utf8")
                return tuple(x)
        else:
            def func(x):
                return tuple(x)

        return func

    def _read_image_directory_infiles(self, path):
        """Provides infiles within path"""
        from glob import iglob

        return sorted(iglob(f"{path}/**/[0-9][0-9].png", recursive=True))

    def _read_image_directory_specs(self, infiles):
        """Provides specs of infiles"""
        import pandas as pd

        return pd.DataFrame(data=infiles,
                            index=range(len(infiles)),
                            columns=self.char_image_spec_columns)

    def _write_hdf5_spec_dtypes(self, columns):
        """Provides spec dtypes compatible with both numpy and h5py"""
        dtypes = {"path": "S255"}
        return list(zip(columns, [dtypes[k] for k in columns]))

    def _write_hdf5_spec_formatter(self, columns):
        """Provides spec formatter compatible with both numpy and h5py"""
        columns = list(columns)

        if "path" in columns:
            path_index = columns.index("path")

            def func(x):
                x = list(x)
                x[path_index] = x[path_index].encode("utf8")
                return tuple(x)
        else:
            def func(x):
                return tuple(x)

        return func

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    UnlabeledOCRDataset.main()
