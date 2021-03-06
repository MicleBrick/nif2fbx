import sys
import glob
import bpy
import math

from pathlib import Path
from io_scene_niftools.modules.nif_import.property import texture
from mathutils import Euler, Matrix

def main():
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

        try_fix_lod()

        uv_map()

        # export fbx file
        bpy.ops.export_scene.fbx(filepath=str(Path(filepath).with_suffix(".fbx")),
                                    apply_scale_options="FBX_SCALE_ALL",
                                    axis_forward="-Z",
                                    axis_up="Y",
                                    use_space_transform=False,
                                    bake_space_transform=True)

def try_fix_lod():
    scene_node = bpy.data.objects['SceneNode']

    if len(scene_node.children) < 1:
        return

    first_child = scene_node.children[0]
    if first_child.name.startswith("loc_"):
        main_child = scene_node.children[1]
        main_child.location = first_child.location
        main_child.rotation_euler = first_child.rotation_euler
    else:
        main_child = first_child
        apply_transform(main_child, False)
        main_child.rotation_euler = Euler((0, 0, 0), 'XYZ')

    if len(main_child.children) < 3:
        return
    
    for i, child in enumerate(list(main_child.children[:3])):
        apply_transform(child, True)

        # https://blender.stackexchange.com/a/47769
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = child
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        child.select_set(state=True)

        for so in bpy.context.selected_objects:
            if so.type != 'MESH':
                so.select_set(state=False)

        if len(bpy.context.selected_objects) > 0:
            target = bpy.context.selected_objects[0]
            bpy.context.view_layer.objects.active = target
            bpy.ops.object.join()
            if target != child:
                target.parent = child.parent
                bpy.data.objects.remove(child, do_unlink=True)
            target.name = "imported_LOD" + str(i)


def apply_transform(obj, rot):
    active = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=rot, scale=False)
    bpy.context.view_layer.objects.active = active


def uv_map():
    bpy.ops.object.select_all(action='SELECT')
    
    selection_names = []

    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH':
            selection_names.append(obj)
            obj.select_set(False)

    if selection_names != []:
        for obj in selection_names:
                bpy.context.view_layer.objects.active = obj
                lm = obj.data.uv_layers.new(name="LightMap")
                lm.active = True
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
                bpy.ops.object.editmode_toggle()


main()
