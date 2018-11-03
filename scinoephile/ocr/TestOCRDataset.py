#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.ocr.TestOCRDataset,py
#
#   Copyright (C) 2017-2018 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
from scinoephile.ocr import OCRDataset
from IPython import embed


################################### CLASSES ###################################
class TestOCRDataset(OCRDataset):
    """
    A collection of unlabeled character images
    """

    # region Builtins

    def __init__(self, n_chars=None, model=None, sub_ds=None, **kwargs):
        super().__init__(**kwargs)

        # Store property values
        if n_chars is not None:
            self.n_chars = n_chars

        if model is not None:
            self.model = model
        if sub_ds is not None:
            self.sub_ds = sub_ds

    def __call__(self):
        """ Core logic """

        # Input
        if self.infile is not None:
            self.load()

        # Present IPython prompt
        if self.interactive:
            embed(**self.embed_kw)
        self.label_new_chars()

        # Output
        if self.outfile is not None:
            self.save()

    # endregion

    # region Public Properties

    @property
    def model(self):
        """scinoephile.ocr.Model: model"""
        if not hasattr(self, "_model"):
            self._model = None
        return self._model

    @model.setter
    def model(self, value):
        from scinoephile.ocr import Model

        if value is not None:
            if not isinstance(value, Model):
                raise ValueError(self._generate_setter_exception(value))
        self._model = value

    @property
    def n_chars(self):
        """int: Number of unique characters to support"""
        if not hasattr(self, "_n_chars"):
            self._n_chars = 10
        return self._n_chars

    @n_chars.setter
    def n_chars(self, value):
        if value is not None:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except Exception as e:
                    raise ValueError(self._generate_setter_exception(value))
            if value < 1:
                raise ValueError(self._generate_setter_exception(value))
        self._n_chars = value

    @property
    def spec_cols(self):
        """list(str): Character image specification columns"""
        return ["char", "source", "sub index", "char index"]

    @property
    def spec_dtypes(self):
        """list(str): Character image specification dtypes"""
        return {"char": str, "source": str, "sub index": int,
                "char index": int}

    @property
    def sub_ds(self):
        """scinoephile.ocr.ImageSubtitleDataset: Source subtitles"""
        if not hasattr(self, "_sub_ds"):
            self._sub_ds = None
        return self._sub_ds

    @sub_ds.setter
    def sub_ds(self, value):
        from scinoephile.ocr import ImageSubtitleDataset

        if value is not None:
            if not isinstance(value, ImageSubtitleDataset):
                raise ValueError(self._generate_setter_exception(value))
        self._sub_ds = value

    # endregion

    # region Public Methods

    def label_new_chars(self):
        embed(**self.embed_kw)

    # endregion

    # region Private Methods

    def _load_hdf5(self, fp, **kwargs):
        import pandas as pd
        import numpy as np

        decode = lambda x: x.decode("utf8")

        # Load image mode
        if "mode" not in fp.attrs:
            return
        self.mode = fp.attrs["mode"]

        # Load image specs
        if "spec" not in fp:
            raise ValueError()  # Weird to have mode but no specs or data
        spec = np.array(fp["spec"])
        spec = pd.DataFrame(data=spec, index=range(spec.size), columns=spec.dtype.names)
        spec["char"] = spec["char"].apply(decode)
        spec["source"] = spec["source"].apply(decode)

        # Load image data
        if "data" not in fp:
            raise ValueError()  # Weirder to have mode and specs but no data
        data = np.array(fp["data"])

        self.add_img(spec, data)

    def _save_hdf5(self, fp, **kwargs):
        import numpy as np

        dtypes = [("char", "S3"),
                  ("source", "S255"),
                  ("sub index", "i1"),
                  ("char index", "i1")]
        encode = lambda x: x.encode("utf8")

        # Save image mode
        fp.attrs["mode"] = self.mode

        # Save image specs
        if "spec" in fp:
            del fp["spec"]
        encoded = self.spec.copy()
        encoded["char"] = encoded["char"].apply(encode)
        encoded["source"] = encoded["source"].apply(encode)
        encoded = np.array(list(map(tuple, list(encoded.values))), dtype=dtypes)
        fp.create_dataset("spec",
                          data=encoded, dtype=dtypes,
                          chunks=True, compression="gzip")

        # Save iamge data
        if "data" in fp:
            del fp["data"]
        fp.create_dataset("data",
                          data=self.data, dtype=self.data_dtype,
                          chunks=True, compression="gzip")

    # endregion
