# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

from ._attribute_abc import _Attribute


@dataclass
class _MultiSelectAttribute(_Attribute):
    options: set[str]

    @classmethod
    def supports(cls, data_dict: dict) -> bool:
        return (
            type(data_dict) is dict and "type" in data_dict and data_dict["type"] == "multi-select"
        )

    @classmethod
    def fromdict(cls, data_dict: dict) -> _MultiSelectAttribute:
        return _MultiSelectAttribute(options=set(data_dict["options"]))

    def check(
        self, attribute_name: str, attribute_values: bool | float | str | list, annotation_id: str
    ) -> list[str]:
        if type(attribute_values) is not list:
            return [
                f"Attribute '{attribute_name}' of annotation {annotation_id} is of type "
                f"'{attribute_values.__class__.__name__}' (should be 'list')."
            ]

        for attribute_value in attribute_values:
            if attribute_value not in self.options:
                return [
                    f"Attribute '{attribute_name}' of annotation {annotation_id} has an undefined "
                    f"value '{attribute_value}' (defined options: {self._stringify_options()})."
                ]

        return []

    def _stringify_options(self) -> str:
        options_str = ""

        for option in sorted(self.options):
            options_str += f"'{option}', "

        if options_str != "":
            options_str = options_str[:-2]

        return options_str
