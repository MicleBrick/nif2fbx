import sys
import glob
import bpy
import math

from pathlib import Path
from io_scene_niftools.modules.nif_import.property import texture

# hacky fix for error
texture.IMPORT_EMBEDDED_TEXTURES = False

argv = sys.argv
argv = argv[argv.index("--") + 1:]

for filepath in glob.glob(argv[0]):
    print("Processing " + filepath)

    # delete default scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

    # import nif file
    bpy.ops.import_scene.nif(filepath=filepath, scale_correction=0.5)

    # change LOD_ to LOD
    bpy.ops.object.select_all(action='SELECT')
    for obj in bpy.context.selected_objects:
        if len(obj.name) > 3 and obj.name[:-1].lower().endswith("lod_"):
            obj.name = "LOD" + obj.name[-1]

    # export fbx file
    bpy.ops.export_scene.fbx(filepath=str(Path(filepath).with_suffix(".fbx")),
                                apply_scale_options="FBX_SCALE_ALL",
                                axis_forward="-Z",
                                axis_up="Y",
                                use_space_transform=False,
                                bake_space_transform=True)
