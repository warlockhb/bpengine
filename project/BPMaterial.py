import bpy


def get_materials_properties(materials):
    # 데이터 리스트
    list_color_rgb = []
    list_color_alpha = []
    list_roughness = []
    list_metallic = []
    list_use_texture = []
    list_texture = []

    for material in materials:
        # 데이터 초기화
        color = material.diffuse_color
        color_rgb = (color[0], color[1], color[2])
        color_alpha = color[3]
        roughness = material.roughness
        metallic = material.metallic
        use_texture = False
        texture = []


        # 노드 트리 검사
        if material.use_nodes:
            for node in material.node_tree.nodes:
                # BSDF 검사
                if node.type == 'BSDF_PRINCIPLED':
                    if node.inputs[0].is_linked is True:
                        continue
                    else:
                        # basecolor 값 이전
                        color = node.inputs[0].default_value
                        color_rgb = (color[0], color[1], color[2])

                    if node.inputs[1].is_linked is True:
                        continue
                    else:
                        # metallic 값 이전
                        metallic = node.inputs[1].default_value

                    if node.inputs[2].is_linked is True:
                        continue
                    else:
                        # roughness 값 이전
                        roughness = node.inputs[2].default_value

                    if node.inputs[4].is_linked is True:
                        continue
                    else:
                        # alpha 값 이전
                        color_alpha = node.inputs[4].default_value

                # 텍스쳐 노드 검사
                if node.type == 'TEX_IMAGE':
                    use_texture = True
                    texture.append(node.image)

        list_color_rgb.append(color_rgb)
        list_color_alpha.append(color_alpha)
        list_roughness.append(roughness)
        list_metallic.append(metallic)
        list_use_texture.append(use_texture)
        list_texture.append(texture)

    return list_color_rgb, list_color_alpha, list_roughness, list_metallic, list_use_texture, list_texture


def get_color_materials(materials):
    color_materials = []

    for material in materials:
        # 노드 트리 검사
        if material.use_nodes:
            for node in material.node_tree.nodes:
                # BSDF 검사
                if node.type is 'BSDF_PRINCIPLED':
                    if not node.inputs[0].is_linked:
                        color_materials.append(material)
                        break

        else:
            color_materials.append(material)

    return color_materials


def set_materials_cluster_color(materials, center_colors, group_labels):
    for i, material in enumerate(materials):
        # 라벨에 따른 색상 센터 찾기
        label = group_labels[i]
        color = center_colors[label]

        material.diffuse_color = (color[0], color[1], color[2], material.diffuse_color[3])


def replace_remove_duplicate_color_materials(materials):
    # 머티리얼을 diffuse_color에 따라 그룹화
    color_groups = {}
    list_primary_mat = []
    list_dupliace_mat = []

    for mat in materials:
        if mat.use_nodes and mat.node_tree:
            base_color = next((node for node in mat.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
            if base_color:
                color = tuple(base_color.inputs[0].default_value)
                if color in color_groups:
                    color_groups[color].append(mat)
                else:
                    color_groups[color] = [mat]
        else:
            color = tuple(mat.diffuse_color)
            if color in color_groups:
                color_groups[color].append(mat)
            else:
                color_groups[color] = [mat]

    # 각 그룹에서 대표 머티리얼 선택 및 중복 머티리얼 교체
    for color, mats in color_groups.items():
        primary_mat = mats[0]  # 첫 번째 머티리얼을 대표로 선택
        for mat in mats[1:]:
            # 모든 오브젝트 순회하며 머티리얼 교체
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    for slot in obj.material_slots:
                        if slot.material is mat:
                            slot.material = primary_mat
            # 중복 머티리얼 삭제
            if mat is not None:
                list_dupliace_mat.append(mat)

        list_primary_mat.append(primary_mat)

    for mat in list_dupliace_mat:
        bpy.data.materials.remove(mat)

    return list_primary_mat




