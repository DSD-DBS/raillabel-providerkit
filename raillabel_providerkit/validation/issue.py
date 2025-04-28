# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from enum import Enum
from uuid import UUID


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
    HORIZON_CROSSED = "HorizonCrossedIssue"
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

    def serialize(self) -> dict[str, str | int]:
        """Serialize the IssueIdentifiers into a JSON-compatible dictionary.

        Returns
        -------
        dict[str, str | int]
            The serialized IssueIdentifiers as a JSON-compatible dictionary
        """
        serialized_issue_identifiers: dict[str, str | int] = {}
        if self.annotation is not None:
            serialized_issue_identifiers["annotation"] = str(self.annotation)
        if self.attribute is not None:
            serialized_issue_identifiers["attribute"] = self.attribute
        if self.frame is not None:
            serialized_issue_identifiers["frame"] = self.frame
        if self.object is not None:
            serialized_issue_identifiers["object"] = str(self.object)
        if self.object_type is not None:
            serialized_issue_identifiers["object_type"] = self.object_type
        if self.sensor is not None:
            serialized_issue_identifiers["sensor"] = self.sensor
        return serialized_issue_identifiers

    @classmethod
    def deserialize(cls, serialized_issue_identifiers: dict[str, str | int]) -> "IssueIdentifiers":  # noqa: C901
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
        TypeError
            If the reason is not None or a string or if the identifiers are a string
        """
        serialized_type = serialized_issue["type"]
        serialized_identifiers = serialized_issue["identifiers"]
        serialized_reason = serialized_issue.get("reason")
        if serialized_reason is not None and not isinstance(serialized_reason, str):
            raise TypeError
        if isinstance(serialized_identifiers, str):
            raise TypeError

        return Issue(
            IssueType(serialized_type),
            IssueIdentifiers.deserialize(serialized_identifiers)
            if not isinstance(serialized_identifiers, list)
            else serialized_identifiers,
            serialized_reason,
        )
