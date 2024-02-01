bl_info = {
    "name": "BPEngine_v2",
    "blender": (4, 0, 2),
    "category": "Render",
    "version": (1, 0, 0),
    "author": "HBpencil",
    "description": "Shader Utility for Toon"
}
import bpy
from . import BPPanel as pt
from . import BPOperator as op


def register():
    # 오퍼레이션
    bpy.utils.register_class(op.RenameTextureMat)
    bpy.utils.register_class(op.RenameColorMat)

    # 패널
    bpy.utils.register_class(pt.PT_TEXTURE)


def unregister():
    # 오퍼레이션
    bpy.utils.unregister_class(op.RenameTextureMat)
    bpy.utils.unregister_class(op.RenameColorMat)

    # 패널
    bpy.utils.unregister_class(pt.PT_TEXTURE)


if __name__ == "__main__":
    register()
