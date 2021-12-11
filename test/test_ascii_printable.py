#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""Test that most characters in string.printable can are represented (some are
altered) in Docx2Python output. """

from docx2python.main import docx2python
import string


class TestAsciiPrintable:
    """ Confirming this works with v1.25 """

    def test_exact_representation(self) -> None:
        """Most characters are represented exactly
        The last seven characters are
        \n\r\x0b\b0cEND
        \n \r \x0b and \x0c are ignored by word when typed.
        END is there (added by hand to docx file) to let me know I'm past any
        trailing characters
        """
        pars = docx2python("resources/ascii_printable.docx")
        assert pars.text[:-7] == string.printable[:-4]
