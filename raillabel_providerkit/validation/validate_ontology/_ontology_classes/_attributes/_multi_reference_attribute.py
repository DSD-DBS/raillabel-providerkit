# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t
from dataclasses import dataclass
from uuid import UUID

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType

from ._attribute_abc import _Attribute


@dataclass
class _MultiReferenceAttribute(_Attribute):
    TYPE_IDENTIFYER = "multi-reference"

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
