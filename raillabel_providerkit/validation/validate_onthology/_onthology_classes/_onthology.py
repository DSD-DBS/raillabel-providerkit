# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t
from dataclasses import dataclass

import raillabel

from ._object_classes import _ObjectClass


@dataclass
class _Onthology:
    classes: dict[str, _ObjectClass]
    errors: t.ClassVar = []

    @classmethod
    def fromdict(cls, data_dict: dict) -> _Onthology:
        return _Onthology(
            {class_id: _ObjectClass.fromdict(class_) for class_id, class_ in data_dict.items()}
        )

    def check(self, scene: raillabel.Scene) -> list[str]:
        self.errors = []

        self._check_class_validity(scene)
        annotations = self._compile_annotations(scene)
        for annotation in annotations:
            self.errors.extend(self.classes[annotation.object.type].check(annotation))

        return self.errors

    def _check_class_validity(self, scene: raillabel.Scene) -> list[str]:
        object_classes_in_scene = [obj.type for obj in scene.objects.values()]

        for object_class in object_classes_in_scene:
            if object_class not in self.classes:
                self.errors.append(f"Object type '{object_class}' is not defined.")

    def _compile_annotations(
        self, scene: raillabel.Scene
    ) -> list[type[raillabel.format._ObjectAnnotation]]:
        annotations = []
        for frame in scene.frames.values():
            annotations.extend(list(frame.annotations.values()))

        return annotations
