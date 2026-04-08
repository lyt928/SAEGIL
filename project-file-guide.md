# 프로젝트 파일 역할 정리

이 문서는 팀원이 프로젝트 구조를 한눈에 이해할 수 있도록, 폴더와 주요 파일의 역할을 설명한 안내서입니다.

## 먼저 어디부터 보면 되는가

처음 프로젝트를 파악할 때는 아래 순서로 보면 이해가 가장 빠릅니다.

1. `README.md`
2. `apps/backend/main.py`
3. `apps/backend/services/pipeline.py`
4. `core/detection`, `core/ppe`, `core/zones`, `core/risk`
5. `tests/unit`
6. `docs/implementation-checklist.md`

## 전체 구조 한눈에 보기

```text
프로젝트심화/
├─ apps/        : 실행 앱 코드
├─ core/        : 핵심 AI/판정 로직
├─ data/        : 샘플, 로그, 학습 데이터
├─ docs/        : 요구사항, 구조, API, 체크리스트 문서
├─ models/      : 모델 관련 파일과 클래스 정보
├─ scripts/     : 실행/학습/평가용 스크립트
├─ tests/       : 단위/통합 테스트
├─ README.md    : 프로젝트 소개
└─ requirements.txt : Python 의존성 목록
```

## 폴더별 역할

### `apps/`

- 실제로 실행되는 애플리케이션 코드가 들어 있습니다.
- 현재는 백엔드가 중심이고, 대시보드는 자리만 잡혀 있는 상태입니다.

### `core/`

- 프로젝트의 핵심 기능이 들어 있는 폴더입니다.
- 탐지, PPE 판정, 위험구역 판정, 경고 문구 생성, 이벤트 로그 저장 같은 핵심 로직이 여기 있습니다.

### `data/`

- 샘플 설정 파일, 이벤트 로그 저장 경로, 학습 원본 데이터가 들어갑니다.

### `docs/`

- 요구사항, 시스템 구조, API, 데모 시나리오, 구현 체크리스트 같은 문서를 모아둔 곳입니다.

### `models/`

- 모델 가중치와 클래스 이름 같은 모델 관련 리소스를 두는 폴더입니다.
- 현재는 클래스 이름 파일만 있고, 실제 가중치 파일은 아직 없는 상태입니다.

### `scripts/`

- 백엔드 실행, 학습, 평가, 데모용 스크립트를 두는 폴더입니다.
- 현재는 데모 실행 스크립트만 실제로 존재합니다.

### `tests/`

- 핵심 로직이 제대로 동작하는지 확인하는 테스트 파일들이 들어 있습니다.

## 파일별 역할 정리

### 루트 파일

- [README.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/README.md)
  - 프로젝트 소개 문서입니다.
  - 목표, 기능 범위, 구조, 향후 방향을 설명합니다.
- [requirements.txt](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/requirements.txt)
  - 프로젝트 실행에 필요한 Python 패키지 목록입니다.
  - `fastapi`, `uvicorn`, `opencv-python`, `ultralytics`, `pytest` 등이 들어 있습니다.
- [프심계획서.docx](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/프심계획서.docx)
  - 프로젝트 기획 문서 원본입니다.

### `apps/backend`

- [apps/backend/main.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/apps/backend/main.py)
  - FastAPI 앱의 시작점입니다.
  - 설정을 불러오고 라우터를 등록합니다.
- [apps/backend/api/routes.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/apps/backend/api/routes.py)
  - 백엔드 API 라우트를 정의합니다.
  - 현재는 `/health` 상태 확인 API가 있습니다.
- [apps/backend/services/pipeline.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/apps/backend/services/pipeline.py)
  - 한 프레임을 처리하는 핵심 파이프라인입니다.
  - 탐지 결과를 받아 PPE 판정, 위험구역 판정, 위험 이벤트 생성, 로그 저장, 경고 문구 생성을 연결합니다.
- [apps/backend/schemas/events.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/apps/backend/schemas/events.py)
  - API 응답 형식을 정의하는 스키마 파일입니다.
  - 현재는 `HealthResponse`만 있습니다.
- [apps/backend/config/settings.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/apps/backend/config/settings.py)
  - 앱 설정값을 관리합니다.
  - 앱 이름, 포트, 로그 경로, 카메라 소스, 모델 경로 등이 여기에 있습니다.
- `apps/backend/__init__.py`, `api/__init__.py`, `services/__init__.py`, `schemas/__init__.py`, `config/__init__.py`
  - Python 패키지 인식을 위한 초기화 파일입니다.
  - 별도 로직은 없습니다.

### `apps/dashboard`

- [apps/dashboard/README.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/apps/dashboard/README.md)
  - 대시보드 앱에 대한 자리 표시용 문서입니다.
  - 아직 실제 대시보드 코드는 구현되지 않았습니다.

### `core/camera`

- [core/camera/stream.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/core/camera/stream.py)
  - 카메라 설정 정보를 다루는 파일입니다.
  - 현재는 카메라를 실제로 열기보다는 설정값을 구조화하는 수준입니다.
- `core/camera/__init__.py`
  - 패키지 초기화 파일입니다.

### `core/detection`

- [core/detection/yolo_detector.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/core/detection/yolo_detector.py)
  - YOLO 모델 로딩과 추론을 담당하는 래퍼 클래스입니다.
  - 모델 파일 존재 여부 확인, 라벨 정규화, confidence 필터링, 탐지 결과 파싱을 수행합니다.
- [core/detection/types.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/core/detection/types.py)
  - 탐지 결과 구조를 정의하는 타입 파일입니다.
- `core/detection/__init__.py`
  - 패키지 초기화 파일입니다.

### `core/ppe`

- [core/ppe/matcher.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/core/ppe/matcher.py)
  - 사람 박스와 안전모, 안전조끼 박스를 매칭해서 PPE 착용 여부를 판정합니다.
  - 이 프로젝트의 `미착용 판정` 핵심 로직입니다.
- `core/ppe/__init__.py`
  - 패키지 초기화 파일입니다.

### `core/zones`

- [core/zones/polygon_zone.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/core/zones/polygon_zone.py)
  - 다각형 위험구역 내부에 사람이 들어왔는지 판정합니다.
  - 사람의 발 위치를 기준으로 침입 여부를 계산합니다.
- `core/zones/__init__.py`
  - 패키지 초기화 파일입니다.

### `core/risk`

- [core/risk/rules.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/core/risk/rules.py)
  - PPE 판정 결과와 위험구역 이벤트를 바탕으로 실제 위험 이벤트를 생성합니다.
  - 현재는 안전모 미착용, 안전조끼 미착용 중심의 기본 규칙이 구현되어 있습니다.
- `core/risk/__init__.py`
  - 패키지 초기화 파일입니다.

### `core/alerts`

- [core/alerts/overlay.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/core/alerts/overlay.py)
  - 위험 이벤트를 사람이 읽을 수 있는 경고 문구로 바꿔주는 파일입니다.
  - 예: 위험구역 진입, 안전모 미착용 등
- `core/alerts/__init__.py`
  - 패키지 초기화 파일입니다.

### `core/logging`

- [core/logging/event_logger.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/core/logging/event_logger.py)
  - 이벤트를 JSONL 파일로 저장하고 다시 읽는 역할을 합니다.
  - 이벤트 ID와 타임스탬프도 여기서 자동으로 추가됩니다.
- `core/logging/__init__.py`
  - 패키지 초기화 파일입니다.

### `data`

- [data/samples/sample_zones.json](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/data/samples/sample_zones.json)
  - 위험구역 예시 설정 파일입니다.
  - 다각형 구역 데이터를 어떤 형태로 둘지 보여주는 샘플입니다.
- [data/datasets/README.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/data/datasets/README.md)
  - 학습 데이터가 어디에 있고 어떻게 정리되어 있는지 설명합니다.
- [data/datasets/aihub-construction-safety](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/data/datasets/aihub-construction-safety)
  - 공사 안전 관련 AIHub 원본 학습 데이터입니다.
- [data/datasets/aihub-opening-work](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/data/datasets/aihub-opening-work)
  - 개구부 작업 관련 AIHub 원본 학습 데이터입니다.

### `models`

- [models/labels/classes.txt](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/models/labels/classes.txt)
  - 현재 프로젝트가 기본적으로 생각하는 탐지 클래스 목록입니다.
  - 현재는 `person`, `helmet`, `vest` 3개가 정의되어 있습니다.

### `scripts`

- [scripts/demo/run_backend.ps1](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/scripts/demo/run_backend.ps1)
  - FastAPI 백엔드를 실행하는 PowerShell 스크립트입니다.
- [scripts/demo/README.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/scripts/demo/README.md)
  - 데모 스크립트 설명 문서입니다.
- [scripts/train/README.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/scripts/train/README.md)
  - 학습 스크립트를 둘 위치를 안내하는 문서입니다.
  - 아직 실제 학습 스크립트는 없습니다.
- [scripts/eval/README.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/scripts/eval/README.md)
  - 평가 스크립트를 둘 위치를 안내하는 문서입니다.
  - 아직 실제 평가 스크립트는 없습니다.

### `tests/unit`

- [tests/unit/test_ppe.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/tests/unit/test_ppe.py)
  - PPE 매칭 로직이 제대로 동작하는지 테스트합니다.
- [tests/unit/test_zones.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/tests/unit/test_zones.py)
  - 위험구역 침입 판정이 올바른지 테스트합니다.
- [tests/unit/test_event_logger.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/tests/unit/test_event_logger.py)
  - 이벤트 로그 저장과 조회가 제대로 되는지 테스트합니다.
- [tests/unit/test_yolo_detector.py](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/tests/unit/test_yolo_detector.py)
  - YOLO 결과 파싱과 라벨 정규화 로직을 테스트합니다.

### `tests/integration`

- [tests/integration/README.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/tests/integration/README.md)
  - 통합 테스트를 추가할 위치를 설명하는 문서입니다.
  - 아직 실제 통합 테스트는 없습니다.

### `docs`

- [docs/requirements.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/docs/requirements.md)
  - 프로젝트 핵심 요구사항 요약 문서입니다.
- [docs/architecture.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/docs/architecture.md)
  - 시스템 처리 흐름을 간단히 적어둔 구조 문서입니다.
- [docs/api-spec.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/docs/api-spec.md)
  - 현재 구현된 API 명세 문서입니다.
- [docs/demo-scenario.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/docs/demo-scenario.md)
  - 데모를 어떤 흐름으로 보여줄지 정리한 문서입니다.
- [docs/implementation-checklist.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/docs/implementation-checklist.md)
  - 현재 구현 완료/미완료 상태를 점검하는 체크리스트입니다.
- [docs/project-file-guide.md](/c:/Users/dlaxo/OneDrive/바탕%20화면/프로젝트심화/docs/project-file-guide.md)
  - 지금 보고 있는 파일 역할 정리 문서입니다.

## 현재 코드 흐름 요약

현재 핵심 흐름은 아래처럼 연결됩니다.

1. `apps/backend/main.py`에서 FastAPI 앱 시작
2. 필요 시 `core/detection/yolo_detector.py`로 객체 탐지 수행
3. 탐지 결과를 `apps/backend/services/pipeline.py`로 전달
4. `core/ppe/matcher.py`에서 PPE 판정
5. `core/zones/polygon_zone.py`에서 위험구역 침입 판정
6. `core/risk/rules.py`에서 위험 이벤트 생성
7. `core/logging/event_logger.py`에서 이벤트 저장
8. `core/alerts/overlay.py`에서 경고 문구 생성

## 팀원이 기억하면 좋은 포인트

- 백엔드 시작 파일은 `apps/backend/main.py` 입니다.
- 핵심 처리 흐름은 `apps/backend/services/pipeline.py` 에 모여 있습니다.
- PPE, 위험구역, 위험 규칙은 각각 `core/ppe`, `core/zones`, `core/risk`로 역할이 나뉘어 있습니다.
- 테스트는 `tests/unit`부터 보면 각 모듈이 무엇을 의도했는지 빠르게 이해할 수 있습니다.
- `__pycache__` 폴더와 `.pyc` 파일은 Python 캐시 파일이므로, 코드 이해 대상으로 보지 않아도 됩니다.
