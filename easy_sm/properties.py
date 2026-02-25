import bpy

def register():
    bpy.types.Scene.ue_export_path = bpy.props.StringProperty(
        name="Path",
        description="Directory to export the FBX files",
        default="//UE_Export/",
        subtype='DIR_PATH'
    )
    


    bpy.types.Scene.ue_apply_transforms = bpy.props.BoolProperty(
        name="Apply Transforms",
        description="Automatically apply Location, Rotation, and Scale before export",
        default=True
    )
    
    bpy.types.Scene.ue_center_to_origin = bpy.props.BoolProperty(
        name="Center to Origin",
        description="Temporarily move the object to (0, 0, 0) for export to reset the pivot in Unreal Engine",
        default=True
    )
    
    bpy.types.Scene.ue_export_textures = bpy.props.BoolProperty(
        name="Export Textures",
        description="Extract and export material textures to a 'Textures' subfolder",
        default=True
    )
    
    bpy.types.Scene.ue_export_collisions = bpy.props.BoolProperty(
        name="Export Collisions",
        description="Automatically find and export associated collision meshes (UCX_, UBX_, USP_, UCP_) with the object",
        default=True
    )
    
    # Collision Generator Properties
    bpy.types.Scene.ue_col_prefix = bpy.props.EnumProperty(
        name="Collision Type",
        description="Prefix used for UE collision type",
        items=[
            ('UCX', "UCX (Convex Hull)", "Standard custom convex hull collision"),
            ('UBX', "UBX (Box)", "Box collision"),
            ('USP', "USP (Sphere)", "Sphere collision"),
            ('UCP', "UCP (Capsule)", "Capsule collision"),
        ],
        default='UCX'
    )
    
    bpy.types.Scene.ue_col_suffix = bpy.props.BoolProperty(
        name="Add Suffix",
        description="Add '_01' suffix (needed if you plan to have multiple collision shapes per mesh)",
        default=True
    )
    
    bpy.types.Scene.ue_col_separate_parts = bpy.props.BoolProperty(
        name="Separate Loose Parts",
        description="Automatically split disconnected parts of the mesh and generate separate collisions for each",
        default=False
    )
    
    bpy.types.Scene.ue_col_decimate_ratio = bpy.props.FloatProperty(
        name="Decimate Ratio",
        description="Ratio of triangles to keep (1.0 = no decimation, 0.1 = maximum decimation)",
        default=1.0,
        min=0.01,
        max=1.0,
        subtype='FACTOR'
    )
    
    # LOD Generator Properties
    bpy.types.Scene.ue_lod_count = bpy.props.IntProperty(
        name="LOD Count",
        description="Number of LODs to generate (e.g. 2 means creating LOD1 and LOD2)",
        default=2,
        min=1,
        max=5
    )
    
    bpy.types.Scene.ue_lod_step = bpy.props.FloatProperty(
        name="Decimate Step",
        description="Multiplier for polygon count per LOD level (0.5 means each LOD has half the polygons of the previous)",
        default=0.5,
        min=0.01,
        max=0.99,
        subtype='FACTOR'
    )

def unregister():
    del bpy.types.Scene.ue_export_path
    del bpy.types.Scene.ue_apply_transforms
    del bpy.types.Scene.ue_center_to_origin
    del bpy.types.Scene.ue_export_textures
    del bpy.types.Scene.ue_export_collisions
    del bpy.types.Scene.ue_col_prefix
    del bpy.types.Scene.ue_col_suffix
    del bpy.types.Scene.ue_col_separate_parts
    del bpy.types.Scene.ue_col_decimate_ratio
    del bpy.types.Scene.ue_lod_count
    del bpy.types.Scene.ue_lod_step
