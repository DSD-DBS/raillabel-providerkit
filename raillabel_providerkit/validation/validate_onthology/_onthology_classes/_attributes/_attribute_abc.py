# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import abc
from dataclasses import dataclass
from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules

from raillabel_providerkit.validation import Issue, IssueIdentifiers
from raillabel_providerkit.validation.validate_onthology._onthology_classes._scope import _Scope


@dataclass
class _Attribute(abc.ABC):
    """Attribute definition of an object class.

    Parameters
    ----------
    optional: bool
        Whether the attribute is required to exist in every annotation of the object class.
    scope: _Scope
        The scope all attributes following this definition have to adhere to.
    sensor_types: list[str]
        The sensors for which annotations are allowed to have this attribute.

    """

    optional: bool
    scope: _Scope
    sensor_types: list[str]

    @classmethod
    @abc.abstractmethod
    def supports(cls, attribute_dict: dict) -> bool:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def fromdict(cls, attribute_dict: dict) -> _Attribute:
        raise NotImplementedError

    @abc.abstractmethod
    def check_type_and_value(
        self,
        attribute_name: str,
        attribute_value: bool | float | str | list,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
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


ATTRIBUTE_CLASSES: list[type[_Attribute]] = []
_collect_attribute_classes()
