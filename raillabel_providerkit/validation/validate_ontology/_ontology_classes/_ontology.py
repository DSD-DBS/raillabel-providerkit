# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

import raillabel

from raillabel_providerkit.validation import Issue, IssueIdentifiers, IssueType

from ._annotation_with_metadata import _AnnotationWithMetadata
from ._object_classes import _ObjectClass


@dataclass
class _Ontology:
    classes: dict[str, _ObjectClass]
    errors: list[Issue]

    @classmethod
    def fromdict(cls, data: dict) -> _Ontology:
        return _Ontology(
            {class_id: _ObjectClass.fromdict(class_) for class_id, class_ in data.items()}, []
        )

    def check(self, scene: raillabel.Scene) -> list[Issue]:
        self.errors = []

        self._check_class_validity(scene)
        annotations = _Ontology._compile_annotations(scene)
        for annotation_metadata in annotations:
            if annotation_metadata.object_type not in self.classes:
                continue

            self.errors.extend(
                self.classes[annotation_metadata.object_type].check(annotation_metadata)
            )

        return self.errors

    def _check_class_validity(self, scene: raillabel.Scene) -> None:
        for obj_uid, obj in scene.objects.items():
            object_class = obj.type
            if object_class not in self.classes:
                self.errors.append(
                    Issue(
                        type=IssueType.OBJECT_TYPE_UNDEFINED,
                        identifiers=IssueIdentifiers(object=obj_uid, object_type=object_class),
                    )
                )

    @classmethod
    def _compile_annotations(cls, scene: raillabel.Scene) -> list[_AnnotationWithMetadata]:
        return [
            _AnnotationWithMetadata(annotation_id, frame_id, scene)
            for frame_id, frame in scene.frames.items()
            for annotation_id in frame.annotations
        ]
