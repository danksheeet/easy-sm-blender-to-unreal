import bpy
import os
import shutil
from .utils import is_descendant

class UE_EXPORT_OT_Batch(bpy.types.Operator):
    """Applies transforms, renames and exports selected objects to FBX"""
    bl_idname = "export_scene.ue_batch"
    bl_label = "Export to Unreal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        export_dir = scene.ue_export_path
        
        if not export_dir:
            self.report({'WARNING'}, "Please set an export path first!")
            return {'CANCELLED'}

        abs_export_dir = bpy.path.abspath(export_dir)
        if not os.path.exists(abs_export_dir):
            os.makedirs(abs_export_dir)

        selected_objs = context.selected_objects
        if not selected_objs:
            self.report({'WARNING'}, "No objects selected!")
            return {'CANCELLED'}

        exported_count = 0
        col_prefixes = ("UCX_", "UBX_", "USP_", "UCP_")

        # Save current active object to restore later
        original_active = context.view_layer.objects.active

        for obj in selected_objs:
            if obj.type == 'MESH':
                base_name = obj.name
                has_sm = base_name.startswith("SM_")
                
                if scene.ue_add_sm_prefix and not has_sm and not base_name.startswith("SK_"):
                    new_base_name = "SM_" + base_name
                    obj.name = new_base_name
                    
                    for scene_obj in context.scene.objects:
                        if scene_obj.type == 'MESH':
                            for prefix in col_prefixes:
                                if scene_obj.name.startswith(prefix) and base_name in scene_obj.name:
                                    scene_obj.name = scene_obj.name.replace(prefix + base_name, prefix + new_base_name, 1)
                                    break
                                    
                    for child in obj.children:
                        if child.type == 'MESH' and "_LOD" in child.name:
                            child.name = child.name.replace(base_name, new_base_name, 1)

                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                
                collision_objs = []
                if scene.ue_export_collisions:
                    base_name = obj.name
                    if base_name.startswith("SM_"):
                        base_name = base_name[3:]
                    elif base_name.startswith("SK_"):
                        base_name = base_name[3:]
                        
                    for scene_obj in context.scene.objects:
                        if scene_obj.type == 'MESH':
                            for prefix in col_prefixes:
                                if scene_obj.name.startswith(prefix) and base_name in scene_obj.name:
                                    collision_objs.append(scene_obj)
                                    break
                
                lod_objs = [child for child in obj.children if child.type == 'MESH' and "_LOD" in child.name]
                
                original_location = obj.location.copy()
                if scene.ue_center_to_origin:
                    offset = -original_location
                    obj.location = (0.0, 0.0, 0.0)
                    for col_obj in collision_objs:
                        if not is_descendant(col_obj, obj):
                            col_obj.location += offset
                
                if scene.ue_apply_transforms:
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    context.view_layer.objects.active = obj
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    
                    for col_obj in collision_objs:
                        bpy.ops.object.select_all(action='DESELECT')
                        col_obj.select_set(True)
                        context.view_layer.objects.active = col_obj
                        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    
                    for lod_obj in lod_objs:
                        if not lod_obj.parent:
                            bpy.ops.object.select_all(action='DESELECT')
                            lod_obj.select_set(True)
                            context.view_layer.objects.active = lod_obj
                            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                    
                orig_name = obj.name
                orig_parent = obj.parent
                has_lods = bool(lod_objs)
                lod_group_empty = None
                
                orig_col_parents = {}
                for col_obj in collision_objs:
                    orig_col_parents[col_obj] = col_obj.parent
                    if col_obj.parent:
                        mw_col = col_obj.matrix_world.copy()
                        col_obj.parent = None
                        col_obj.matrix_world = mw_col

                orig_lod_parents = {}
                mw_lods = {}
                orig_col_names = {}
                
                if has_lods:
                    obj.name = orig_name + "_LOD0"
                    
                    for col_obj in collision_objs:
                        orig_col_names[col_obj] = col_obj.name
                        for prefix in col_prefixes:
                            if col_obj.name.startswith(prefix):
                                col_after_prefix = col_obj.name[len(prefix):]
                                if col_after_prefix.startswith(orig_name):
                                    suffix = col_after_prefix[len(orig_name):]
                                    col_obj.name = f"{prefix}{orig_name}_LOD0{suffix}"
                                break

                    lod_group_empty = bpy.data.objects.new(orig_name, None)
                    context.collection.objects.link(lod_group_empty)
                    lod_group_empty["fbx_type"] = "LodGroup"
                    
                    if scene.ue_center_to_origin:
                        lod_group_empty.location = (0.0, 0.0, 0.0)
                    else:
                        lod_group_empty.location = obj.location
                        
                    mw = obj.matrix_world.copy()
                    obj.parent = lod_group_empty
                    obj.matrix_parent_inverse = lod_group_empty.matrix_world.inverted()

                    for lod_obj in lod_objs:
                        orig_lod_parents[lod_obj] = lod_obj.parent
                        mw_lods[lod_obj] = lod_obj.matrix_world.copy()
                        lod_obj.parent = lod_group_empty
                        lod_obj.matrix_parent_inverse = lod_group_empty.matrix_world.inverted()

                bpy.ops.object.select_all(action='DESELECT')
                if lod_group_empty:
                    lod_group_empty.select_set(True)
                obj.select_set(True)
                for col_obj in collision_objs:
                    col_obj.select_set(True)
                for lod_obj in lod_objs:
                    lod_obj.select_set(True)
                context.view_layer.objects.active = lod_group_empty if lod_group_empty else obj
                
                if scene.ue_export_textures:
                    tex_dir = os.path.join(abs_export_dir, "Textures")
                    if not os.path.exists(tex_dir):
                        os.makedirs(tex_dir)
                        
                    for mat_slot in obj.material_slots:
                        mat = mat_slot.material
                        if not mat or not mat.use_nodes:
                            continue
                        for node in mat.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and node.image:
                                img = node.image
                                if not img.has_data:
                                    continue
                                    
                                ext = ".png"
                                if img.filepath:
                                    _, orig_ext = os.path.splitext(img.filepath)
                                    if orig_ext:
                                        ext = orig_ext
                                        
                                img_name = bpy.path.clean_name(img.name)
                                if not img_name.lower().endswith(ext.lower()):
                                    img_name += ext
                                    
                                target_path = os.path.join(tex_dir, img_name)
                                
                                if not os.path.exists(target_path):
                                    src_path = bpy.path.abspath(img.filepath)
                                    if img.source == 'FILE' and os.path.exists(src_path):
                                        try:
                                            shutil.copy2(src_path, target_path)
                                        except Exception as e:
                                            print(f"Failed to copy texture: {e}")
                                    elif getattr(img, "has_data", False):
                                        try:
                                            old_path = img.filepath_raw
                                            img.filepath_raw = target_path
                                            img.save()
                                            img.filepath_raw = old_path
                                        except Exception as e:
                                            print(f"Failed to save packed texture {img.name}: {e}")

                safe_name = bpy.path.clean_name(orig_name)
                filepath = os.path.join(abs_export_dir, f"{safe_name}.fbx")
                
                bpy.ops.export_scene.fbx(
                    filepath=filepath,
                    use_selection=True,
                    bake_space_transform=False,
                    global_scale=1.0,
                    mesh_smooth_type='FACE',
                    add_leaf_bones=False,
                    axis_forward='-Z',
                    axis_up='Y',
                    path_mode='COPY',
                    embed_textures=True,
                    use_custom_props=True,
                    object_types={'EMPTY', 'MESH'}
                )
                exported_count += 1
                
                if has_lods:
                    obj.parent = orig_parent
                    if orig_parent:
                        obj.matrix_parent_inverse = orig_parent.matrix_world.inverted()
                    else:
                        obj.matrix_parent_inverse.identity()
                    obj.matrix_world = mw

                    for lod_obj in lod_objs:
                        lod_obj.parent = orig_lod_parents[lod_obj]
                        if orig_lod_parents[lod_obj]:
                            lod_obj.matrix_parent_inverse = orig_lod_parents[lod_obj].matrix_world.inverted()
                        else:
                            lod_obj.matrix_parent_inverse.identity()
                        lod_obj.matrix_world = mw_lods[lod_obj]

                    bpy.data.objects.remove(lod_group_empty)
                    obj.name = orig_name

                for col_obj in collision_objs:
                    if col_obj in orig_col_names:
                        col_obj.name = orig_col_names[col_obj]
                    
                    if orig_col_parents[col_obj]:
                        mw_col = col_obj.matrix_world.copy()
                        col_obj.parent = orig_col_parents[col_obj]
                        col_obj.matrix_parent_inverse = orig_col_parents[col_obj].matrix_world.inverted()
                        col_obj.matrix_world = mw_col

                if scene.ue_center_to_origin:
                    obj.location = original_location
                    for col_obj in collision_objs:
                        if not is_descendant(col_obj, obj):
                            col_obj.location += original_location

                for col_obj in collision_objs:
                    col_obj.select_set(False)
                for lod_obj in lod_objs:
                    lod_obj.select_set(False)


        for obj in selected_objs:
            obj.select_set(True)
        if original_active:
            context.view_layer.objects.active = original_active

        self.report({'INFO'}, f"Exported {exported_count} objects to Unreal!")
        return {'FINISHED'}

classes = (
    UE_EXPORT_OT_Batch,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
