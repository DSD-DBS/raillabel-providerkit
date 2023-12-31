# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import raillabel

from ..exceptions import UnsupportedFormatError
from . import loader_classes as loader_classes_pkg
from .loader_classes import LoaderABC


def convert(data: dict, loader_class: t.Optional[t.Type[LoaderABC]] = None) -> raillabel.Scene:
    """Convert annotation data from provider formats into raillabel.

    Parameters
    ----------
    data: dict
        Raw data in the provider format, that should be converted.
    loader_class: child-class of raillabel_providerkit.LoaderABC, optional
        Class used for converting the provider formatted data. If None is provided, then one is
        chosen based on criteria present in the data. Default is None.

    Returns
    -------
    scene: raillabel.Scene
        Scene with the loaded data in the raillabel format.

    Raises
    ------
    raillabel.UnsupportedFormatError
        if the annotation file does not match any loaders.
    """

    if loader_class is None:
        loader_class = _select_loader_class(data)

    return loader_class().load(data)


def _select_loader_class(data: dict) -> t.Type[LoaderABC]:
    loader_classes = []
    for cls in loader_classes_pkg.__dict__.values():
        if isinstance(cls, type) and issubclass(cls, LoaderABC) and cls != LoaderABC:
            loader_classes.append(cls)

    for loader_class in loader_classes:

        if loader_class().supports(data):
            return loader_class

    raise UnsupportedFormatError("No loader could be found, that supported the provided data.")
