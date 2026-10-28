"""Turn verified public seller pages into attributed advertising drafts."""
from pathlib import Path
import json, base64, html

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'result'
e=json.loads((R/'juice_seller_evidence_2026-10-28.json').read_text(encoding='utf-8'))
u=e['sources']
photo='data:image/webp;base64,'+base64.b64encode((R/'juice_original_product_2026-10-28.webp').read_bytes()).decode()
drafts=[
 ('01 산지·재배자','청송 얼음골에서 키운 사과, 한 포로','삼형제농원이 직접 재배한 청송사과로 만든 사과즙. 얼음골 사과하나, 120ml × 50포.','청송사과농가','직접 키운 청송사과로 만든 사과즙','당근의 직접 재배 소개와 네이버 농원 소개. 새로운 출고 제품의 원물도 동일한지 최종 대조.'),
 ('02 원재료·제품','청송사과 100%, 한 포의 사과즙','청송얼음골 사과즙 사과하나. 사과 100%의 원재료 표시와 실제 파우치를 함께 보여줍니다.','청송사과100%','청송사과 100% 얼음골 사과즙 120ml 50포','실제 상세 원재료표: 사과100%(국내산 청송군). 제품사진 라벨과 다음 출고 로트 일치 확인.'),
 ('03 생활 속 한 포','아침에도, 외출할 때도 청송사과즙 한 포','120ml 파우치 50포 구성. 한 포씩 꺼내 마시고, 실제 원재료·공정·출고 정보를 확인하세요.','청송사과즙한포','청송사과즙 120ml 50포, 한 포씩 간편하게','실제 파우치 규격 및 쿠팡 후기의 음용 상황. 특정 건강 효과나 재구매율을 약속하지 않음.'),
]
for _,_,_,s,l,_ in drafts:
    assert len(s)<=10 and len(l)<=30 and '청송사과' in s and '청송사과' in l
cards=''.join(f'''<article class="card"><div class="eyebrow">{label}</div><img style="width:100%;height:250px;object-fit:contain;background:white" src="{photo}" alt="실제 얼음골 사과하나 파우치 원본사진"><h3>{headline}</h3><p>{body}</p><p><b>쇼핑광고 짧은 문구</b><br>{short} ({len(short)}자)</p><p><b>긴 문구</b><br>{long} ({len(long)}자)</p><p class="note">{basis}</p></article>''' for label,headline,body,short,long,basis in drafts)
section=f'''<section id="seller-story"><style>#seller-story article.card p b{{font-size:15px;display:inline;color:inherit}}#seller-story article.card h3{{font-size:20px;line-height:1.5}}</style><div class="eyebrow">2026.10.28 보강 · 가격 소구에서 산지와 실제 제품으로</div>
<h2>청송사과를 키우는 농원과, 실제 사과즙을 보여줍니다</h2>
<p>광고의 중심을 <b>청송사과 → 청송 얼음골의 재배자 → 사과 100% → 얼음골 사과하나 → 120ml×50포</b>로 연결합니다. 가격 비교는 내부 판단 자료로 두고 광고 제목·홍보문구에서 가격의 우월성을 내세우지 않습니다.</p>
<div class="flow"><div><b>어디서?</b><br>경북 청송·얼음골</div><div><b>누가?</b><br>직접 재배하는 삼형제농원</div><div><b>무엇을?</b><br>사과100% 사과하나</div><div><b>어떻게 받나?</b><br>120ml×50포·출고정보</div></div>
<h3>친구분의 판매 채널을 연결했습니다</h3>
<table><tr><th>채널</th><th>확인한 연결과 활용 정보</th></tr><tr><td>네이버</td><td>삼형제농원·김규현. 청송 얼음골의 삼형제 농가 소개. 원재료표와 실제 사과하나 포장 확인.</td></tr><tr><td>쿠팡</td><td>같은 상호·대표자, 동일 상품명·120ml50포 확인. 공개 상품번호8698914518. 판매자 답변에서 저온착즙·기계세척 안내. 공주 신풍면의 동명업체는 제외.</td></tr><tr><td>당근</td><td>업체가 네이버 threebrothersfarmm으로 직접 연결. 동일 지역·상품과 청송사과식품 상호변경 예정 소개. 직접 재배 사과를 사용한다는 판매자 게시글 확인.</td></tr></table>
<h3>원재료표와 상품정보에서 확보한 내용</h3>
<table><tr><th>상품명</th><td>청송얼음골 사과즙 · 포장 표기 얼음골 사과하나</td></tr><tr><th>원재료·산지</th><td>사과100% · 국내산 청송군 (공개 상세이미지 표시)</td></tr><tr><th>규격</th><td>120ml×50포 · 총6L · 파우치형</td></tr><tr><th>제조원·판매원</th><td>상세이미지에는 청송사과식품. 네이버 제조사 필드는 청송 삼형제농원. 다음 출고 라벨을 기준으로 표기를 통일할 항목.</td></tr><tr><th>공정 문의</th><td>쿠팡 판매자가2025-07-05 저온착즙·기계세척이라고 답변. 당근 글에도 저온착즙·설탕/물엿/꿀을 넣지 않는다고 설명. 구체 온도·살균방식·신규 로트는 확인 대상.</td></tr></table>
<p class="note">네이버 사업자번호 상세는 캡차로 확인하지 못했으므로 번호 전체 대조 완료로 적지 않습니다. 당근의 자사 스토어 직접 연결은 확인했습니다. 공개 판매자 설명은 확보했으며, 인증·시험성적·새 출고 제조기록까지 확보한 것은 아닙니다.</p>
<h3>바로 사용할 광고 원고 3안</h3><p>현 쇼핑광고 제목은 <b>청송사과즙 얼음골 사과하나 120ml 50포</b>를 유지합니다. 아래는 산지·원재료·음용 상황을 분리한 후속 홍보문구와 상세 첫 화면 시안입니다. 새 문구는 아직 광고계정에 등록하지 않았습니다.</p><div class="cards">{cards}</div>
<p class="note">사진은 현재 네이버 상품 원본입니다. 문구가 함께 있는 이 설명 카드 자체를 쇼핑 대표이미지로 올리는 안은 아닙니다. 한 소재에 모든 정보를 몰아넣지 않고 제목→홍보문구→상세 첫 화면→FAQ로 나눕니다.</p>
<h3>판매자 소개를 실제 구매 불안 해소로 연결합니다</h3>
<table><tr><th>확인된 고객 반응</th><th>광고·상세페이지에서 할 일</th></tr><tr><td>깔끔하거나 진한 맛, 한 포씩 마시는 편의</td><td>실물 파우치와 음용 장면으로 전달. 모든 사람이 같은 맛을 느낀다고 보장하지 않음.</td></tr><tr><td>기대했던 생사과 같은 맛과 차이</td><td>원재료와 실제 착즙·살균 과정을 FAQ로 설명. 후기만으로 가열 온도나 공정을 판단하지 않음.</td></tr><tr><td>일부 파우치 내용량 지적</td><td>현재 출고 제품의 충전·검수 자료와120ml 표시 대조. 파우치 크기만으로 용량이 충분하다고 반박하지 않음.</td></tr><tr><td>배송 지연 경험</td><td>출고 가능일과 마감시각을 통일. 상세이미지는12시, 구조화배송/당근공지는11시로 서로 다름.</td></tr></table>
<p class="note">쿠팡 첫 페이지 베스트순10개 후기에서 확인한 주제이며 전체 불만율이 아닙니다. 이름·연락처·원문 후기는 저장하지 않았습니다. 후기 이미지를 광고에 복제하지 않고 소비자 표현을 제품 설명 개선에 활용합니다.</p>
<h3>채널별 신뢰는 확보하되 합산하지 않습니다</h3>
<p>10/28 공개 화면의 쿠팡 상품평104개는 상품 전체, 당근 후기325개·단골986명은 업체 전체, 네이버 리뷰1개는 해당 상품 기준입니다. 이를 합쳐 사과즙 후기430개·구매자 수·재구매율로 광고하지 않습니다. 당근 생과 후기의 만족도는 사과즙의 검증 결과가 아닙니다.</p>
<details><summary>현재 광고에서 보류할 주장과 정보 정정 목록</summary><p>상세에3대·4만평·부사15Brix·친환경·GAP·NFC가 적혀 있으나 현재 원료·공정·인증 적용 범위는 추가 대조가 필요합니다. 부사의 당도 수치를 사과즙 당도 보장으로 바꾸지 않습니다. 원재료표의 당류15.58g/120ml와 설탕 첨가 여부는 다른 정보이므로 제로슈거·당류0g 표현을 쓰지 않습니다. 현재 제조일/소비기한 모순과 제조원 표기를 바로잡고 출고 가능일을 통일해야 합니다. 건강 회복·질병·어린이 안전을 보장하는 표현은 광고 원고에 넣지 않았습니다.</p></details>
<p><b>추천 첫 화면:</b><br>청송 얼음골에서 키운 사과, 한 포에 담았습니다.<br>청송사과100% · 얼음골 사과하나 · 120ml×50포<br>직접 재배하는 삼형제농원의 소개와 실제 원재료표·파우치를 이어 보여줍니다.</p>
<p class="note">출처: <a href="{u['naver']}">네이버 실제상품</a> · <a href="{u['coupang']}">쿠팡 상품·판매자답변</a> · <a href="{u['daangn']}">당근 업체</a> · <a href="{u['farm_post']}">직접재배 소개</a> · <a href="{u['process_post']}">착즙 소개</a>. 새 원고는 원재료/다음 출고 구성과 대조한 후 적용합니다. 현재 제목 시험을 유지하며 가격·입찰·예산은 바꾸지 않았습니다.</p></section>'''
(ROOT/'scripts/seller_story_section.html').write_text(section,encoding='utf-8')
print('Built seller story: 3 attributed ad drafts and source-backed fact tables.')
