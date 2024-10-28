# Copyright DB Netz AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from uuid import uuid4

import pytest
import raillabel

from raillabel_providerkit import exceptions
from raillabel_providerkit.validation import validate_onthology

# == Helpers ==========================


def make_dict_with_uids(objects: list) -> dict:
    return {obj.uid: obj for obj in objects}


def build_scene(
    sensors: t.List[raillabel.format.Sensor],
    objects: t.List[raillabel.format.Object],
    annotations: t.List[t.Type[raillabel.format._ObjectAnnotation]],
) -> raillabel.Scene:
    if type(sensors) == list:
        sensors = make_dict_with_uids(sensors)

    return raillabel.Scene(
        metadata=raillabel.format.Metadata(schema_version="1.0.0"),
        sensors=sensors,
        objects=make_dict_with_uids(objects),
        frames={0: raillabel.format.Frame(uid=0, annotations=make_dict_with_uids(annotations))},
    )


@pytest.fixture
def sensors() -> t.List[raillabel.format.Sensor]:
    return {
        "rgb_middle": raillabel.format.Sensor(
            uid="rgb_middle",
            type=raillabel.format.SensorType.CAMERA,
        ),
        "lidar": raillabel.format.Sensor(
            uid="lidar",
            type=raillabel.format.SensorType.LIDAR,
        ),
        "radar": raillabel.format.Sensor(
            uid="radar",
            type=raillabel.format.SensorType.RADAR,
        ),
    }


@pytest.fixture
def object_person() -> raillabel.format.Object:
    return raillabel.format.Object(
        uid="973ecc31-36f3-4b41-a1d8-9b584f265822",
        name="person_0000",
        type="person",
    )


def build_object(type: str) -> raillabel.format.Object:
    return raillabel.format.Object(
        uid=uuid4,
        name=type,
        type=type,
    )


def build_annotation(
    object: raillabel.format.Object,
    uid: str = "a3f3abe5-082d-42ce-966c-bae9c6dae9d9",
    sensor: raillabel.format.Sensor = raillabel.format.Sensor(
        uid="rgb_middle",
        type=raillabel.format.SensorType.CAMERA,
    ),
    attributes: dict = {},
) -> raillabel.format.Bbox:
    return raillabel.format.Bbox(
        uid=uid,
        object=object,
        sensor=sensor,
        attributes=attributes,
        pos=[],
        size=[],
    )


# == Fixtures =========================


@pytest.fixture
def metadata():
    return raillabel.format.Metadata(schema_version="1.0.0")


@pytest.fixture
def demo_onthology() -> dict:
    return {
        "person": {},
        "train": {},
    }


@pytest.fixture
def valid_onthology_scene(metadata) -> raillabel.Scene:
    return raillabel.format.Scene(
        metadata=metadata,
        objects=make_dict_with_uids(
            [
                build_object("person"),
                build_object("person"),
                build_object("train"),
            ]
        ),
    )


@pytest.fixture
def invalid_onthology_scene(metadata) -> raillabel.Scene:
    return raillabel.format.Scene(
        metadata=metadata,
        objects=make_dict_with_uids(
            [
                build_object("INVALID_CLASS"),
            ]
        ),
    )


# == Tests ============================


def test_onthology_schema_invalid():
    onthology = {"person": {"INVALID_FIELD": {}}}

    with pytest.raises(exceptions.OnthologySchemaError):
        validate_onthology(None, onthology)


def test_valid_classes(metadata):
    onthology = {
        "person": {},
        "train": {},
    }

    scene = raillabel.format.Scene(
        metadata=metadata,
        objects=make_dict_with_uids(
            [
                build_object("person"),
                build_object("person"),
                build_object("train"),
            ]
        ),
    )

    assert validate_onthology(scene, onthology) == []


def test_invalid_class(metadata):
    onthology = {
        "person": {},
        "train": {},
    }

    scene = raillabel.format.Scene(
        metadata=metadata,
        objects=make_dict_with_uids(
            [
                build_object("person"),
                build_object("UNDEFINED_CLASS"),
            ]
        ),
    )

    assert validate_onthology(scene, onthology) == ["Object type 'UNDEFINED_CLASS' is not defined."]


def test_undefined_attribute(sensors, object_person):
    onthology = {
        "person": {"attributes": {}},
    }

    annotation = build_annotation(
        object=object_person, sensor=sensors["lidar"], attributes={"UNKNOWN_ATTRIBUTE": 10}
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Undefined attribute 'UNKNOWN_ATTRIBUTE' in annotation {annotation.uid}."
    ]


def test_missing_attribute(sensors, object_person):
    onthology = {
        "person": {"attributes": {"number_of_fingers": "integer"}},
    }

    annotation = build_annotation(object=object_person, sensor=sensors["lidar"], attributes={})

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Missing attribute 'number_of_fingers' in annotation {annotation.uid}."
    ]


def test_valid_integer_attribute(sensors, object_person):
    onthology = {
        "person": {"attributes": {"number_of_fingers": "integer"}},
    }

    annotation = build_annotation(
        object=object_person, sensor=sensors["lidar"], attributes={"number_of_fingers": 10}
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == []


def test_false_integer_attribute_type(sensors, object_person):
    onthology = {
        "person": {"attributes": {"number_of_fingers": "integer"}},
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={"number_of_fingers": "THIS SHOULD BE AN INTEGER"},
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Attribute 'number_of_fingers' of annotation {annotation.uid} is of type 'str' (should be 'int')."
    ]


def test_valid_string_attribute(sensors, object_person):
    onthology = {
        "person": {"attributes": {"first_name": "string"}},
    }

    annotation = build_annotation(
        object=object_person, sensor=sensors["lidar"], attributes={"first_name": "Gudrun"}
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == []


def test_false_string_attribute_type(sensors, object_person):
    onthology = {
        "person": {"attributes": {"first_name": "string"}},
    }

    annotation = build_annotation(
        object=object_person, sensor=sensors["lidar"], attributes={"first_name": 42}
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Attribute 'first_name' of annotation {annotation.uid} is of type 'int' (should be 'str')."
    ]


def test_valid_boolean_attribute(sensors, object_person):
    onthology = {
        "person": {"attributes": {"has_cool_blue_shirt": "boolean"}},
    }

    annotation = build_annotation(
        object=object_person, sensor=sensors["lidar"], attributes={"has_cool_blue_shirt": False}
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == []


def test_false_boolean_attribute_type(sensors, object_person):
    onthology = {
        "person": {"attributes": {"has_cool_blue_shirt": "boolean"}},
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={"has_cool_blue_shirt": "NO THE SHIRT IS ORANGE ... AND THIS SHOULD BE A BOOL"},
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Attribute 'has_cool_blue_shirt' of annotation {annotation.uid} is of type 'str' (should be 'bool')."
    ]


def test_valid_vector_attribute(sensors, object_person):
    onthology = {
        "person": {"attributes": {"favorite_pizzas": "vector"}},
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={"favorite_pizzas": ["Diavolo", "Neapolitan", "Quattro Formaggi"]},
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == []


def test_false_vector_attribute_type(sensors, object_person):
    onthology = {
        "person": {"attributes": {"favorite_pizzas": "vector"}},
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={
            "favorite_pizzas": "does not like pizza (ikr)... THIS SHOULD BE A VECTOR AS WELL"
        },
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Attribute 'favorite_pizzas' of annotation {annotation.uid} is of type 'str' (should be 'list')."
    ]


def test_valid_single_select_attribute(sensors, object_person):
    onthology = {
        "person": {
            "attributes": {
                "carries": {
                    "type": "single-select",
                    "options": [
                        "groceries",
                        "a baby",
                        "the SlicerDicer 3000™ (wow!)",
                    ],
                }
            }
        },
    }

    annotation = build_annotation(
        object=object_person, sensor=sensors["lidar"], attributes={"carries": "groceries"}
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == []


def test_false_single_select_attribute_type(sensors, object_person):
    onthology = {
        "person": {
            "attributes": {
                "carries": {
                    "type": "single-select",
                    "options": [
                        "groceries",
                        "a baby",
                        "the SlicerDicer 3000™ (wow!)",
                    ],
                }
            }
        },
    }

    annotation = build_annotation(
        object=object_person, sensor=sensors["lidar"], attributes={"carries": False}
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Attribute 'carries' of annotation {annotation.uid} is of type 'bool' (should be 'str')."
    ]


def test_single_select_attribute_undefined_option(sensors, object_person):
    onthology = {
        "person": {
            "attributes": {
                "carries": {
                    "type": "single-select",
                    "options": [
                        "groceries",
                        "a baby",
                        "the SlicerDicer 3000™ (wow!)",
                    ],
                }
            }
        },
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={"carries": "something very unexpected"},
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Attribute 'carries' of annotation {annotation.uid} has an undefined value "
        + "'something very unexpected' (defined options: 'a baby', 'groceries', 'the SlicerDicer 3000™ (wow!)')."
    ]


def test_valid_multi_select_attribute(sensors, object_person):
    onthology = {
        "person": {
            "attributes": {
                "carries": {
                    "type": "multi-select",
                    "options": [
                        "groceries",
                        "a baby",
                        "the SlicerDicer 3000™ (wow!)",
                    ],
                }
            }
        },
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={"carries": ["groceries", "a baby"]},
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == []


def test_false_multi_select_attribute_type(sensors, object_person):
    onthology = {
        "person": {
            "attributes": {
                "carries": {
                    "type": "multi-select",
                    "options": [
                        "groceries",
                        "a baby",
                        "the SlicerDicer 3000™ (wow!)",
                    ],
                }
            }
        },
    }

    annotation = build_annotation(
        object=object_person, sensor=sensors["lidar"], attributes={"carries": "a baby"}
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Attribute 'carries' of annotation {annotation.uid} is of type 'str' (should be 'list')."
    ]


def test_multi_select_attribute_undefined_option(sensors, object_person):
    onthology = {
        "person": {
            "attributes": {
                "carries": {
                    "type": "multi-select",
                    "options": [
                        "groceries",
                        "a baby",
                        "the SlicerDicer 3000™ (wow!)",
                    ],
                }
            }
        },
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={"carries": ["a baby", "something very unexpected"]},
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Attribute 'carries' of annotation {annotation.uid} has an undefined value "
        + "'something very unexpected' (defined options: 'a baby', 'groceries', 'the SlicerDicer 3000™ (wow!)')."
    ]


def test_multiple_attributes_valid(sensors, object_person):
    onthology = {
        "person": {
            "attributes": {
                "number_of_fingers": "integer",
                "first_name": "string",
                "carries": {
                    "type": "single-select",
                    "options": [
                        "groceries",
                        "a baby",
                        "the SlicerDicer 3000™ (wow!)",
                    ],
                },
            }
        }
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={
            "carries": "groceries",
            "number_of_fingers": 9,
            "first_name": "Brunhilde",
        },
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == []


def test_multiple_attributes_invalid(sensors, object_person):
    onthology = {
        "person": {
            "attributes": {
                "number_of_fingers": "integer",
                "first_name": "string",
                "carries": {
                    "type": "single-select",
                    "options": [
                        "groceries",
                        "a baby",
                        "the SlicerDicer 3000™ (wow!)",
                    ],
                },
            }
        }
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={
            "carries": "something very unexpected",
            "number_of_fingers": 9,
            "first_name": True,
        },
    )

    scene = build_scene(sensors, [object_person], [annotation])
    c = validate_onthology(scene, onthology)
    assert validate_onthology(scene, onthology) == [
        f"Attribute 'carries' of annotation {annotation.uid} has an undefined value "
        + "'something very unexpected' (defined options: 'a baby', 'groceries', 'the SlicerDicer 3000™ (wow!)').",
        f"Attribute 'first_name' of annotation {annotation.uid} is of type 'bool' (should be 'str').",
    ]


def test_valid_sensor_type_attribute(sensors, object_person):
    onthology = {
        "person": {"sensor_types": {"lidar": {"attributes": {"number_of_fingers": "integer"}}}},
    }

    annotation = build_annotation(
        object=object_person, sensor=sensors["lidar"], attributes={"number_of_fingers": 10}
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == []


def test_invalid_sensor_type_attribute(sensors, object_person):
    onthology = {
        "person": {"sensor_types": {"lidar": {"attributes": {"number_of_fingers": "integer"}}}},
    }

    annotation = build_annotation(
        object=object_person, sensor=sensors["lidar"], attributes={"number_of_fingers": "None"}
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Attribute 'number_of_fingers' of annotation {annotation.uid} is of type 'str' (should be 'int')."
    ]


def test_valid_sensor_type_attributes_and_attributes(sensors, object_person):
    onthology = {
        "person": {
            "attributes": {"first_name": "string"},
            "sensor_types": {"lidar": {"attributes": {"number_of_fingers": "integer"}}},
        },
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={
            "number_of_fingers": 10,
            "first_name": "Brunhilde",
        },
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == []


def test_invalid_sensor_type_attributes_and_attributes(sensors, object_person):
    onthology = {
        "person": {
            "attributes": {"first_name": "string"},
            "sensor_types": {"lidar": {"attributes": {"number_of_fingers": "integer"}}},
        },
    }

    annotation = build_annotation(
        object=object_person,
        sensor=sensors["lidar"],
        attributes={
            "first_name": "Brunhilde",
        },
    )

    scene = build_scene(sensors, [object_person], [annotation])
    assert validate_onthology(scene, onthology) == [
        f"Missing attribute 'number_of_fingers' in annotation {annotation.uid}."
    ]


if __name__ == "__main__":
    pytest.main([__file__, "--disable-pytest-warnings", "--cache-clear", "-v"])
