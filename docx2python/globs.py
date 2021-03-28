#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
""" Global variables for docx context.

:author: Shay Hill
:created: 3/18/2021

The rels and flags for docx processing.
# TODO: improve docmod
"""
from dataclasses import dataclass, field
from typing import Dict, Set, Union, List, Optional
from operator import attrgetter
import os
from xml.etree import ElementTree
from contextlib import suppress

import zipfile
from .attribute_dicts import filter_files_by_type, ExpandedAttribDict, get_path

# TODO: match all imports re: ElementTree


@dataclass
class File:
    """
    The attribute dict of a file in the docx plus cached data

    The docx lists internal files in various _rels files. Each will be specified with a
    dict of, e.g.::

        {
            'Id': 'rId8',
            'Type': 'http://schemas.openxmlformats.org/.../relationships/header',
            'Target': 'header1.xml'
        }

    This isn't quite enough to infer the structure of the docx. You'll also need to
    know the directory where each attribute dict was found::

        'dir': 'word/_rels'

    # With this, you can make one additional inference: The other files each file will
    # reference within its xml::



    That's the starting point for these instances
    """

    def __init__(self, attribute_dict: Dict[str, str]) -> None:
        """
        Pull attributes from above-described dicts

        :param attribute_dict:
        """
        self.Id = attribute_dict["Id"]
        self.Type = os.path.basename(attribute_dict["Type"])
        self.Target = attribute_dict["Target"]
        self.dir = attribute_dict["dir"]

        self._path: Optional[str] = None
        # self._rels_path: Optional[str] = None
        self._unzipped: Optional[bytes] = None
        self._tree: Optional[ElementTree.Element] = None
        self._rels: List[Dict[str, str]] = []

    @property
    def path(self) -> str:
        # TODO: update docstring and ditch previous get_path_rels
        """
        Get path/to/rels for path/to/xml

        :param path: path to a docx content file.
        :returns: path to rels (which may not exist)

        Every content file (``document.xml``, ``header1.xml``, ...) will have its own
        ``.rels`` file--if any relationships are defined.
        """
        if not self._path:
            dirs = [os.path.dirname(x) for x in (self.dir, self.Target)]
            dirname = "/".join([x for x in dirs if x])
            filename = os.path.basename(self.Target)
            self._path = "/".join([dirname, filename])
        return self._path

    @property
    def _rels_path(self) -> str:
        # TODO: update docstring and ditch previous get_path_rels
        """
        Get path/to/rels for path/to/xml

        :param path: path to a docx content file.
        :returns: path to rels (which may not exist)

        Every content file (``document.xml``, ``header1.xml``, ...) will have its own
        ``.rels`` file--if any relationships are defined.

        The path inferred here may not exist.
        """
        dirs = [os.path.dirname(x) for x in (self.dir, self.Target)]
        dirname = "/".join([x for x in dirs if x])
        filename = os.path.basename(self.Target)
        return "/".join([dirname, "_rels", filename + ".rels"])

    @property
    def rels(self) -> Dict[str, Dict[str, str]]:
        if not self._rels:
            try:
                unzipped = DocxContext.zipf.read(self._rels_path)
                tree = ElementTree.fromstring(unzipped)
                rels = [x.attrib for x in tree]
            except KeyError:
                rels = []
            self._rels = {x["Id"]: x["Target"] for x in rels}
        return self._rels

    @property
    def unzipped(self) -> bytes:
        if not self._unzipped:
            self._unzipped = DocxContext.zipf.read(self.path)
        return self._unzipped

    @property
    def tree(self) -> bytes:
        if not self._tree:
            self._tree = ElementTree.fromstring(self.unzipped)
        return self._tree


@dataclass
class DocxContext:
    # each xml file has its own rels file.
    # rId numbers are NOT unique between rels files.
    # update this value before parsing text for each xml content file.
    file_specifiers: File
    zipf: zipfile.ZipFile

    current_file_rels: Dict[str, Dict[str, str]] = field(default_factory=dict)

    @classmethod
    def files_of_type(cls, type_: str) -> List[ExpandedAttribDict]:
        """
        File specifiers for all files with attrib Type='http://.../type_'

        :param type_: this package looks for any of
            ("header", "officeDocument", "footer", "footnotes", "endnotes")
        :return: file specifiers of the requested type, sorted by path
        """
        return sorted(
            (x for x in cls.file_specifiers if x.Type == type_), key=attrgetter("path")
        )

    @classmethod
    def find_by_path(cls, path: str):
        return (x for x in cls.file_specifiers if x.path == path)

    @classmethod
    def file_unzipped(cls, file_specifier: ExpandedAttribDict) -> bytes:
        if "unzipped" not in file_specifier:
            file_specifier["unzipped"] = cls.zipf.read(get_path(file_specifier))
        return file_specifier["unzipped"]
