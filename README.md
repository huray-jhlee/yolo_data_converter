# YOLO Bounding Box Generator

## Overview
이 Python 스크립트는 이미지 데이터를 처리하여 YOLO 형식으로 바운딩 박스 주석을 생성합니다. 이미지를 읽고, 데이터베이스에서 바운딩 박스를 추출하여 YOLO 형식으로 변환한 뒤, 지정된 디렉토리에 저장합니다. 이 스크립트는 개발 및 운영 환경과 같은 다양한 서버 환경을 지원합니다.

## Requirements
다음 Python 패키지가 설치되어 있어야 합니다:

```bash
pip install opencv-python pandas tqdm sqlalchemy pymysql
```
혹은
```bash
pip install -r requirements.txt
```

## File Structure
```
.
├── main.py               # 메인 Python 스크립트
├── config.py             # 서버 세부 정보가 포함된 설정 파일
└── README.md             # 이 README 파일
```

## Usage
### 1. Arguments
| Argument      | Short | Type   | Description                                           |
|---------------|-------|--------|-------------------------------------------------------|
| `--class_name`| `-c`  | string | 데이터베이스에서 필터링할 대상 클래스 이름            |
| `--label`     | `-l`  | int    | YOLO 형식에서 사용할 클래스 레이블                    |
| `--save_dir`  | `-s`  | string | YOLO 주석 파일을 저장할 디렉토리 경로                 |
| `--server`    |       | string | 서버 유형: `dev` 또는 `main`                          |

### 2. Running the Scripts
먼저, 서버 정보가 포함된 유효한 config.py 파일을 준비합니다. config.py 파일에는 아래와 같은 서버 정보 클래스가 포함되어 있어야 합니다:
```python
class DevServer:
    DB_USERNAME = "your_dev_db_username"
    DB_PASSWORD = "your_dev_db_password"
    DB_HOST = "your_dev_db_host"
    DB_NAME = "your_dev_db_name"

class MainServer:
    DB_USERNAME = "your_main_db_username"
    DB_PASSWORD = "your_main_db_password"
    DB_HOST = "your_main_db_host"
    DB_NAME = "your_main_db_name"
```
그 다음, 적절한 인자를 사용하여 스크립트를 실행합니다:
```bash
python main.py --class_name "target_class_name" --label 1 --save_dir "./output" --server "dev"
```
### 3. output
각 이미지에 대해 YOLO 형식의 바운딩 박스 정보가 포함된 .txt 파일이 생성되며, 지정된 디렉토리에 저장됩니다. 파일의 각 줄은 다음 형식으로 저장됩니다:
```
<label> <x_center> <y_center> <box_width> <box_height>
```

### 4.Key Function
- `draw_bbox(image, bbox)`: 이미지에 바운딩 박스를 그립니다.
- `draw_with_label(image_path, bbox_info)`: 이미지에 바운딩 박스를 시각화합니다.
- `convert_to_yolo_format(bbox, width, height)`: 바운딩 박스 좌표를 YOLO 형식으로 변환합니다.