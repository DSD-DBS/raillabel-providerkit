# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class IssueType(Enum):
    """General classification of the issue."""

    SCHEMA = "SchemaIssue"
    ATTRIBUTE_MISSING = "AttributeMissing"
    ATTRIBUTE_TYPE = "AttributeTypeIssue"
    ATTRIBUTE_UNDEFINED = "AttributeUndefined"
    ATTRIBUTE_VALUE = "AttributeValueIssue"
    DIMENSION_INVALID = "DimensionInvalidIssue"
    EMPTY_FRAMES = "EmptyFramesIssue"
    MISSING_EGO_TRACK = "MissingEgoTrackIssue"
    OBJECT_TYPE_UNDEFINED = "ObjectTypeUndefined"
    RAIL_SIDE = "RailSide"
    SENSOR_ID_UNKNOWN = "SensorIdUnknown"
    SENSOR_TYPE_WRONG = "SensorTypeWrong"
    UNEXPECTED_CLASS = "UnexpectedClassIssue"
    URI_FORMAT = "UriFormatIssue"


@dataclass
class IssueIdentifiers:
    """Information for locating an issue."""

    annotation: UUID | None = None
    attribute: str | None = None
    frame: int | None = None
    object: UUID | None = None
    object_type: str | None = None
    sensor: str | None = None


@dataclass
class Issue:
    """An error that was found inside the scene."""

    type: IssueType
    identifiers: IssueIdentifiers | list[str | int]
    reason: str | None = None
