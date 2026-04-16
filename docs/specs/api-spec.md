# API 명세

## `GET /`
- 백엔드 상태 메시지와 현재 실행 모드 반환

## `GET /health`
- 헬스 체크 응답 반환

## `POST /infer`
- 탐지 결과(`detections`)와 위험구역(`zones`)을 직접 입력받아 PPE/이벤트/경고 결과 반환

## `POST /infer/image`
- base64 이미지 입력 기반 추론 API
- `detector_mode=real`이면 실제 YOLO 사용
- `detector_mode=mock`이면 미리 정의한 mock 탐지 결과 사용

## `GET /events`
- 최근 이벤트 목록 조회
- `limit`, `event_type`, `severity` 필터 지원

## `GET /events/{event_id}`
- 단일 이벤트 상세 조회

## `DELETE /events`
- 저장된 이벤트 로그 초기화

## `GET /zones`
- 현재 등록된 위험구역 목록 조회

## `GET /zones/{zone_id}`
- 단일 위험구역 조회

## `POST /zones`
- 위험구역 추가 또는 같은 ID 기준 덮어쓰기 저장

## `DELETE /zones/{zone_id}`
- 위험구역 삭제
