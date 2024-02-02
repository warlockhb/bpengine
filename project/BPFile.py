import bpy
import os


def append_material_from_asset(blend_file_path, material_name):
    current_path = os.path.dirname(__file__)
    blend_file_path = os.path.join(current_path, blend_file_path)

    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
        if material_name in data_from.materials:
            data_to.materials = [material_name]
        else:
            print(f"Material '{material_name}' not found in '{blend_file_path}'")
            return None
    return bpy.data.materials.get(material_name)


def append_nodegroup_from_asset(blend_file_path, node_group_name):
    current_path = os.path.dirname(__file__)
    blend_file_path = os.path.join(current_path, blend_file_path)

    # 블렌드 파일을 열고 노드 그룹을 가져옵니다.
    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
        # 지정된 노드 그룹이 블렌드 파일 내에 존재하는지 확인합니다.
        if node_group_name in data_from.node_groups:
            # 가져올 노드 그룹을 지정합니다.
            data_to.node_groups = [node_group_name]
        else:
            # 지정된 노드 그룹이 없을 경우 오류 메시지를 출력합니다.
            print(f"Node group '{node_group_name}' not found in '{blend_file_path}'")
            return None

    # 가져온 노드 그룹을 반환합니다.
    return bpy.data.node_groups.get(node_group_name)