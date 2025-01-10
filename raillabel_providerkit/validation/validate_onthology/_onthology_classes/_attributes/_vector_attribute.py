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
class _VectorAttribute(_Attribute):
    @classmethod
    def supports(cls, data: dict) -> bool:
        return "attribute_type" in data and data["attribute_type"] == "vector"

    @classmethod
    def fromdict(cls, data: dict) -> _VectorAttribute:
        if not cls.supports(data):
            raise ValueError

        return _VectorAttribute(
            optional=data.get("optional", False),
            scope=_Scope(data["scope"]),
            sensor_types=data.get("sensor_types", ["camera", "lidar", "radar"]),
        )

    def check_type_and_value(
        self,
        attribute_name: str,
        attribute_value: list | float | str | bool,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        errors = []

        if type(attribute_value) is not list:
            errors.append(
                Issue(
                    type=IssueType.ATTRIBUTE_TYPE,
                    reason=(
                        f"Attribute '{attribute_name}' is of type"
                        f" {attribute_value.__class__.__name__} (should be 'list')."
                    ),
                    identifiers=identifiers,
                )
            )

        return errors
