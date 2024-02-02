import bpy


class PT_TEXTURE(bpy.types.Panel):
    bl_label = "텍스쳐"
    bl_idname = "TEXTURE_PT_rename"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BP엔진 v2'

    def draw(self, context):
        layout = self.layout

        layout.operator("texture.rename_by_ai")

        layout.operator("color.rename_by_ai")

        layout.operator("material.change_materials")