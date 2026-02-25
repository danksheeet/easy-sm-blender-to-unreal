bl_info = {
    "name": "Easy SM",
    "author": "Artem Bobkov",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Easy SM",
    "description": "Prepares and exports selected meshes to FBX for Unreal Engine",
    "category": "Import-Export",
}

import bpy
from . import ui
from . import properties
from . import export_operator
from . import collision_operator
from . import lod_operator

import importlib
if "ui" in locals():
    importlib.reload(ui)
if "properties" in locals():
    importlib.reload(properties)
if "export_operator" in locals():
    importlib.reload(export_operator)
if "collision_operator" in locals():
    importlib.reload(collision_operator)
if "lod_operator" in locals():
    importlib.reload(lod_operator)

modules = (
    properties,
    ui,
    export_operator,
    collision_operator,
    lod_operator,
)

def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()

if __name__ == "__main__":
    register()
