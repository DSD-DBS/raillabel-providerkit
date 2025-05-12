# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from enum import Enum
from typing import Literal
from uuid import UUID

import jsonschema


class IssueType(Enum):
    """General classification of the issue."""

    SCHEMA = "SchemaIssue"
    ATTRIBUTE_MISSING = "AttributeMissing"
    ATTRIBUTE_SCOPE = "AttributeScopeInconsistency"
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
    annotation_type: Literal["Bbox", "Cuboid", "Num", "Poly2d", "Poly3d", "Seg3d"] | None = None
    attribute: str | None = None
    frame: int | None = None
    object: UUID | None = None
    object_type: str | None = None
    sensor: str | None = None

    def serialize(self) -> dict[str, str | int]:
        """Serialize the IssueIdentifiers into a JSON-compatible dictionary.

        Returns
        -------
        dict[str, str | int]
            The serialized IssueIdentifiers as a JSON-compatible dictionary
        """
        return _clean_dict(
            {
                "annotation": str(self.annotation),
                "annotation_type": self.annotation_type,
                "attribute": self.attribute,
                "frame": self.frame,
                "object": str(self.object),
                "object_type": self.object_type,
                "sensor": self.sensor,
            }
        )

    @classmethod
    def deserialize(cls, serialized_issue_identifiers: dict[str, str | int]) -> "IssueIdentifiers":  # noqa: C901, PLR0912
        """Deserialize a JSON-compatible dictionary back into an IssueIdentifiers class instance.

        Parameters
        ----------
        serialized_issue_identifiers : dict[str, str  |  int]
            The serialized IssueIdentifiers as a JSON-compatible dictionary

        Returns
        -------
        IssueIdentifiers
            The deserialized IssueIdentifiers class instance

        Raises
        ------
        TypeError
            If any of the fields have an unexpected type
        """
        identifiers = IssueIdentifiers()

        annotation = serialized_issue_identifiers.get("annotation")
        if isinstance(annotation, int):
            raise TypeError
        if annotation is not None:
            identifiers.annotation = UUID(annotation)

        annotation_type = serialized_issue_identifiers.get("annotation_type")
        if annotation_type is not None:
            identifiers.annotation_type = annotation_type

        attribute = serialized_issue_identifiers.get("attribute")
        if isinstance(attribute, int):
            raise TypeError
        if attribute is not None:
            identifiers.attribute = attribute

        frame = serialized_issue_identifiers.get("frame")
        if isinstance(frame, str):
            raise TypeError
        if frame is not None:
            identifiers.frame = frame

        object = serialized_issue_identifiers.get("object")  # noqa: A001
        if isinstance(object, int):
            raise TypeError
        if object is not None:
            identifiers.object = UUID(object)

        object_type = serialized_issue_identifiers.get("object_type")
        if isinstance(object_type, int):
            raise TypeError
        if object_type is not None:
            identifiers.object_type = object_type

        sensor = serialized_issue_identifiers.get("sensor")
        if isinstance(sensor, int):
            raise TypeError
        if sensor is not None:
            identifiers.sensor = sensor

        return identifiers


@dataclass
class Issue:
    """An error that was found inside the scene."""

    type: IssueType
    identifiers: IssueIdentifiers | list[str | int]
    reason: str | None = None

    def serialize(self) -> dict[str, str | dict[str, str | int] | list[str | int]]:
        """Serialize the Issue into a JSON-compatible dictionary.

        Returns
        -------
        dict[str, str | dict[str, str | int] | list[str | int]]
            The serialized Issue as a JSON-compatible dictionary
        """
        serialized_issue = {
            "type": str(self.type.value),
            "identifiers": (
                self.identifiers.serialize()
                if isinstance(self.identifiers, IssueIdentifiers)
                else self.identifiers
            ),
        }
        if self.reason is not None:
            serialized_issue["reason"] = self.reason
        return serialized_issue

    @classmethod
    def deserialize(
        cls, serialized_issue: dict[str, str | dict[str, str | int] | list[str | int]]
    ) -> "Issue":
        """Deserialize a JSON-compatible dictionary back into an Issue class instance.

        Parameters
        ----------
        serialized_issue : dict[str, str  |  dict[str, str  |  int]  |  list[str  |  int]]
           The serialized Issue as a JSON-compatible dictionary

        Returns
        -------
        Issue
            The deserialized Issue class instance

        Raises
        ------
        jsonschema.exceptions.ValidationError
            If the serialized data does not match the Issue JSONSchema.
        """
        _verify_issue_schema(serialized_issue)
        return Issue(
            type=IssueType(serialized_issue["type"]),
            identifiers=IssueIdentifiers.deserialize(serialized_issue["identifiers"])
            if not isinstance(serialized_issue["identifiers"], list)
            else serialized_issue["identifiers"],
            reason=serialized_issue.get("reason"),
        )


def _clean_dict(d: dict) -> dict:
    """Remove all fields in a dict that are None or 'None'."""
    return {k: v for k, v in d.items() if str(v) != "None"}


ISSUES_SCHEMA = {
    "type": "array",
    "definitions": {
        "issue": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "identifiers": {
                    "anyOf": [
                        {
                            "type": "object",
                            "properties": {
                                "annotation": {"type": "string"},
                                "annotation_type": {
                                    "enum": ["Bbox", "Cuboid", "Num", "Poly2d", "Poly3d", "Seg3d"]
                                },
                                "attribute": {"type": "string"},
                                "frame": {"type": "integer"},
                                "object": {"type": "string"},
                                "object_type": {"type": "string"},
                                "sensor": {"type": "string"},
                            },
                        },
                        {"type": "array", "items": {"type": ["string", "integer"]}},
                    ]
                },
                "reason": {"type": "string"},
            },
            "required": ["type", "identifiers"],
        }
    },
    "items": {"$ref": "#/definitions/issue"},
}


def _verify_issue_schema(d: dict) -> None:
    jsonschema.validate(d, ISSUES_SCHEMA["definitions"]["issue"])
