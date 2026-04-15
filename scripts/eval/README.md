# 평가 스크립트 안내

- `validate.py`: 단일 모델 검증 스크립트
- `compare_experiments.py`: 두 실험 결과를 비교하고 JSON, Markdown, PNG 리포트를 생성

예시:

```powershell
python scripts\eval\compare_experiments.py --baseline reports\experiments\run_a --candidate reports\experiments\run_b
```
