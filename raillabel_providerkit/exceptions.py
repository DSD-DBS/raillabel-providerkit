# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0


class UnsupportedFormatError(Exception):
    """Raised when a loaded annotation file is not in a supported format."""

    __module__ = "raillabel_providerkit"


class SchemaError(Exception):
    """Raised when the data does not validate against a given schema."""

    __module__ = "raillabel_providerkit"
