import bpy

class UE_EXPORT_PT_Panel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport sidebar"""
    bl_label = "Easy SM Export"
    bl_idname = "UE_EXPORT_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Easy SM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Export Settings:")
        row = layout.row()
        row.prop(scene, "ue_export_path")
        
        layout.separator()
        
        layout.label(text="Actions:")
        row = layout.row()
        row.prop(scene, "ue_apply_transforms", text="Apply Transforms")
        row = layout.row()
        row.prop(scene, "ue_center_to_origin", text="Center to Origin")
        row = layout.row()
        row.prop(scene, "ue_export_textures", text="Export Textures")
        row = layout.row()
        row.prop(scene, "ue_export_collisions", text="Export Collisions")

        layout.separator()

        layout.operator("export_scene.ue_batch", text="Export Selected to UE", icon='EXPORT')

class UE_COLLISION_PT_Panel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport sidebar"""
    bl_label = "Easy SM Collision"
    bl_idname = "UE_COLLISION_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Easy SM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Collision Generator:")
        
        row = layout.row()
        row.prop(scene, "ue_col_prefix", text="Prefix")
        
        if scene.ue_col_prefix == 'UCX':
            row = layout.row()
            row.prop(scene, "ue_col_decimate_ratio", text="Decimate Ratio")

        row = layout.row()
        row.prop(scene, "ue_col_suffix", text="Add Incremental Suffix")
        row = layout.row()
        row.prop(scene, "ue_col_separate_parts", text="Separate by Loose Parts")

        layout.separator()
        layout.operator("object.ue_generate_collisions", text="Generate Collisions", icon='MESH_CUBE')

class UE_LOD_PT_Panel(bpy.types.Panel):
    """Creates a LOD Panel in the 3D Viewport sidebar"""
    bl_label = "Easy SM LOD Generator"
    bl_idname = "UE_LOD_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Easy SM'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="LOD Settings:")
        
        row = layout.row()
        row.prop(scene, "ue_lod_count", text="Number of LODs")
        row = layout.row()
        row.prop(scene, "ue_lod_step", text="Decimate Step")
        
        layout.separator()
        layout.operator("object.ue_generate_lods", text="Generate LODs", icon='MOD_DECIM')

classes = (
    UE_EXPORT_PT_Panel,
    UE_COLLISION_PT_Panel,
    UE_LOD_PT_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
