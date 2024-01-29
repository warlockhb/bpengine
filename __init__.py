bl_info = {
    "name": "BPEngine_v2",
    "blender": (4, 0, 2),
    "category": "Render",
    "version": (1, 0, 0),
    "author": "HBpencil",
    "description": "Shader Utility for Toon"
}

import bpy

class SimpleOperator(bpy.types.Operator):
    """My Simple Operator"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"

    def execute(self, context):
        print("hello")
        return {'FINISHED'}


class SimplePanel(bpy.types.Panel):
    bl_label = "Simple Panel"
    bl_idname = "OBJECT_PT_simple"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BPEngine'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.simple_operator")


def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.utils.register_class(SimplePanel)


def unregister():
    bpy.utils.unregister_class(SimplePanel)
    bpy.utils.unregister_class(SimpleOperator)


if __name__ == "__main__":
    register()
