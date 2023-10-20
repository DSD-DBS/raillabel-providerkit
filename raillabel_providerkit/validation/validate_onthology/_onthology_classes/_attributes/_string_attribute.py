# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from dataclasses import dataclass

from ._attribute_abc import _Attribute


@dataclass
class _StringAttribute(_Attribute):
    @classmethod
    def supports(cls, data_dict: dict):
        return data_dict == "string"

    @classmethod
    def fromdict(cls, data_dict: dict):
        return _StringAttribute()

    def check(self, attribute_name: str, attribute_value, annotation_id: str) -> t.List[str]:
        errors = []

        if type(attribute_value) != str:
            errors.append(
                f"Attribute '{attribute_name}' of annotation {annotation_id} is of type "
                + f"'{attribute_value.__class__.__name__}' (should be 'str')."
            )

        return errors
