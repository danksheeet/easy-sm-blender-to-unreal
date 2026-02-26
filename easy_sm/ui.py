import bpy

class UE_EXPORT_PT_Panel(bpy.types.Panel):
    bl_label = "Easy SM Export"
    bl_idname = "UE_EXPORT_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Easy SM'
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.label(text="Export Settings:", icon='FILE_FOLDER')
        row = box.row()
        row.prop(scene, "ue_export_path", text="")
        
        layout.separator()
        
        box = layout.box()
        box.label(text="Actions:", icon='MODIFIER')
        
        col = box.column(align=True)
        col.prop(scene, "ue_add_sm_prefix", text="Add SM_ Prefix")
        col.prop(scene, "ue_apply_transforms", text="Apply Transforms")
        col.prop(scene, "ue_center_to_origin", text="Center to Origin")
        col.prop(scene, "ue_export_textures", text="Export Textures")
        col.prop(scene, "ue_export_collisions", text="Export Collisions")

        layout.separator()

        row = layout.row()
        row.scale_y = 1.5
        row.operator("export_scene.ue_batch", text="Export Selected to UE", icon='EXPORT')

class UE_COLLISION_PT_Panel(bpy.types.Panel):
    bl_label = "Easy SM Collision"
    bl_idname = "UE_COLLISION_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Easy SM'
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.label(text="Collision Generator:", icon='MESH_CUBE')
        
        col = box.column(align=True)
        col.prop(scene, "ue_col_prefix", text="Prefix")
        
        if scene.ue_col_prefix == 'UCX':
            col.prop(scene, "ue_col_decimate_ratio", text="Decimate Ratio")

        col.prop(scene, "ue_col_suffix", text="Add Incremental Suffix")
        col.prop(scene, "ue_col_separate_parts", text="Separate by Loose Parts")

        layout.separator()
        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("object.ue_generate_collisions", text="Generate Collisions", icon='MESH_CUBE')

class UE_LOD_PT_Panel(bpy.types.Panel):
    bl_label = "Easy SM LOD Generator"
    bl_idname = "UE_LOD_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Easy SM'
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        box.label(text="LOD Settings:", icon='MOD_DECIM')
        
        col = box.column(align=True)
        col.prop(scene, "ue_lod_count", text="Number of LODs")
        col.prop(scene, "ue_lod_step", text="Decimate Step")
        
        layout.separator()
        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("object.ue_generate_lods", text="Generate LODs", icon='MOD_DECIM')

classes = (
    UE_COLLISION_PT_Panel,
    UE_LOD_PT_Panel,
    UE_EXPORT_PT_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
