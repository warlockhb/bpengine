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
    bl_label = "AI 컬러 이름 적용"

    def execute(self, context):
        from . import BPColor, BPMaterial

        # TODO 전체 머티리얼 혹은 선택한 머티리얼할 수 있게 UI 연동
        # 현재는 전체 머티리얼을 적용 중이다.
        color_materials = BPMaterial.get_color_materials(bpy.data.materials)

        # 머티리얼 가져오기 & 분류
        color, alpha, roughness, metallic, use_texture, texture = BPMaterial.get_materials_properties(color_materials)

        # 클러스터링
        cluster_centers, cluster_group = BPColor.cluster_vector(color, clusters=60)

        # 머티리얼 클러스터 센터 색상 적용
        BPMaterial.set_materials_cluster_color(color_materials, cluster_centers, cluster_group)

        # 색상 머티리얼 중 중복 제거 및 재배치
        replace_materials = BPMaterial.replace_remove_duplicate_color_materials(color_materials)

        # 이름 적용
        BPColor.rename_color_materials(replace_materials)
