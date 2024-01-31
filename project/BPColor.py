import bpy
import webcolors
import numpy as np
from sklearn.cluster import KMeans

# 리스트
materials = []
color_materials = []
texture_materials = []


# 머티리얼 데이터
class MaterialManager:
    def __init__(self):
        # 기본 데이터
        self.data = None
        self.name = None
        self.replacement = True
        self.master = None

        # 컬러 데이터
        self.color_float = None
        self.color_int = None
        self.color_alpha = None

        # 텍스쳐 데이터
        self.use_texture = False
        self.texture = None

        # 그룹 데이터
        self.closet_color = None
        self.color_cluster = None
        self.alpha_cluster = None

    def create(self, material):
        if material.malt.material_type == 'Mesh':
            # 기본 데이터
            self.name = material.name
            self.data = material

            # 컬러 데이터
            self.color_float = material.diffuse_color[0:3]
            self.color_int = convert_color_float_to_int(self.color_float)
            self.color_alpha = material.diffuse_color[3]

            # 텍스쳐 데이터
            self.check_texture()

            # 그룹 데이터
            self.closet_color = None
            self.color_cluster = None
            self.alpha_cluster = None

    def check_texture(self):
        if self.data.use_nodes:
            image_node = 'Image Texture'
            if image_node in self.data.node_tree.nodes:
                self.use_texture = True
                self.texture = self.data.node_tree.nodes["Image Texture"].image


# 함수 영역
# 컬러 함수
def convert_color_float_to_int(color):
    return tuple(int(c * 255) for c in color)


def set_closest_color(color):
    color = convert_color_float_to_int(color)

    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - color[0]) ** 2
        gd = (g_c - color[1]) ** 2
        bd = (b_c - color[2]) ** 2
        min_colors[(rd + gd + bd)] = name

    return min_colors[min(min_colors.keys())]


# 클러스터 함수
def analyze_cluster(list, clusters=5):
    # K-means 클러스터링 수행
    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(list)

    # 클러스터 중심점(대표 색상) 가져오기
    cluster_centers = kmeans.cluster_centers_

    # 각 색상에 대한 클러스터 라벨 반환
    cluster_group = kmeans.labels_


    return cluster_centers, cluster_group


def set_color_cluster(materials: list, clusters: int) -> list:
    #검사
    if materials is not None:
        colors = []

        # 컬러 리스트화
        for material in materials:
            color = material.color_float
            if color is not None:
                colors.append(color)

            else:
                print("컬러 머티리얼 리스트에 잘못된 머티리얼가 포함되어 있음")
                return None

        # 분석기
        centers, groups = analyze_cluster(colors, clusters)

        # 클러스터 리스트
        clusters_list = [[] for _ in range(clusters)]

        # 그룹화
        if len(groups) == len(materials):
            mat_dict = dict(zip(materials, groups))
            for i, (material, group) in enumerate(mat_dict.items()):
                materials[i].color_cluster = group
                clusters_list[group].append(material)
                # print(materials[i].name, materials[i].color_cluster)

            return centers, clusters_list
        else:
            print("컬러 그룹과 컬러 머티리얼의 수가 맞지 않음.")
            return None
    else:
        print("머티리얼 리스트가 잘못되었습니다.")
        return None


# 머티리얼 함수
def import_blender_materials():
    for blender_material in bpy.data.materials:
        material = MaterialManager()
        material.create(blender_material)

        if material.data is not None:
            materials.append(material)
            branch_material_list(material)


def branch_material_list(material):
    if material.use_texture is True:
        texture_materials.append(material)

    elif material.use_texture is False:
        color_materials.append(material)


def set_color_master(color_clusters, color_centers):
    for i, color_cluster in enumerate(color_clusters):
        # 클러스터의 0번 머티리얼
        master_material = color_cluster[0]

        # 머티리얼의 컬러 값 -> 컬러 센터 값 적용
        master_material.color_float = color_centers[i]
        master_material.name = set_closest_color(master_material.color_float)
        master_material.replacement = False

        for material in color_cluster:
            material.master = master_material.data
        print(i, "번째 실행")
        print(master_material.name)


def replace_color_materials(color_clusters):
    for color_cluster in color_clusters:
        for material in color_cluster:
            if material.data is not material.master:
                for obj in bpy.data.objects:
                    if obj.type == 'MESH':
                        for slot in obj.material_slots:
                            if slot.material is material.data:
                                slot.material = material.master
                bpy.data.materials.remove(material.data)

            for blender_mat in bpy.data.materials:
                if blender_mat == material.data:
                    blender_mat.name = "M_" + material.name


def replace_texture_materials(material_list):
    for material in material_list:
        blender_mat = bpy.data.materials.get(material.name)
        if blender_mat.malt.material_type == 'Mesh':
            # 노드를 쓰는지 구분 (노드를 안쓰는 경우가 존재)
            if blender_mat.use_nodes:
                if 'Image Texture' in blender_mat.node_tree.nodes:
                    name = blender_mat.node_tree.nodes["Image Texture"].image.name
                    blender_mat.name = 'T_' + name

