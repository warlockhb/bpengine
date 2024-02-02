import bpy


# 머티리얼 섹션
class RenameTextureMat(bpy.types.Operator):
    bl_idname = "texture.rename_by_ai"
    bl_label = "AI 텍스쳐 이름 적용"

    def execute(self, context):
        from . import BPTextures
        # TODO 이미지 분석 모델 유기적으로 조정할 수 있게 변경
        BPTextures.rename_texture_materials()
        return {'FINISHED'}


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

        return {'FINISHED'}


# TODO 차후, 머티리얼 프리셋을 선택하여 변경할 수 있도록 수정
class ChangeMaterials(bpy.types.Operator):
    bl_idname = "material.change_materials"
    bl_label = "머티리얼 변경"

    def execute(self, context):
        from . import BPFile, BPColor, BPMaterial

        # 모든 머티리얼 프로퍼티 가져오기
        color, alpha, roughness, metallic, use_texture, texture = BPMaterial.get_materials_properties(bpy.data.materials)

        # 애셋 머티리얼 불러오기
        genshin_node = BPFile.append_nodegroup_from_asset("asset/BPA_Material.blend", "Genshin Shader")
        global_param_node = BPFile.append_nodegroup_from_asset("asset/BPA_Material.blend", "Global Color Parameter")

        # TODO 다양한 머티리얼 노드 그룹을 적용하도록, 좀 더 프로시저럴하게 함수화시켜야할 것 같다.
        for i, material in enumerate(bpy.data.materials):
            # 머티리얼 필터링
            if material.is_grease_pencil is True :
                continue
            if material.use_fake_user is True:
                continue

            # 머티리얼이 노드를 사용하도록 설정
            material.use_nodes = True
            nodes = material.node_tree.nodes

            # 모든 노드를 제거
            nodes.clear()

            # -------------------------------------------------------------
            # 노드 인스턴스 추가
            # 아웃풋 노드
            material_output_node = nodes.new(type='ShaderNodeOutputMaterial')

            # 원신 쉐이더
            genshin_ins = nodes.new('ShaderNodeGroup')
            genshin_ins.node_tree = genshin_node

            # 베이스컬러
            # 텍스쳐 사용 검사
            if use_texture[i]:
                # 텍스쳐 이미지 노드 생성
                texture_node = nodes.new(type='ShaderNodeTexImage')
                texture_node.image = texture[i][0]

            else:
                # 기존 베이스컬러 사용
                genshin_ins.inputs[0].default_value = color[i][0:3] + (alpha[i],)

            genshin_ins.inputs[2].default_value = alpha[i]
            genshin_ins.inputs[17].default_value = metallic[i]

            # 글로벌 파라미터
            global_param_ins = nodes.new('ShaderNodeGroup')
            global_param_ins.node_tree = global_param_node

            # -------------------------------------------------------------
            # 노드 연결 작업
            links = material.node_tree.links  # 노드 연결을 위한 링크 객체

            # 글로벌 파라미터 아웃풋[i] -> 원신 인풋[i] 연결
            # shadow color - 4
            links.new(global_param_ins.outputs[0], genshin_ins.inputs[4])
            # specular color - 25
            links.new(global_param_ins.outputs[1], genshin_ins.inputs[25])
            # metalic color - 21
            links.new(global_param_ins.outputs[2], genshin_ins.inputs[21])

            # use_texture가 참일 경우, 텍스쳐 아웃풋 -> 원신 인풋[0] 연결
            if use_texture[i]:
                links.new(texture_node.outputs[0], genshin_ins.inputs[0])

            # 원신의 아웃풋 -> 머티리얼 인풋[0] 연결
            links.new(genshin_ins.outputs[0], material_output_node.inputs['Surface'])

        return {'FINISHED'}