# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType
from raillabel_providerkit.validation.validate_onthology._onthology_classes._scope import (
    _Scope,
)

from ._attribute_abc import _Attribute


@dataclass
class _SingleSelectAttribute(_Attribute):
    options: set[str]

    @classmethod
    def supports(cls, attribute_dict: dict) -> bool:
        return (
            "attribute_type" in attribute_dict
            and type(attribute_dict["attribute_type"]) is dict
            and "type" in attribute_dict["attribute_type"]
            and attribute_dict["attribute_type"]["type"] == "single-select"
        )

    @classmethod
    def fromdict(cls, attribute_dict: dict) -> _SingleSelectAttribute:
        if not cls.supports(attribute_dict):
            raise ValueError

        return _SingleSelectAttribute(
            optional=attribute_dict.get("optional", False),
            scope=_Scope(attribute_dict.get("scope", "annotation")),
            sensor_types=attribute_dict.get("sensor_types", ["camera", "lidar", "radar"]),
            options=set(attribute_dict["attribute_type"]["options"]),
        )

    def check_type_and_value(
        self,
        attribute_name: str,
        attribute_value: bool | float | str | list,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        if type(attribute_value) is not str:
            return [
                Issue(
                    type=IssueType.ATTRIBUTE_TYPE,
                    reason=(
                        f"Attribute '{attribute_name}' is of type"
                        f" {attribute_value.__class__.__name__} (should be 'str')."
                    ),
                    identifiers=identifiers,
                )
            ]

        if attribute_value not in self.options:
            return [
                Issue(
                    type=IssueType.ATTRIBUTE_VALUE,
                    reason=(
                        f"Attribute '{attribute_name}' has an undefined value"
                        f" '{attribute_value}' (defined options: {self._stringify_options()})."
                    ),
                    identifiers=identifiers,
                )
            ]

        return []

    def _stringify_options(self) -> str:
        options_str = ""

        for option in sorted(self.options):
            options_str += f"'{option}', "

        if options_str != "":
            options_str = options_str[:-2]

        return options_str
