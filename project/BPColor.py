import bpy
import webcolors
import numpy as np
from sklearn.cluster import KMeans
from . import BPMaterial


# 리스트
def convert_color_float_to_int(color):
    return tuple(int(c * 255) for c in color)


def cluster_vector(list, clusters=30):
    # K-means 클러스터링 수행
    kmeans = KMeans(n_clusters=clusters, random_state=0).fit(list)

    # 클러스터 중심점(대표 색상) 가져오기
    cluster_centers = kmeans.cluster_centers_

    # 각 색상에 대한 클러스터 라벨 반환
    cluster_group = kmeans.labels_

    return cluster_centers, cluster_group


def get_color_name(color):
    color = convert_color_float_to_int(color)

    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - color[0]) ** 2
        gd = (g_c - color[1]) ** 2
        bd = (b_c - color[2]) ** 2
        min_colors[(rd + gd + bd)] = name

    return min_colors[min(min_colors.keys())]


def rename_color_materials(materials):
    for material in materials:
        new_name = get_color_name(material.diffuse_color)
        material.name = "M_" + new_name
