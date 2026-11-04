# 장면 이미지 생성 → 영상 조립 (#100, 2026-11-04)

Claude 세션에는 이미지·영상 생성 도구가 없다. 장면 사진은 Codex의 image_gen(또는 외부 도구)으로 만들고, 아래 파일명으로 result/에 저장하면 `py -3.12 scripts/make_juice_video.py`가 자동으로 그 사진을 써서 15초 영상(9:16·1:1)을 다시 만든다.

## 저장 파일명 (세로 1080×1920 또는 그 이상, PNG/JPG)

| 파일 | 장면 | 자막(영상에서 자동으로 붙음) |
|---|---|---|
| result/juice_scene_01_bag.png | 아침 식탁 옆, 열린 캔버스 토트백 안주머니에 손이 납작한 크림색 사과즙 파우치 한 포를 넣는 순간. 창가 자연광, 손만 보임 | 출근 가방에 쏙 |
| result/juice_scene_02_pouch.png | 흰 바탕에 실제 파우치(참조 사진 그대로)가 세워져 정면, 라벨 글자 변형 없음, 부드러운 스튜디오 조명 | 청송사과즙 120ml 한 포 |
| result/juice_scene_03_pour.png | 밝은 나무 식탁, 손이 파우치 모서리를 뜯어 짧은 유리컵에 호박색 사과즙을 따르는 순간, 물방울 몇 개, 얼굴 없음 | 개봉해 바로, 또는 컵에 따라 |
| result/juice_scene_04_box.png | 크림색 손잡이 박스 뚜껑이 열려 파우치 50개가 가지런히 보이고 손이 한 포를 살짝 드는 장면, 45도 위에서 | 50포 한 박스 · 삼형제농원 |
| (선택) result/juice_scene_05_family.png | 식탁에 파우치 두세 포와 컵, 아이 손과 어른 손이 각각 한 포를 집는 장면(얼굴 없음) | (엔드카드 전 1.5초, 자막 없음) |

## 규칙 (영상 브리프와 동일)
- 파우치·박스·라벨은 참조 사진(result/juice_original_product_2026-10-28.webp, result/juice_pouch_label_roll_2026-11-04.jpg)을 그대로. 라벨 글자가 바뀌면 그 컷은 폐기하고 다시 생성.
- 얼굴·가짜 고객·효능·인증·지명 표지판·"직접 재배/저온 착즙/물 안 섞음" 문자 생성 금지. 손·사물·식탁·가방·컵만.
- 사진 안에 글자를 넣지 않는다(자막은 영상에서 붙임).

## Codex에 붙여 넣을 프롬프트

```text
작업 폴더 C:\Users\jun99\OneDrive - 계명대학교\바탕 화면\Analysis\toy_agent_project\advertisement_apple 에서 AGENTS.md → WORKSPACE_RULES.md 절차대로 새 요청 번호로 기록하고, result/juice_scene_prompts_2026-11-04.md의 표대로 장면 이미지 4장(+선택 1장)을 image_gen으로 생성해 지정 파일명으로 result/에 저장해. 참조 이미지는 result/juice_original_product_2026-10-28.webp와 result/juice_pouch_label_roll_2026-11-04.jpg. 각 장면은 세로 1080×1920 이상, 실사 사진 느낌, 손·사물만, 얼굴·글자·로고·인증·표지판 없음, 파우치 라벨은 참조 사진과 동일하게. 생성 후 라벨 글자가 참조와 다르면 그 장면을 다시 생성하고, 최종 5장을 한 장짜리 검수 시트(result/juice_scene_contact_2026-11-04.png)로 붙여 저장해. 그다음 `py -3.12 scripts/make_juice_video.py`를 실행해 result/juice_video_15s_9x16_2026-11-04.mp4와 1x1을 다시 만들고, result/juice_video_15s_contact_2026-11-04.png를 확인해 자막·라벨 오류가 없는지 보고해. 개인정보·비밀값 없는 산출물만 main에 커밋·푸시하고 원격 동일을 확인해. 상품·광고 설정은 바꾸지 마.
```

## 외부 도구(Sora/Veo/Kling/Runway)로 바로 영상을 만들 때
- 장면별 영문 프롬프트는 result/juice_ai_video_brief_2026-11-04.md의 "생성 프롬프트" 절을 그대로 쓴다. 각 컷 3~4초, 참조 이미지 첨부.
- 받은 클립을 result/juice_clip_01~04.mp4로 두면 다음 단계에서 자막·엔드카드를 입혀 합친다(요청 시 스크립트 추가).
