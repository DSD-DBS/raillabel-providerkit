..
   Copyright DB InfraGO AG and contributors
   SPDX-License-Identifier: Apache-2.0

===================
1 Validating Scenes
===================

Motivation
##########
The validation of the project requirements should ideally be done as close to the source of the data as possible. This devkit therefore provides functionality to check for basic errors on the supplier side. If you are unsure whether your applications produce valid annotations, simply use the functions provided here to check. **Only send us data, if the methods below say that no errors are present.** If you find any bugs in the code, just hit us up and we will fix them as soon as possible or create a PR.

Usage
#####

.. code-block:: python

    import json
    from pathlib import Path

    from raillabel_providerkit import validate

    scene_path = Path("path/to/scene.json")
    issues_in_scene = validate(scene_path)
    assert issues_in_scene == []

If this code does not raise any errors, you are good to go. If it does, read the content of the list `validate` returns carefully. It should tell you where the errors are. If you are unsure, contact your project partner or raise an issue on GitHub.
