# image-prompt-reverse — 한국어 포크

참고 이미지의 구도·화풍·색감·조명·재질을 분석해 이미지 생성용 프롬프트를 작성하는 스킬이다. [LunarXuan/image-prompt-reverse](https://github.com/LunarXuan/image-prompt-reverse)를 기반으로 한국어 출력과 개인 Omarchy 환경에 맞춰 관리한다.

로컬 변경: 2026-10-09. 상류 이름과 이미지 분석 지침을 유지하고, 기본 출력 언어·UI 표시·이 README를 수정했다.

## 사용

Codex에 참고 그림을 첨부하고 호출한다.

```text
$image-prompt-reverse 이 이미지의 생성용 프롬프트를 작성해줘.
```

기본 출력:

- 한국어 생성 프롬프트: 450~700자의 자연어 문단.
- 영어 생성 프롬프트: 한국어와 같은 내용.
- Negative Prompt: 이미지에 맞춘 영어 구절 10~15개.

언어·길이·생성 모델을 요청에 지정하면 그 조건을 우선한다. 생성된 프롬프트를 이미지 생성 도구에 넣어 결과를 확인한다. 사진·삽화·3D·제품·캐릭터·포스터 등을 다루며, 삽화는 그린 내용과 선·형태·명암·색·질감의 표현 방식을 구분해 분석한다.

## 내 PC의 설치 구조

| 역할 | 위치 |
| --- | --- |
| 포크 수정·상류 병합 | `~/Projects/image-prompt-reverse`, `ko` 브랜치 |
| 설치 정본(스킬 사본) | `~/Projects/agent-skills/skills/image-prompt-reverse/` |
| 한국어 패치 | `git diff upstream/main...ko -- . ':!tools'` |
| 설치본의 상류 기준 | `git merge-base ko upstream/main`, agent-skills 커밋 메시지 |
| 갱신 도구 | `tools/sync.py` |

omarchy-setup 의 `bash setup.sh skills` 가 agent-skills 의 스킬마다 `~/.agents/skills`·`~/.claude/skills`·`~/.codex/skills`·`~/.pi/agent/skills` 에 링크를 건다. 다른 PC 는 agent-skills 만 있으면 된다(이 포크는 없어도 된다).

## 상류 업데이트와 내 수정

Git remote는 `origin` = [parapuda/image-prompt-reverse](https://github.com/parapuda/image-prompt-reverse), `upstream` = 원저장소다. `ko`에서 내 수정과 상류 변경을 관리하고, 푸시 기본 대상은 `origin`이다.

이 저장소에서 실행한다.

```bash
python3 tools/sync.py check
python3 tools/sync.py update
python3 tools/sync.py install
```

- `check`: 상류를 fetch하고 아직 반영하지 않은 커밋과 로컬 변경을 보여준다.
- `update`: 작업 트리가 깨끗하면 상류를 병합하고 설치 정본을 갱신한다. 병합은 커밋 전에 멈추므로 `ko`의 diff를 검토한 뒤 직접 커밋한다. 충돌이나 미커밋 변경이 있으면 설치본을 유지한다.
- `install`: `ko`에서 직접 수정하거나 병합 충돌을 해결한 내용을 설치 정본에 반영한다. Git 이 추적하는 파일만, `tools/` 는 빼고 들어간다(새 파일은 먼저 Git에 등록).

갱신 도구는 커밋·푸시를 실행하지 않는다. `ko` 의 수정과 agent-skills 의 설치본 변경을 각각 검토해 저장한다(agent-skills 커밋 메시지에 상류 커밋을 적는다).

## 스킬 파일

- `SKILL.md`: 적용 조건과 출력 형식.
- `references/analysis-framework.md`: 공통 이미지 분석 기준.
- `references/category-guides.md`: 피사체·매체별 분석 기준.
- `references/illustration-style.md`: 삽화 화풍 분석 기준.
- `agents/openai.yaml`: 한국어 표시 이름과 호출 예시.

## 출처와 라이선스

원저장소: [LunarXuan/image-prompt-reverse](https://github.com/LunarXuan/image-prompt-reverse). 최초 도입 기준: [4dead0a32e2312e56a14ebf3658ee75c9b865055](https://github.com/LunarXuan/image-prompt-reverse/commit/4dead0a32e2312e56a14ebf3658ee75c9b865055).

원저장소의 [GPL-3.0 라이선스](LICENSE)를 유지한다.
