import os

# 생성할 디렉토리 구조 정의
project_structure = {
    "backend": {
        "app": {
            "api": {},
            "core": {},
            "models": {},
            "schemas": {},
            "services": {},
            "etl": {},
            "utils": {}
        },
        "tests": {}
    },
    "scripts": {}
}

def create_structure(base_path, structure):
    for name, subdirs in structure.items():
        path = os.path.join(base_path, name)
        os.makedirs(path, exist_ok=True)
        if isinstance(subdirs, dict):
            create_structure(path, subdirs)

if __name__ == "__main__":
    base_dir = "."  # 현재 디렉토리 (DD-Investment)
    create_structure(base_dir, project_structure)

    # 기본 파일 생성
    files_to_create = [
        "backend/app/main.py",
        "backend/app/__init__.py",
        "backend/app/etl/__init__.py",
        "backend/app/etl/fetch_api.py",
        "backend/app/etl/preprocess.py",
        "backend/app/etl/load.py",
        "backend/app/etl/pipeline.py",
        "scripts/run_etl.py",
        "scripts/init_db.py",
        "backend/requirements.txt",
        ".gitignore",
        "README.md",
        "docker-compose.yml",
        "backend/Dockerfile"
    ]

    for file in files_to_create:
        with open(file, "w", encoding="utf-8") as f:
            f.write("")  # 빈 파일 생성
    print("✅ 프로젝트 구조 생성 완료!")
