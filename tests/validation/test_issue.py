# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from uuid import UUID

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType


def test_issue_identifiers_serialize__empty():
    identifiers = IssueIdentifiers()
    assert identifiers.serialize() == {}


def test_issue_identifiers_serialize__filled():
    identifiers = IssueIdentifiers(
        UUID("f9b8aa82-e42b-43df-85fb-99ab51145732"),
        "likes_trains",
        42,
        UUID("6caf0a36-3872-4368-8d88-801593c7bc24"),
        "person",
        "rgb_center",
    )
    assert identifiers.serialize() == {
        "annotation": "f9b8aa82-e42b-43df-85fb-99ab51145732",
        "attribute": "likes_trains",
        "frame": 42,
        "object": "6caf0a36-3872-4368-8d88-801593c7bc24",
        "object_type": "person",
        "sensor": "rgb_center",
    }


def test_issue_identifiers_deserialize__empty():
    identifiers = IssueIdentifiers.deserialize({})
    assert identifiers.annotation is None
    assert identifiers.attribute is None
    assert identifiers.frame is None
    assert identifiers.object is None
    assert identifiers.object_type is None
    assert identifiers.sensor is None


def test_issue_identifiers_deserialize__filled():
    identifiers = IssueIdentifiers.deserialize(
        {
            "annotation": "f9b8aa82-e42b-43df-85fb-99ab51145732",
            "attribute": "likes_trains",
            "frame": 42,
            "object": "6caf0a36-3872-4368-8d88-801593c7bc24",
            "object_type": "person",
            "sensor": "rgb_center",
        }
    )
    assert identifiers.annotation == UUID("f9b8aa82-e42b-43df-85fb-99ab51145732")
    assert identifiers.attribute == "likes_trains"
    assert identifiers.frame == 42
    assert identifiers.object == UUID("6caf0a36-3872-4368-8d88-801593c7bc24")
    assert identifiers.object_type == "person"
    assert identifiers.sensor == "rgb_center"


def test_issue_identifiers_deserialize__invalid_type_annotation():
    with pytest.raises(TypeError):
        IssueIdentifiers.deserialize(
            {
                "annotation": 42,
            }
        )


def test_issue_identifiers_deserialize__invalid_type_attribute():
    with pytest.raises(TypeError):
        IssueIdentifiers.deserialize(
            {
                "attribute": 42,
            }
        )


def test_issue_identifiers_deserialize__invalid_type_frame():
    with pytest.raises(TypeError):
        IssueIdentifiers.deserialize(
            {
                "frame": "the_first_frame",
            }
        )


def test_issue_identifiers_deserialize__invalid_type_object():
    with pytest.raises(TypeError):
        IssueIdentifiers.deserialize(
            {
                "object": 42,
            }
        )


def test_issue_identifiers_deserialize__invalid_type_object_type():
    with pytest.raises(TypeError):
        IssueIdentifiers.deserialize(
            {
                "object_type": 42,
            }
        )


def test_issue_identifiers_deserialize__invalid_type_sensor():
    with pytest.raises(TypeError):
        IssueIdentifiers.deserialize(
            {
                "sensor": 42,
            }
        )


def test_issue_serialize__simple():
    issue = Issue(
        IssueType.ATTRIBUTE_MISSING,
        IssueIdentifiers(
            UUID("f9b8aa82-e42b-43df-85fb-99ab51145732"),
            "likes_trains",
            42,
            UUID("6caf0a36-3872-4368-8d88-801593c7bc24"),
            "person",
            "rgb_center",
        ),
        "some reason",
    )
    assert issue.serialize() == {
        "type": "AttributeMissing",
        "identifiers": {
            "annotation": "f9b8aa82-e42b-43df-85fb-99ab51145732",
            "attribute": "likes_trains",
            "frame": 42,
            "object": "6caf0a36-3872-4368-8d88-801593c7bc24",
            "object_type": "person",
            "sensor": "rgb_center",
        },
        "reason": "some reason",
    }


def test_issue_serialize__do_not_add_reason_if_none():
    issue = Issue(
        IssueType.ATTRIBUTE_MISSING,
        IssueIdentifiers(
            UUID("f9b8aa82-e42b-43df-85fb-99ab51145732"),
            "likes_trains",
            42,
            UUID("6caf0a36-3872-4368-8d88-801593c7bc24"),
            "person",
            "rgb_center",
        ),
    )
    assert issue.serialize() == {
        "type": "AttributeMissing",
        "identifiers": {
            "annotation": "f9b8aa82-e42b-43df-85fb-99ab51145732",
            "attribute": "likes_trains",
            "frame": 42,
            "object": "6caf0a36-3872-4368-8d88-801593c7bc24",
            "object_type": "person",
            "sensor": "rgb_center",
        },
    }


def test_issue_serialize__schema_error():
    issue = Issue(
        IssueType.SCHEMA,
        ["this", "is", "some", "schema", "error", 73],
        "some reason",
    )
    assert issue.serialize() == {
        "type": "SchemaIssue",
        "identifiers": ["this", "is", "some", "schema", "error", 73],
        "reason": "some reason",
    }


def test_issue_deserialize__simple():
    issue = Issue.deserialize(
        {
            "type": "AttributeMissing",
            "identifiers": {
                "annotation": "f9b8aa82-e42b-43df-85fb-99ab51145732",
                "attribute": "likes_trains",
                "frame": 42,
                "object": "6caf0a36-3872-4368-8d88-801593c7bc24",
                "object_type": "person",
                "sensor": "rgb_center",
            },
            "reason": "some reason",
        }
    )
    assert issue.type == IssueType.ATTRIBUTE_MISSING
    assert isinstance(issue.identifiers, IssueIdentifiers)
    assert issue.identifiers.annotation == UUID("f9b8aa82-e42b-43df-85fb-99ab51145732")
    assert issue.identifiers.attribute == "likes_trains"
    assert issue.identifiers.frame == 42
    assert issue.identifiers.object == UUID("6caf0a36-3872-4368-8d88-801593c7bc24")
    assert issue.identifiers.object_type == "person"
    assert issue.identifiers.sensor == "rgb_center"
    assert issue.reason == "some reason"


def test_issue_deserialize__without_reason():
    issue = Issue.deserialize(
        {
            "type": "AttributeMissing",
            "identifiers": {
                "annotation": "f9b8aa82-e42b-43df-85fb-99ab51145732",
                "attribute": "likes_trains",
                "frame": 42,
                "object": "6caf0a36-3872-4368-8d88-801593c7bc24",
                "object_type": "person",
                "sensor": "rgb_center",
            },
        }
    )
    assert issue.type == IssueType.ATTRIBUTE_MISSING
    assert isinstance(issue.identifiers, IssueIdentifiers)
    assert issue.identifiers.annotation == UUID("f9b8aa82-e42b-43df-85fb-99ab51145732")
    assert issue.identifiers.attribute == "likes_trains"
    assert issue.identifiers.frame == 42
    assert issue.identifiers.object == UUID("6caf0a36-3872-4368-8d88-801593c7bc24")
    assert issue.identifiers.object_type == "person"
    assert issue.identifiers.sensor == "rgb_center"
    assert issue.reason is None


def test_issue_deserialize__schema_error():
    issue = Issue.deserialize(
        {
            "type": "SchemaIssue",
            "identifiers": ["this", "is", "some", "schema", "error", 73],
            "reason": "some reason",
        }
    )
    assert issue.type == IssueType.SCHEMA
    assert isinstance(issue.identifiers, list)
    assert issue.identifiers == ["this", "is", "some", "schema", "error", 73]
    assert issue.reason == "some reason"


def test_issue_deserialize__invalid_reason_type():
    with pytest.raises(TypeError):
        Issue.deserialize(
            {
                "type": "SchemaIssue",
                "identifiers": ["ignore"],
                "reason": ["wait", "that's", "illegal"],
            }
        )


def test_issue_deserialize__invalid_identifiers_type():
    with pytest.raises(TypeError):
        Issue.deserialize(
            {
                "type": "SchemaIssue",
                "identifiers": "A simple string is forbidden",
                "reason": "ignore",
            }
        )
