# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t
from dataclasses import dataclass
from uuid import UUID

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType
from raillabel_providerkit.validation.validate_onthology._onthology_classes._scope import (
    _Scope,
)

from ._attribute_abc import _Attribute


@dataclass
class _MultiReferenceAttribute(_Attribute):
    @classmethod
    def supports(cls, attribute_dict: dict) -> bool:
        return (
            "attribute_type" in attribute_dict
            and attribute_dict["attribute_type"] == "multi-reference"
        )

    @classmethod
    def fromdict(cls, attribute_dict: dict) -> _MultiReferenceAttribute:
        if not cls.supports(attribute_dict):
            raise ValueError

        return _MultiReferenceAttribute(
            optional=attribute_dict.get("optional", False),
            scope=_Scope(attribute_dict.get("scope", "annotation")),
            sensor_types=attribute_dict.get("sensor_types", ["camera", "lidar", "radar"]),
        )

    def check_type_and_value(
        self,
        attribute_name: str,
        attribute_values: bool | float | str | list,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        if type(attribute_values) is not list:
            return [
                Issue(
                    type=IssueType.ATTRIBUTE_TYPE,
                    reason=(
                        f"Attribute '{attribute_name}' is of type"
                        f" {attribute_values.__class__.__name__} (should be 'list')."
                    ),
                    identifiers=identifiers,
                )
            ]

        attribute_value: t.Any
        try:
            for attribute_value in attribute_values:
                UUID(attribute_value)
        except (ValueError, AttributeError):
            return [
                Issue(
                    type=IssueType.ATTRIBUTE_VALUE,
                    reason=(
                        f"Attribute '{attribute_name}' has a non-UUID value '{attribute_value}'."
                    ),
                    identifiers=identifiers,
                )
            ]

        return []
