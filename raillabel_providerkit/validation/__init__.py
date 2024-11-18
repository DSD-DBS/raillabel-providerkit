# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Package for validating raillabel data regarding the format requirements."""

from .validate_onthology.validate_onthology import validate_onthology

__all__ = ["validate_onthology"]
