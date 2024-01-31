import bpy
from sklearn.cluster import KMeans
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
from PIL import Image
import os

if bpy.data.filepath:
    blend_file_path = bpy.path.abspath("//")
else:
    blend_file_path = None
save_dir = os.path.join(blend_file_path, "textures")


def get_unique_filename(directory, base_name, extension):
    counter = 1
    unique_name = f"{base_name}{extension}"

    # 이미 존재하는 파일 이름일 경우 고유한 이름 생성
    while os.path.exists(os.path.join(directory, unique_name)):
        unique_name = f"{base_name}_{counter}{extension}"
        counter += 1

    return unique_name


def clear_dir(dir_path):
    # 폴더 내의 모든 파일과 서브폴더 나열
    items = os.listdir(dir_path)

    # 폴더가 비어 있지 않다면
    if items:
        for item in items:
            item_path = os.path.join(dir_path, item)

            # 파일이면 삭제
            if os.path.isfile(item_path):
                os.remove(item_path)
            # 서브폴더이면 (폴더 내용도 삭제한 후) 폴더 삭제
            elif os.path.isdir(item_path):
                clear_dir(item_path)  # 재귀적으로 서브폴더 내용 삭제
                os.rmdir(item_path)
        print(f"{dir_path} 내의 모든 파일 및 폴더가 삭제되었습니다.")
    else:
        print(f"{dir_path}는 이미 비어 있습니다.")


def classify_image(img_path, model):
    # 사전 훈련된 모델 로드

    # 이미지 로드 및 전처리
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    # 이미지 분류
    predictions = model.predict(img_array)

    # 예측 결과 해석
    class_id, label, probability = decode_predictions(predictions, top=1)[0][0]
    # 가장 확률이 높은 결과 출력
    print(label)
    return label


def auto_rename_image(img_path, model):
    # 이미지 파일 필터링
    if img_path.lower().endswith((".png", ".jpg", ".jpeg")):
        img_path = os.path.join(save_dir, img_path)

        # 모델 가동
        label = classify_image(img_path, model)

        # TODO 텍스쳐 이미지 접두사"T_" 관련해서 디파인 따로 작성하거나, UI 패널로 빼기
        # temporarily code
        label = "T_" + label

        ext = os.path.splitext(img_path)[1]

        new_file_name = get_unique_filename(save_dir, label, ext)
        new_file_path = os.path.join(save_dir, new_file_name)
        new_name, _ = os.path.splitext(os.path.basename(new_file_path))

        # 파일 이름 변경
        os.rename(img_path, new_file_path)
        return label, new_file_path, new_name

# TODO 오퍼레이션 파트와 중복 방지 및 통폐합
def rename_texture_materials(model=MobileNetV2(weights='imagenet')):
    # 디렉토리가 없으면 생성
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 디렉토리 클리너
    clear_dir(save_dir)

    # 모든 패킹된 이미지 저장 및 경로 업데이트
    for image in bpy.data.images:
        if image.packed_files:
            # 파일 경로와 이름 설정
            file_path = os.path.join(save_dir, image.name + ".png")

            # 이미지 저장
            image.filepath_raw = file_path
            image.file_format = 'PNG'
            image.save()

            print(image.name)

            # 모든 머티리얼의 쉐이더 노드 업데이트
            for material in bpy.data.materials:
                # Name = None
                new_name = None
                if material.node_tree:
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image == image:
                            # Old name for debugging
                            old_name = image.name

                            # rename by machine learning
                            label, new_file_path, new_name = auto_rename_image(file_path, model)

                            # 각 파라미터 변경
                            image.name = new_name
                            node.image = image
                            node.image.filepath = new_file_path
                            print(f"{old_name} -> {new_name}")
                if new_name is not None:
                    material.name = new_name
                    print("머티리얼 이름까지 변경 성공!")
                    break

    print("모든 이미지가 저장되었으며, 쉐이더 경로가 업데이트되었습니다.")
    return