import bpy

class UE_LOD_OT_Generate(bpy.types.Operator):
    """Generates LODs (Level of Detail) for all selected meshes"""
    bl_idname = "object.ue_generate_lods"
    bl_label = "Generate LODs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        lod_count = scene.ue_lod_count
        lod_step = scene.ue_lod_step
        
        selected_objs = context.selected_objects
        if not selected_objs:
            self.report({'WARNING'}, "No objects selected!")
            return {'CANCELLED'}

        generated_count = 0

        # Save current active object
        original_active = context.view_layer.objects.active



        for obj in selected_objs:
            if obj.type == 'MESH':
                # Determine base name for LOD naming
                base_name = obj.name

                # Remove existing LOD children to prevent duplicates on repeated calls
                existing_lods = [child for child in obj.children
                                 if child.type == 'MESH' and "_LOD" in child.name]
                for old_lod in existing_lods:
                    bpy.data.meshes.remove(old_lod.data, do_unlink=True)
                    bpy.data.objects.remove(old_lod, do_unlink=True)

                current_ratio = 1.0

                for i in range(1, lod_count + 1):
                    current_ratio *= lod_step
                    lod_name = f"{base_name}_LOD{i}"
                    
                    # Create copy
                    lod_data = obj.data.copy()
                    lod_data.name = f"{lod_name}_Mesh"
                    lod_obj = obj.copy()
                    lod_obj.data = lod_data
                    lod_obj.name = lod_name
                    
                    # Link to active collection
                    context.collection.objects.link(lod_obj)
                    
                    # Parent to original mesh
                    lod_obj.parent = obj
                    lod_obj.matrix_parent_inverse = obj.matrix_world.inverted()
                    
                    # Add decimate modifier
                    bpy.ops.object.select_all(action='DESELECT')
                    lod_obj.select_set(True)
                    context.view_layer.objects.active = lod_obj
                    
                    mod = lod_obj.modifiers.new(name=f"Decimate_LOD{i}", type='DECIMATE')
                    mod.ratio = current_ratio
                    
                    # Optional: apply the modifier (Unreal might prefer raw mesh data rather than relying on modifiers in some export paths)
                    bpy.ops.object.modifier_apply(modifier=f"Decimate_LOD{i}")
                    
                    generated_count += 1

        # Restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objs:
            obj.select_set(True)
        
        if original_active:
            context.view_layer.objects.active = original_active

        self.report({'INFO'}, f"Generated {generated_count} LOD objects!")
        return {'FINISHED'}

classes = (
    UE_LOD_OT_Generate,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
