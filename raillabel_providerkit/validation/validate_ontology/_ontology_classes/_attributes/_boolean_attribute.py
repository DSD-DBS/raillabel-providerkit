# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType

from ._attribute_abc import _Attribute


@dataclass
class _BooleanAttribute(_Attribute):
    TYPE_IDENTIFYER = "boolean"

    def check_type_and_value(
        self,
        attribute_name: str,
        attribute_value: bool | float | str | list,
        identifiers: IssueIdentifiers,
    ) -> list[Issue]:
        errors = []

        if type(attribute_value) is not bool:
            errors.append(
                Issue(
                    type=IssueType.ATTRIBUTE_TYPE,
                    reason=(
                        f"Attribute '{attribute_name}' is of type"
                        f" {attribute_value.__class__.__name__} (should be 'bool')."
                    ),
                    identifiers=identifiers,
                )
            )

        return errors
