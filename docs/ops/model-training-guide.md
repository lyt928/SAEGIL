# 모델 학습 가이드

기준: 현재 저장소의 학습 노트북, 추론 코드, 실행 스크립트 기준

## 목적

이 문서는 팀원이 학습한 모델을 현재 프로젝트에 바로 연결할 수 있도록 최소 규격을 맞추기 위한 가이드입니다.

현재 백엔드 추론 코드는 다음 라벨을 핵심으로 사용합니다.

- `person`
- `helmet`
- `vest`

따라서 학습 결과가 이 규격과 크게 다르면, 모델이 잘 학습되어도 현재 시스템에서는 일부 탐지 결과를 활용하지 못할 수 있습니다.

## 현재 저장소에서 확인된 사항

### 학습 코드 위치

- `scripts/train/helmet_stage1.ipynb`

### 추론 코드가 기대하는 기본 모델 경로

- `models/weights/stage1_best.pt`

### 추론 코드가 현재 허용하는 핵심 라벨

- `person`
- `helmet`
- `vest`

참고:

- 일부 별칭은 내부에서 정규화됩니다.
- 예: `hardhat -> helmet`, `safety_vest -> vest`, `worker -> person`

하지만 가장 안전한 방법은 학습 데이터의 최종 클래스명을 처음부터 위 3개에 맞추는 것입니다.

## 권장 학습 규격

### 1. 1차 필수 클래스만 먼저 맞추기

현재 프로젝트의 1차 필수 범위는 아래 3개입니다.

- `person`
- `helmet`
- `vest`

추가 클래스가 있어도 되지만, 현재 서비스 로직은 위 3개 중심으로 동작합니다.

따라서 1차 모델은 가능하면 위 3개를 정확히 탐지하는 방향으로 맞추는 편이 좋습니다.

### 2. 클래스 이름을 추론 코드 기준에 맞추기

권장 최종 클래스명:

```text
person
helmet
vest
```

주의:

- `Person`처럼 대문자를 쓰면 현재 정규화로 흡수될 가능성은 있습니다.
- 다만 `no_helmet`, `none`, `goggles`, `boots` 같은 추가 클래스는 현재 백엔드 핵심 흐름에서 직접 쓰지 않습니다.
- 따라서 1차 발표/시연용 모델은 핵심 클래스 중심이 더 안전합니다.

### 3. 최종 산출물 파일명을 통일하기

현재 백엔드 기본 설정은 아래 파일을 읽습니다.

```text
models/weights/stage1_best.pt
```

따라서 학습 완료 후 최종 모델은 이 경로에 두는 것을 권장합니다.

권장 절차:

1. 학습 완료
2. `best.pt` 확인
3. 저장소의 `models/weights/stage1_best.pt`로 복사
4. 백엔드 `real` 모드에서 검증

## 현재 노트북 기준 주의사항

현재 노트북 `scripts/train/helmet_stage1.ipynb`에서는 다음 흔적이 확인됩니다.

- 데이터셋 설정 파일: `construction-ppe.yaml`
- 학습 실행 이름: `stage1_construction_ppe`
- 학습 결과 저장 폴더: `runs_ppe/...`
- 최종 복사 저장 경로: `C:\ppe_models\stage1_best.pt`

즉, 노트북 기본 흐름대로만 학습하면 저장소 내부 `models/weights/stage1_best.pt`가 자동 갱신되지 않을 수 있습니다.

그래서 팀원은 학습 후 반드시 아래 둘 중 하나를 해야 합니다.

1. `C:\ppe_models\stage1_best.pt`를 `models/weights/stage1_best.pt`로 복사
2. 또는 백엔드 실행 시 `MODEL_PATH`를 별도 경로로 지정

## 권장 학습 절차

### A. 환경 준비

- Python 가상환경 준비
- `ultralytics`, `torch`, `opencv-python`, `pyyaml`, `matplotlib` 등 설치
- GPU 사용 환경 확인

### B. 데이터셋 확인

- `construction-ppe.yaml` 경로가 실제 환경에서 유효한지 확인
- train/val 이미지 경로가 깨지지 않았는지 확인
- 클래스 이름이 추론 규격과 맞는지 확인

체크 포인트:

- `person`
- `helmet`
- `vest`

### C. 1차 학습

노트북 기준으로 확인된 기본 값은 아래와 같습니다.

- `epochs=30`
- `imgsz=640`
- `workers=8`
- 모델 후보: `yolo26n.pt`, `yolo11n.pt`, `yolov8n.pt`

이 값들은 시작점으로는 무난하지만, 실제 데이터셋 크기와 GPU 메모리에 따라 조정이 필요할 수 있습니다.

### D. 결과 확인

학습 후 반드시 확인할 것:

- `best.pt` 생성 여부
- val 결과
- confusion matrix 또는 예시 예측 이미지
- 실제 샘플 이미지에서 `person`, `helmet`, `vest`가 잘 나오는지

### E. 서비스 연결

최종 산출물을 아래로 복사:

```text
models/weights/stage1_best.pt
```

이후 실행:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\demo\run_backend_real.ps1
```

또는:

```powershell
$env:MODEL_PATH="models/weights/stage1_best.pt"
powershell -ExecutionPolicy Bypass -File .\scripts\demo\run_backend.ps1 -Mode real -DetectorMode real
```

## 팀원용 체크리스트

- 데이터셋 yaml 경로가 내 PC에서 유효한가
- 클래스 이름이 `person`, `helmet`, `vest`와 맞는가
- `best.pt`가 생성되었는가
- 최종 모델을 `models/weights/stage1_best.pt`로 복사했는가
- `run_backend_real.ps1`로 서버 기동이 되는가
- `/infer/image` 또는 샘플 영상에서 실제 탐지가 나오는가

## 팀원에게 바로 전달할 짧은 버전

1. 우선 1차 모델 클래스는 `person`, `helmet`, `vest`에 맞춰 주세요.
2. 학습 완료 후 최종 `best.pt`는 저장소의 `models/weights/stage1_best.pt`로 복사해 주세요.
3. 모델 저장 경로가 다르면 현재 백엔드에서 바로 안 읽을 수 있습니다.
4. 추가 클래스는 나중에 써도 되지만, 지금 서비스 로직은 위 3개 중심입니다.
5. 모델 연결 후 `run_backend_real.ps1`로 바로 검증해 주세요.

## 한 줄 요약

현재 프로젝트 기준으로는 "클래스명 3개 통일"과 "`stage1_best.pt` 경로 통일"이 가장 중요합니다.
