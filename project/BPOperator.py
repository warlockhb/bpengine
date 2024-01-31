import bpy

# 머티리얼 섹션
class RenameTextureMat(bpy.types.Operator):
    bl_idname = "texture.rename_by_ai"
    bl_label = "AI 텍스쳐 이름 적용"

    def execute(self, context):
        from . import BPTextures
        # TODO 이미지 분석 모델 유기적으로 조정할 수 있게 변경
        BPTextures.rename_texture_materials()


class RenameColorMat(bpy.types.Operator):
    bl_idname = "color.rename_by_ai"
    bl_label = "AI 텍스쳐 이름 적용"

    def execute(self, context):
        from . import BPColor
        # 머티리얼 가져오기 & 분류
        import_blender_materials()

        # 머티리얼 - 컬러 섹션
        color_centers, color_clusters = set_color_cluster(color_materials, color_cluster_amount)

        # 머티리얼 대표자 지정
        set_color_master(color_clusters, color_centers)
        # 대표 머티리얼 -> 블렌더 머티리얼 색 적용

        # 머티리얼 대체 및 삭제
        replace_color_materials(color_clusters)

        # # 머티리얼 - 텍스쳐 섹션
        replace_texture_materials(texture_materials)
        #