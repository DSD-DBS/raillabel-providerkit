# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from dataclasses import dataclass

from ._attribute_abc import _Attribute


@dataclass
class _SingleSelectAttribute(_Attribute):

    options: t.Set[str]

    @classmethod
    def supports(cls, data_dict: dict):
        return (
            type(data_dict) == dict and "type" in data_dict and data_dict["type"] == "single-select"
        )

    @classmethod
    def fromdict(cls, data_dict: dict):
        return _SingleSelectAttribute(options=set(data_dict["options"]))

    def check(self, attribute_name: str, attribute_value, annotation_id: str) -> t.List[str]:

        if type(attribute_value) != str:
            return [
                f"Attribute '{attribute_name}' of annotation {annotation_id} is of type "
                + f"'{attribute_value.__class__.__name__}' (should be 'str')."
            ]

        if attribute_value not in self.options:
            return [
                f"Attribute '{attribute_name}' of annotation {annotation_id} has an undefined "
                + f"value '{attribute_value}' (defined options: {self._stringify_options()})."
            ]

        return []

    def _stringify_options(self) -> str:
        options_str = ""

        for option in sorted(list(self.options)):
            options_str += f"'{option}', "

        if options_str != "":
            options_str = options_str[:-2]

        return options_str
