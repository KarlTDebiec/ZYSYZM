#!/usr/bin/python
# -*- coding: utf-8 -*-
#   scinoephile.Compositor.py
#
#   Copyright (C) 2017-2019 Karl T Debiec
#   All rights reserved.
#
#   This software may be modified and distributed under the terms of the
#   BSD license. See the LICENSE file for details.
################################### MODULES ###################################
import re
import numpy as np
import pandas as pd
from os.path import expandvars, isfile
from IPython import embed
from scinoephile import (get_cantonese_pinyin, get_mandarin_pinyin,
                         merge_subtitles, package_root, CLToolBase,
                         SubtitleSeries)

################################## SETTINGS ###################################
pd.set_option("display.width", 110)
pd.set_option("display.max_colwidth", 16)
pd.set_option("display.max_rows", None)


################################### CLASSES ###################################
class Compositor(CLToolBase):
    """
    Compiles Chinese and English subtitles

    .. todo::
        - [ ] Refactor and improve code for handling dashes
        - [ ] Clean up merging code
        - [ ] Apply timings from one infile directly to another, provided they
              have the same number of subtitles
        - [ ] Address warnings
          - .../Compositor.py:762:         FutureWarning: from_items is
            deprecated. Please use DataFrame.from_dict(dict(items), ...)
            instead. DataFrame.from_dict(OrderedDict(items)) may be used to
            preserve the key order. [("start", [start]), ("end", [time])]),
            .../lib/python3.6/site-packages/pandas/core/frame.py:6211:
          - FutureWarning: Sorting because non-concatenation axis is not
            aligned. A future version of pandas will change to not sort by
            default. To accept the future behavior, pass 'sort=False'. To
            retain the current behavior and silence the warning, pass
            'sort=True'. sort=sort)
          - .../lib/python3.6/site-packages/pandas/core/generic.py:4405:
            SettingWithCopyWarning: A value is trying to be set on a copy of a
            slice from a DataFrame. See the caveats in the documentation:
            http://pandas.pydata.org/pandas-docs/stable/
            indexing.html#indexing-view-versus-copy self[name] = value
        - [ ] Document
    """
    import re

    # region Instance Variables
    help_message = ("Compiles Chinese and English subtitles into a single "
                    "file, optionally adding Mandarin or Cantonese "
                    "romanization, converting traditional characters to "
                    "simplified, or adding machine translation.")

    re_index = re.compile(r"^(?P<index>\d+)$")
    re_time = re.compile(r"^(?P<start>\d\d:\d\d:\d\d[,.]\d\d\d) --> "
                         r"(?P<end>\d\d:\d\d:\d\d[,.]\d\d\d)(\sX1:0)?$")
    re_blank = re.compile(r"^\s*$")

    # endregion

    # region Builtins
    def __init__(self, bilingual=False, english=False, hanzi=False,
                 pinyin=False, **kwargs):
        """
        Initializes tool

        Args:
            bilingual (str): Path to bilingual infile or outfile
            english (str): Path to English infile or outfile
            hanzi (str): Path to hanzi Chinese infile or outfile
            pinyin (str): Path to pinyin Chinese infile or outfile
            **kwargs: Additional keyword arguments
        """
        super().__init__(**kwargs)

        if bilingual:
            if isinstance(bilingual, str):
                bilingual = expandvars(bilingual)
                if isfile(bilingual):
                    self.bilingual_subtitles = SubtitleSeries.load(
                        bilingual, verbosity=self.verbosity)
        if english:
            if isinstance(english, str):
                english = expandvars(english)
                if isfile(english):
                    self.english_subtitles = SubtitleSeries.load(
                        english, verbosity=self.verbosity)
        if hanzi:
            if isinstance(hanzi, str):
                hanzi = expandvars(hanzi)
                if isfile(hanzi):
                    self.hanzi_subtitles = SubtitleSeries.load(
                        hanzi, verbosity=self.verbosity)
        if pinyin:
            if isinstance(pinyin, str):
                pinyin = expandvars(pinyin)
                if isfile(pinyin):
                    self.pinyin_subtitles = SubtitleSeries.load(
                        pinyin, verbosity=self.verbosity)

    def __call__(self):
        """
        Core logic
        """
        if (self.english_subtitles is not None
                and self.hanzi_subtitles is not None):

            for e in self.english_subtitles.events:
                e.text = re.sub(r"^\s*-?\s*(.*)\s*[\n\s]\s*-\s*(.+)\s*$",
                                r"- \1    - \2", e.text, re.M)
                e.text = re.sub(r"^\s*(.*)\s*\n\s*(.+)\s*$",
                                r"\1 \2", e.text, re.M)
            for e in self.hanzi_subtitles.events:
                e.text = re.sub(r"^\s*﹣?\s*(.*)\s+﹣(.+)\s*$",
                                r"﹣\1　　﹣\2", e.text, re.M)
                e.text = re.sub(r"^\s*(.*)\s*\n\s*(.+)\s*$",
                                r"\1　\2", e.text, re.M)
            self.pinyin_subtitles

            # merged_df = merge_subtitles(self.hanzi_subtitles,
            #                             self.english_subtitles)
            # merged_df["text"] = [f"{e['upper text']}\n{e['lower text']}"
            #                      for _, e in merged_df.iterrows()]
            # self.bilingual_subtitles = SubtitleSeries.from_dataframe(merged_df)
            # self.bilingual_subtitles.save("$HOME/ZE.srt")
            embed()

    # endregion

    # region Properties

    @property
    def bilingual_subtitles(self):
        """SubtitleSeries: Bilingual subtitles"""
        if not hasattr(self, "_bilingual_subtitles"):
            self._bilingual_subtitles = None
        return self._bilingual_subtitles

    @bilingual_subtitles.setter
    def bilingual_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._bilingual_subtitles = value

    @property
    def cantonese_corpus(self):
        """pycantonese.corpus.CantoneseCHATReader: Corpus for Cantonese
             romanization"""
        if not hasattr(self, "_cantonese_corpus"):
            import pycantonese as pc

            self._cantonese_corpus = pc.hkcancor()
            self._cantonese_corpus.add(
                f"{package_root}/data/romanization/unmatched.cha")
        return self._cantonese_corpus

    @property
    def english_subtitles(self):
        """SubtitleSeries: English subtitles"""
        if not hasattr(self, "_english_subtitles"):
            self._english_subtitles = None
        return self._english_subtitles

    @english_subtitles.setter
    def english_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._english_subtitles = value

    @property
    def hanzi_subtitles(self):
        """SubtitleSeries: Hanzi Chinse subtitles"""
        if not hasattr(self, "_hanzi_subtitles"):
            self._hanzi_subtitles = None
        return self._hanzi_subtitles

    @hanzi_subtitles.setter
    def hanzi_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._hanzi_subtitles = value

    @property
    def pinyin_subtitles(self):
        """SubtitleSeries: Romanized Chinese subtitles"""
        if not hasattr(self, "_pinyin_subtitles"):
            if isinstance(self.hanzi_subtitles, SubtitleSeries):
                self._initialize_pinyin_subtitles()
            else:
                self._pinyin_subtitles = None
        return self._pinyin_subtitles

    @pinyin_subtitles.setter
    def pinyin_subtitles(self, value):
        if not isinstance(value, SubtitleSeries):
            raise ValueError(self._generate_setter_exception(value))
        self._pinyin_subtitles = value

    # endregion

    # region Old Properties

    # @property
    # def simplified(self):
    #     """bool: Convert traditional Chinese to simplified"""
    #     if not hasattr(self, "_simplified"):
    #         self._simplified = False
    #     return self._simplified
    #
    # @simplified.setter
    # def simplified(self, value):
    #     if not isinstance(value, bool):
    #         raise ValueError()
    #     self._simplified = value
    # @property
    #
    # @property
    # def translate_client(self):
    #     """google.cloud.translate_v2.client.Client: Google Translate client"""
    #     if not hasattr(self, "_translate_client"):
    #         from google.cloud import translate
    #         self._translate_client = translate.Client()
    #     return self._translate_client
    #
    # @property
    # def truecase(self):
    #     """bool: Apply standard capitalization to English subtitles"""
    #     if not hasattr(self, "_truecase"):
    #         self._truecase = False
    #     return self._truecase
    #
    # @truecase.setter
    # def truecase(self, value):
    #     if not isinstance(value, bool):
    #         raise ValueError()
    #     self._truecase = value

    # endregion Properties

    # region Private Methods

    def _initialize_pinyin_subtitles(self, language="cantonese"):
        from copy import deepcopy

        if self.verbosity >= 1:
            if language == "mandarin":
                print("Adding Mandarin romanization")
            elif language == "cantonese":
                print("Adding Cantonese romanization")

        character_to_cantonese = {}
        unmatched = set()

        self._pinyin_subtitles = deepcopy(self.hanzi_subtitles)
        for event in self._pinyin_subtitles.events:
            if language == "mandarin":
                event.text = get_mandarin_pinyin(event.text)
            elif language == "cantonese":
                event.text = get_cantonese_pinyin(event.text,
                                                  self.cantonese_corpus,
                                                  character_to_cantonese,
                                                  unmatched,
                                                  self.verbosity)

    # endregion

    # region Old Methods

    # def add_english_translation(self, subtitles):
    #
    #     if self.verbosity >= 1:
    #         print("Adding English translation")
    #
    #     translations = []
    #     for i in range(0, len(subtitles), 100):
    #         translations += [c["translatedText"] for c in
    #                          self.translate_client.translate(
    #                              list(subtitles.iloc[i:i + 100].text),
    #                              source_language="zh",
    #                              target_language="en")]
    #     subtitles["translation"] = pd.Series(translations,
    #                                          index=subtitles.index)
    #
    #     if self.verbosity >= 2:
    #         for index, subtitle in subtitles.iterrows():
    #             start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
    #             end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
    #             print(f"{index}\n{start} --> {end}\n{subtitle.text}\n"
    #                   f"{subtitle.translation}\n")

    # def apply_truecase(self, subtitles):
    #     import nltk
    #     import re
    #
    #     if self.verbosity >= 1:
    #         print("Applying truecase to English subtitles")
    #
    #     for index, subtitle in subtitles.iterrows():
    #         text = subtitle["text"]
    #
    #         if self.verbosity >= 2:
    #             start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
    #             end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
    #             print(f"{index}\n{start} --> {end}\n{text}")
    #
    #             tagged = nltk.pos_tag(
    #                 [word.lower() for word in nltk.word_tokenize(text)])
    #             normalized = [w.capitalize() if t in ["NN", "NNS"] else w
    #                           for (w, t) in tagged]
    #             normalized[0] = normalized[0].capitalize()
    #             truecased = re.sub(r" (?=[\.,'!?:;])", "",
    #                                ' '.join(normalized))
    #
    #             # Could probably use a more appropriate tokenization function,
    #             # but cleaning up in this way is fine for now.
    #             truecased = truecased.replace(" n't", "n't")
    #             truecased = truecased.replace(" i ", " I ")
    #             truecased = truecased.replace("``", "\"")
    #             truecased = truecased.replace("''", "\"")
    #             truecased = re.sub(
    #                 r"(\A\w)|(?<!\.\w)([\.?!] )\w|\w(?:\.\w)|(?<=\w\.)\w",
    #                 lambda s: s.group().upper(), truecased)
    #
    #             if self.verbosity >= 2:
    #                 print(f"{truecased}\n")
    #
    #             subtitle["text"] = truecased

    # def simplify(self, subtitles):
    #     from hanziconv import HanziConv
    #
    #     if self.verbosity >= 1:
    #         print("Converting traditional characters to simplified")
    #
    #     for index, subtitle in subtitles.iterrows():
    #         text = subtitle["text"]
    #
    #         if self.verbosity >= 2:
    #             start = subtitle.start.strftime("%H:%M:%S,%f")[:-3]
    #             end = subtitle.end.strftime("%H:%M:%S,%f")[:-3]
    #             print(f"{index}\n{start} --> {end}\n{text}")
    #
    #         simplified = ""
    #         for character in text:
    #             if (self.re_hanzi.match(character)
    #                     or self.re_hanzi_rare.match(character)):
    #                 simplified += HanziConv.toSimplified(character)
    #             else:
    #                 simplified += character
    #
    #         if self.verbosity >= 2:
    #             print(f"{simplified}\n")
    #
    #         subtitle["text"] = simplified

    # endregion

    # region Class Methods
    @classmethod
    def construct_argparser(cls, parser=None):
        """
        Constructs argument parser

        Returns:
            parser (argparse.ArgumentParser): Argument parser
        """
        import argparse

        # Prepare parser
        if isinstance(parser, argparse.ArgumentParser):
            parser = parser
        elif isinstance(parser, argparse._SubParsersAction):
            parser = parser.add_parser(name="extraction",
                                       description=cls.help_message,
                                       help=cls.help_message)
        elif parser is None:
            parser = argparse.ArgumentParser(description=cls.help_message)
        super().construct_argparser(parser)

        # Input
        parser_file = parser.add_argument_group(
            "file arguments (at least one required)")
        parser_file.add_argument("-b", "--bilingual", type=str,
                                 nargs="?", default=False, const=True,
                                 metavar="FILE",
                                 help="Bilingual subtitles")
        parser_file.add_argument("-c", "--chinese", "--hanzi", type=str,
                                 nargs="?", default=False, const=True,
                                 metavar="FILE", dest="hanzi",
                                 help="Chinese Hanzi subtitles")
        parser_file.add_argument("-e", "--english", type=str,
                                 nargs="?", default=False, const=True,
                                 metavar="FILE",
                                 help="English subtitles")
        parser_file.add_argument("-p", "--pinyin", type=str,
                                 nargs="?", default=False, const=True,
                                 metavar="FILE",
                                 help="Chinese Pinyin subtitles")

        # Operation
        # parser_ops = parser.add_argument_group("operation arguments")
        # parser_ops.add_argument("--c_offset", type=float, default=0,
        #                         help="apply offset to Chinese subtitle "
        #                              "timings")
        # parser_ops.add_argument("-s", "--simplified", action="store_true",
        #                         help="convert traditional characters to "
        #                              "simplified")
        # parser_ops.add_argument("-m", "--mandarin", action="store_true",
        #                         help="add Mandarin Hanyu pinyin (汉语拼音)")
        # parser_ops.add_argument("-y", "--yue", action="store_true",
        #                         dest="cantonese",
        #                         help="add Cantonese Yale pinyin (耶鲁粤语拼音)")
        # parser_ops.add_argument("-t", "--translate", action="store_true",
        #                         dest="translate",
        #                         help="add English machine translation "
        #                              "generated using Google Translate; "
        #                              "requires key for Google Cloud Platform")
        # parser_ops.add_argument("--e_offset", type=float, default=0,
        #                         help="apply offset to English subtitle "
        #                              "timings")
        # parser_ops.add_argument("--truecase", action="store_true",
        #                         help="apply standard capitalization to "
        #                              "English subtitles")

        return parser

    @classmethod
    def validate_args(cls, parser, args):
        """
        Validates arguments

        Args:
            parser (argparse.ArgumentParser): Argument parser
            args (argparse.Namespace): Arguments

        Raises:
            ValueError: Incompatibility between provided arguments

        """
        from io import StringIO

        with StringIO() as helptext:
            parser.print_help(helptext)
            try:
                pass
            # if args.chinese_infile is None and args.english_infile is None:
            #     raise ValueError("Either argument '-c/--chinese_infile' "
            #                      "or '-e/--english_infile' is required")
            # if args.chinese_infile is None:
            #     if args.c_offset != 0:
            #         raise ValueError("Argument '--c_offset' requires "
            #                          "argument '-c/--chinese_infile'")
            #     if args.simplified:
            #         raise ValueError("Argument '-s' requires "
            #                          "argument '-c/--chinese_infile'")
            #     if args.mandarin:
            #         raise ValueError("Argument '-m' requires "
            #                          "argument '-c/--chinese_infile'")
            #     if args.cantonese:
            #         raise ValueError("Argument '-y' requires "
            #                          "argument '-c/--chinese_infile'")
            #     if args.translate:
            #         raise ValueError("Argument '-t' requires "
            #                          "argument '-c/--chinese_infile'")
            # if args.english_infile is None:
            #     if args.e_offset != 0:
            #         raise ValueError("Argument '--e_offset' requires "
            #                          "argument '-e/--english_infile'")
            #     if args.truecase:
            #         raise ValueError("Argument '--truecase' requires "
            #                          "argument '-e/--english_infile'")
            # if args.english_infile is not None:
            #     if args.translate:
            #         raise ValueError("Argument '-t' incompatible with "
            #                          "argument '-e/--english_infile'")
            except ValueError as e:
                print(helptext.getvalue())
                raise e

    # endregion


#################################### MAIN #####################################
if __name__ == "__main__":
    Compositor.main()
