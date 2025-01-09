# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

from ._attribute_abc import _Attribute


@dataclass
class _SingleSelectAttribute(_Attribute):
    options: set[str]

    @classmethod
    def supports(cls, data: dict | str) -> bool:
        return type(data) is dict and "type" in data and data["type"] == "single-select"

    @classmethod
    def fromdict(cls, data: dict | str) -> _SingleSelectAttribute:
        if isinstance(data, str):
            raise TypeError

        return _SingleSelectAttribute(options=set(data["options"]))

    def check_type_and_value(
        self, attribute_name: str, attribute_value: bool | float | str | list, annotation_id: str
    ) -> list[str]:
        if type(attribute_value) is not str:
            return [
                f"Attribute '{attribute_name}' of annotation {annotation_id} is of type "
                f"'{attribute_value.__class__.__name__}' (should be 'str')."
            ]

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
