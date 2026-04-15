# 데이터셋 안내

학습 데이터는 `data/datasets` 아래에 데이터셋 단위로 정리합니다.

현재 정리된 데이터셋 구조:

```text
data/datasets/
├─ aihub-construction-safety/
│  └─ raw/
│     ├─ images/
│     └─ labels/
└─ aihub-opening-work/
   └─ raw/
      ├─ images/
      └─ labels/
```

데이터셋 설명:

- `aihub-construction-safety`
  - 기존 `Sample` 폴더에서 이동한 데이터
  - 공사 안전 관련 원천 이미지와 AIHub JSON 라벨 포함
- `aihub-opening-work`
  - 기존 `New_Sample` 폴더에서 이동한 데이터
  - 개구부 작업 관련 원천 이미지와 AIHub JSON 라벨 포함

정리 원칙:

- 원본 데이터는 `raw/` 아래에 그대로 보관합니다.
- YOLO 학습용으로 변환한 데이터는 별도 폴더를 만들어 분리합니다.
- 클래스 매핑, 변환 규칙, 출처 정보는 데이터셋별 README 또는 스크립트에 기록합니다.
