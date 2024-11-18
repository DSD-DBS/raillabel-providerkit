# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import abc
from dataclasses import dataclass
from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules


@dataclass
class _Attribute(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def supports(cls, data_dict: dict) -> bool:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def fromdict(cls, data_dict: dict) -> type[_Attribute]:
        raise NotImplementedError

    @abc.abstractmethod
    def check(
        self, attribute_name: str, attribute_value: bool | float | str | list, annotation_id: str
    ) -> list[str]:
        raise NotImplementedError


def attribute_classes() -> list[type[_Attribute]]:
    """Return dictionary with Attribute child classes."""
    return ATTRIBUTE_CLASSES


def _collect_attribute_classes() -> None:
    """Collect attribute child classes and store them."""
    package_dir = str(Path(__file__).resolve().parent)
    for _, module_name, _ in iter_modules([package_dir]):
        module = import_module(
            f"raillabel_providerkit.validation.validate_onthology._onthology_classes._attributes.{module_name}"
        )
        for class_name in dir(module):
            class_ = getattr(module, class_name)

            if isclass(class_) and issubclass(class_, _Attribute) and class_ != _Attribute:
                ATTRIBUTE_CLASSES.append(class_)


ATTRIBUTE_CLASSES = []
_collect_attribute_classes()
