"""Recheck small observations against denominators before recommending action.

Inputs are saved, anonymous reports, not fresh reads of Naver or order records.
No advertisements or storefront settings are changed.
"""
from pathlib import Path
from collections import defaultdict
import csv
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'result'
sys.path.insert(0, str(ROOT / '.venv-report'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read(name):
    return json.loads((R / name).read_text(encoding='utf-8-sig'))

def number(v):
    return int(re.sub(r'[^0-9]', '', str(v)) or 0)

def blank():
    return dict(impressions=0, clicks=0, cost_krw=0, conversion_events=0)

def add(dest, row):
    for key, col in [('impressions', 4), ('clicks', 5), ('cost_krw', 8), ('conversion_events', 10)]:
        dest[key] += number(row[col])

def rates(d):
    return {**d, 'ctr_pct': d['clicks'] / d['impressions'] * 100 if d['impressions'] else None}

source = read('ads_media_2025-11-01_2026-01-31.json')
assert source['start'] == '2025-11-01' and source['end'] == '2026-01-31'
assert len({tuple(r[:4]) for r in source['rows']}) == len(source['rows'])
devices = defaultdict(blank)
cross = defaultdict(blank)
total = blank()
for row in source['rows']:
    assert row[2] in ['모바일', 'PC']
    assert row[3] in ['검색', '콘텐츠']
    channel = '콘텐츠' if row[3] == '콘텐츠' else ('네이버 검색' if '네이버' in row[1] else '외부 검색')
    add(devices[row[2]], row)
    add(cross[(row[2], channel)], row)
    add(total, row)
assert total == dict(impressions=26783, clicks=112, cost_krw=8481, conversion_events=1)
assert devices['모바일']['clicks'] == 104 and devices['PC']['clicks'] == 8
mobile_impression_share = devices['모바일']['impressions'] / total['impressions'] * 100
mobile_click_share = devices['모바일']['clicks'] / total['clicks'] * 100

with (R / 'ads_search_term_clicks_2025-11-01_2026-01-31.csv').open(encoding='utf-8-sig') as f:
    terms = list(csv.DictReader(f))
assert len(terms) == 23 and all(int(r['클릭']) > 0 for r in terms)
query_totals = {key: sum(int(r[key]) for r in terms) for key in ['노출', '클릭', '광고비(원)', '전체전환']}
search_total = {k: sum(d[k] for (device, channel), d in cross.items() if channel != '콘텐츠') for k in total}
assert query_totals['클릭'] == search_total['clicks'] == 104
assert query_totals['광고비(원)'] == search_total['cost_krw'] == 7678
assert query_totals['노출'] == 15283 < search_total['impressions'] == 21216
queries = {r['검색어']: r for r in terms}
selected = []
for query in ['청송사과즙', '청송얼음골사과즙', '형제농원']:
    r = queries[query]
    selected.append(dict(query=query, impressions=int(r['노출']), clicks=int(r['클릭']),
                         ctr_pct=int(r['클릭']) / int(r['노출']) * 100,
                         cost_krw=int(r['광고비(원)']), conversion_events=int(r['전체전환'])))
identity = queries['얼음골사과하나즙']
assert int(identity['전체전환']) == 1 and int(identity['클릭']) == 1
assert all(r['conversion_events'] == 0 for r in selected)
listing = read('juice_own_listing_2026-10-27.json')
seller = read('juice_seller_evidence_2026-10-28.json')
assert listing['purchase_limit'] == '최대구매1개(1인)'

result = {
    'rechecked_on': '2026-10-28', 'period': [source['start'], source['end']],
    'source_files': ['ads_media_2025-11-01_2026-01-31.json',
                     'ads_search_term_clicks_2025-11-01_2026-01-31.csv',
                     'juice_own_listing_2026-10-27.json', 'juice_seller_evidence_2026-10-28.json'],
    'media_row_count': len(source['rows']), 'total': total,
    'devices': {k: rates(v) for k, v in devices.items()},
    'device_channel': [dict(device=k[0], channel=k[1], **rates(v)) for k, v in cross.items()],
    'mobile_impression_share_pct': mobile_impression_share,
    'mobile_click_share_pct': mobile_click_share,
    'click_share_minus_impression_share_pp': mobile_click_share - mobile_impression_share,
    'selected_queries': selected,
    'query_table_scope': {'rows': len(terms), 'clicked_queries_only': True, 'totals': query_totals,
                          'all_search_totals': search_total},
    'single_identity_query_event': {'query': '얼음골사과하나즙', 'impressions': 1, 'clicks': 1,
                                  'conversion_events': 1, 'interpretation': '단일 사례; 승자·1클릭 구매율·반복 가능성 판단 불가'},
    'listing_as_of': listing['date'],
    'limitations': ['광고그룹 과거 실적; 당시 상품구성 및 타깃 단독귀속 미확인',
                    '노출·클릭은 고유 사용자 수가 아님',
                    '검색어 리포트는 클릭 있는 검색어만 포함; 미클릭 검색어 분포는 미확인',
                    '기기·검색어·매체 비교는 무작위 실험 아님. 위치·경쟁·의도·표본수 차이가 있음',
                    '페이지 문제는 10/27~28 저장 관찰. 현재 페이지·실제 새 로트 상태를 새로 확인한 것이 아님']}
(R / 'juice_eda_decisions_2026-10-28.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

plt.rcParams.update({'font.family': 'Malgun Gothic', 'axes.unicode_minus': False,
                     'font.size': 12, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': 'white', 'axes.facecolor': 'white'})
blue, gray = '#286491', '#b4bdc5'
fig, ax = plt.subplots(figsize=(11, 4.8))
fig.subplots_adjust(left=.19, right=.96, top=.76, bottom=.25)
for y, key, title in [(1, 'impressions', '광고 노출 구성'), (0, 'clicks', '광고 클릭 구성')]:
    m, pc = devices['모바일'][key], devices['PC'][key]
    share = m / (m + pc) * 100
    ax.barh(y, share, color=blue, height=.46, label='모바일' if y == 1 else None)
    ax.barh(y, 100 - share, left=share, color=gray, height=.46, label='PC' if y == 1 else None)
    ax.text(share / 2, y, f'모바일 {share:.1f}%  ({m:,}회)', color='white', ha='center', va='center')
    ax.text(99, y + .33, f'PC {100-share:.1f}% ({pc:,}회)', ha='right', fontsize=11)
ax.set(yticks=[1, 0], yticklabels=['광고 노출 구성', '광고 클릭 구성'], xlim=(0, 100), ylim=(-.5, 1.65), xlabel='전체에서 차지하는 비중 (%)')
ax.spines[['left', 'right', 'top']].set_visible(False)
ax.legend(loc='upper left', bbox_to_anchor=(0, 1.3), frameon=False, ncol=2)
fig.suptitle('모바일은 클릭뿐 아니라 노출도 대부분을 차지했습니다', x=.05, ha='left', fontsize=17, fontweight='bold')
fig.text(.05, .10, '그림 15. 광고그룹 매체 리포트, 2025.11.01~2026.01.31. 노출 26,783회·클릭 112회.', fontsize=10.5)
fig.text(.05, .04, '비중은 접점 규모를 보여줍니다. 모바일의 클릭 반응이나 판매 효과가 더 좋다는 뜻은 아닙니다.', fontsize=10.5)
fig.savefig(R / 'juice_figures/15_mobile_denominator_2026-10-28.png', dpi=160)
plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 5.1))
fig.subplots_adjust(left=.26, right=.95, top=.80, bottom=.29)
for i, r in enumerate(selected):
    y = len(selected)-1-i
    ax.barh(y, r['ctr_pct'], color=blue, height=.48)
    ax.text(r['ctr_pct'] + .18, y, f"{r['ctr_pct']:.2f}% ({r['clicks']}/{r['impressions']:,})", va='center', fontsize=11)
ax.set(yticks=[2,1,0], yticklabels=[r['query'] for r in selected], xlim=(0,16), xlabel='광고 노출 중 클릭한 비율 (%)')
ax.spines[['left','right','top']].set_visible(False)
fig.suptitle('어떤 이름으로 찾았는지에 따라 클릭 반응이 달랐습니다', x=.05, ha='left', fontsize=17, fontweight='bold')
fig.text(.05, .17, '그림 16. 2025.11.01~2026.01.31, 클릭이 있는 23개 검색어 중 비교할 3개를 선택했습니다.', fontsize=10.5)
fig.text(.05, .10, '괄호 = 클릭/노출. 파란 막대 = 클릭률. 선택한 3개 검색어의 귀속 전환은 모두 0건입니다.', fontsize=10.5)
fig.text(.05, .035, '상품을 이미 아는 사람·광고 위치·경쟁 차이일 수 있습니다. 제목 변경 효과나 매출 우열이 아닙니다.', fontsize=10.5)
fig.savefig(R / 'juice_figures/16_query_specificity_2026-10-28.png', dpi=160)
plt.close(fig)
print('Verified 51 media rows, device/channel cuts and 23 clicked queries; saved JSON and two figures.')

# Revise the existing analytical report; keep earlier evidence and appendices.
report = R / 'apple_juice_analysis_2026-10-20.md'
text = report.read_text(encoding='utf-8')
section = '''## 10/28 작은 관찰에서 문제와 실행을 연결한 재검토 (#73)

지금 바꿀 결정은 세 가지입니다. **판매 정보의 충돌을 먼저 확인하고, 검색명과 실물 포장의 연결을 점검하며, 모바일에서 상품을 알아보기 쉬운지 확인합니다.** 아래 수치는 판매 부진의 원인을 확정한 결과가 아니라, 그 결정을 고르기 위해 비교한 근거입니다. 36개 개선 후보를 같은 비중으로 실행하지 않습니다.

### 1. “모바일 클릭 92.9%”에서 빠졌던 질문: 노출도 모바일에 몰렸는가?

![모바일의 노출 비중과 클릭 비중 비교](juice_figures/15_mobile_denominator_2026-10-28.png)

**그림 15 해석:** 모바일 비중은 클릭 92.9%보다 노출 95.8%에서 더 높습니다. 모바일이 특별히 더 잘 반응했다는 해석은 지지하지 않습니다. 현재 광고 접점 대부분이 모바일이라는 사실은 유지됩니다.

| 비교 | 모바일 | PC | 이 비교로 알 수 있는 것 |
|---|---:|---:|---|
| 전체 클릭/노출 | 104/25,657 = 0.41% | 8/1,126 = 0.71% | 클릭 수가 많다고 반응률도 높은 것은 아님 |
| 네이버 검색 안의 클릭/노출 | 62/7,797 = 0.80% | 6/660 = 0.91% | 같은 매체군으로 좁혀도 모바일 우월성은 입증되지 않음 |

- **확인할 문제:** 모바일의 작은 화면에서 사과즙·실물 포장·120ml 50포를 식별할 수 있는가? 접점 규모가 큰 화면부터 점검할 이유가 있습니다.
- **다른 설명:** 모바일 비중은 광고 공급량·검색량·매체 구성에 따른 결과일 수 있습니다. 클릭률 차이 역시 위치·검색어·경쟁이 달라 생길 수 있습니다. PC 8클릭으로 효율 승자를 정하지 않습니다.
- **실행 결정 E01:** 모바일 검색 화면의 제품 사진·제목 읽힘과 클릭 후 첫 화면을 점검합니다. 모바일 입찰 증액·PC 중단으로 연결하지 않습니다.
- **판정 방법:** 작은 화면에서 제품 식별이 어려운 부분을 찾아 사진 한 요소만 비교합니다. 같은 기간·검색어·매체 구성을 기록하고 클릭/노출을 봅니다. 상품 첫 화면 변경은 별도로 방문 이후 순주문을 확인합니다. 매출 효과는 아직 미측정입니다.

### 2. “산지명이 있는 검색”에서 한 단계 더: 어떤 이름을 알고 찾았는가?

![검색어별 노출을 분모로 한 클릭 반응 비교](juice_figures/16_query_specificity_2026-10-28.png)

**그림 16 해석:** `청송사과즙` 8,015노출·44클릭(0.55%)에 비해 `청송얼음골사과즙`은 177노출·21클릭(11.86%)입니다. 노출이 작은 검색어에서 클릭 21회가 발생한 것이 더 깊이 볼 관찰입니다. 제목에 단어를 추가하면 이 비율이 재현된다는 뜻은 아닙니다.

- **확인할 문제:** `청송사과`, `얼음골`, 포장의 `사과하나`, 판매자 `삼형제농원`이 동일한 제품으로 이해되도록 연결돼 있는가?
- **다른 설명:** 자세한 이름을 검색한 사람은 이미 제품을 알거나 재구매하려는 사람일 수 있습니다. 광고 위치·다른 업체와의 경쟁도 다를 수 있습니다. 현재 자료에는 신규/재구매 구분이 없습니다.
- **작지만 필요한 사례:** `얼음골사과하나즙`은 1노출·1클릭·귀속전환 1이벤트입니다. 포장명 연결을 확인할 단서로만 사용합니다. 1건을 우수 키워드나 구매율 100%의 증거로 쓰지 않습니다. 위 비교 그림의 3검색어는 전환이 모두 0입니다.
- **실행 결정 E02:** 새 키워드를 무조건 더 늘리기 전에 온라인 제목·제품 사진·첫 화면의 제품명 연결을 점검합니다. 현재 제목 `청송사과즙 얼음골 사과하나 120ml 50포`는 이미 적용됐으므로 다시 바꾸지 않고 변경 후 실적부터 회수합니다.
- **판정 방법:** 바뀐 제목 아래 관련 검색어의 실제 노출·클릭을 확인합니다. 주말 스토어 연결 후 같은 사과즙의 순주문·신규/재구매와 연결합니다. 재구매 검색에서만 반응이 좋으면 신규 고객용 설명은 별도로 준비합니다. 현재는 신규 수요 확대 효과를 확정할 수 없습니다.

### 3. “출고 안내 확인”이라는 한 줄: 고객이 읽는 날짜가 서로 맞는가?

- **관찰:** 10/27 저장 상품 정보에는 제조일 `2025-01-01`, 유효일 `2026-12-31`, 소비기한 `2025-12-31`이 함께 있습니다. 당시 출고 마감은 구조화 안내 11시와 상세 설명 12시로 다릅니다. 10/28 판매자 정보 재검토에서도 충돌이 기록됐습니다.
- **확인할 문제:** 광고를 눌러도 어떤 제품을 언제 받을 수 있는지 확신하기 어려운 표시인가? 날짜 불일치는 확인된 관찰이지만 실제로 판매를 막았는지는 미측정입니다.
- **다른 설명:** 옛 상품 필드·옛 상세사진이 남았거나 실제 재고와 화면 정보가 다를 수 있습니다. 실제 제품이 소비기한을 지났다고 확정하지 않습니다. 이번 분석은 현재 화면을 새로 조회한 결과가 아닙니다.
- **실행 결정 E03:** 실제 출고 로트의 라벨·출고 가능일과 각 화면의 필드를 판매자와 대조합니다. 오류이면 정확한 값으로 통일한 뒤 광고·디자인 시험을 진행합니다. 틀린 정보를 비교군으로 유지하지 않습니다.
- **판정 방법:** 동일 로트의 라벨·상세·상품정보·배송 안내가 일치하는지 먼저 확인합니다. 이후 관련 문의·취소 사유와 순주문을 관찰합니다. 정정 뒤 주문 증가만으로 날짜 정정의 인과효과를 주장하지 않습니다.

### 4. 발견했어도 주력 과제로 삼지 않은 관찰

| 작은 관찰 | 더 확인한 비교 | 이번 결정 |
|---|---|---|
| `형제농원` 3,896노출·1클릭 | 클릭률0.026%, 비용55원. 클릭 없는 검색어가 빠진 23개 표 전체의 대표값은 아님 | 이름·검색 의도 점검의 단서. 큰 광고비 낭비 원인으로 부풀리지 않음 |
| 다른 산지/동명 검색어 3개 | 총3클릭·220원, 검색어 광고비7,678원의2.9% | 보조 정리 후보. 이것만 제외하면 판매가 늘어난다고 주장하지 않음 |
| 100포 월간검색450회와 1인최대1개 제한 | 현재 상품은50포, 제한이 추가박스 구매를 막는지·재고 보호 목적인지 미확인 | 묶음 제안 전 수량 제한·공급·택배·손익 확인. 묶음 매출 예측 금지 |

### 5. 보고서에 남길 것은 숫자 목록이 아니라 이 결정 순서입니다

1. **E03 상품 정보 대조:** 실제 라벨·출고일 확인 → 충돌 수정안 확정. 실제 상품 변경은 승인 범위·접근 권한 안에서 별도 수행합니다.
2. **E02 현재 제목 관찰:** 이름을 알고 찾는 유입과 넓은 검색을 구분 → 이미 변경한 제목의 결과 회수. 제목을 다시 바꿔 기존 관찰을 섞지 않습니다.
3. **E01 모바일 화면 점검:** 제품 식별이 어려운 지점을 구체적으로 찾기 → 사진 한 요소 비교. 클릭 후 첫 화면은 별도 변경하고 방문·순주문을 대조합니다.

현재 자료로 확인된 것은 기기·검색어별 광고 반응과 저장 화면의 정보 충돌입니다. **클릭 후 이탈이 큰지, 어떤 고객이 샀는지, 무엇이 매출을 막았는지는 아직 확인되지 않았습니다.** 그래서 ‘모바일 개선이 매출을 늘린다’ 대신 어떤 증거가 있어야 그 결정을 유지하거나 바꿀지를 위에 적었습니다.

**출처·범위:** [매체51행](ads_media_2025-11-01_2026-01-31.json), [클릭 있는 검색어23개](ads_search_term_clicks_2025-11-01_2026-01-31.csv), [10/27 상품정보](juice_own_listing_2026-10-27.json), [10/28 판매자·제품 근거](juice_seller_evidence_2026-10-28.json), [현재 제목 기록](juice_title_trial_2026-10-28.json). 기간은 광고2025.11.01~2026.01.31 / 상품 관찰2026.10.27~28로 서로 다릅니다. 옛 광고 성과를 현재 페이지 결함의 결과로 연결하지 않습니다. [재계산 JSON](juice_eda_decisions_2026-10-28.json), 재현 `scripts/analyze_eda_decisions.py`.

'''
start_marker = '## 10/28 작은 관찰에서 문제와 실행을 연결한 재검토 (#73)'
previous_marker = '## 10/28 보고서의 중심: 모바일에서 제품을 알아보고 구매하도록 개선'
start = text.index(start_marker) if start_marker in text else text.index(previous_marker)
end = text.index('## 10/28 판매 성장 후보36개:', start)
text = text[:start] + section + text[end:]
text = text.replace('# 청송사과즙은 노출 확대와 함께 가격·상품 신뢰를 준비해야 합니다',
                    '# 청송사과즙의 작은 관찰을 비교해 다음 검증을 정합니다', 1)
report.write_text(text, encoding='utf-8')

# --- #75 (Claude Code): device is not one screen; split by ad surface, bound query mix, recheck dates ---
def surface(name, kind):
    if kind == '콘텐츠':
        return '네이버 콘텐츠·추천 지면'
    if name.startswith('당근'):
        return '당근마켓 검색'
    if '네이버 통합검색 네이버플러스' in name:
        return '네이버 통합검색 내 플러스스토어 영역'
    if name.startswith('네이버 통합검색'):
        return '네이버 통합검색'
    if name.startswith('네이버 쇼핑') or name.startswith('네이버플러스 스토어'):
        return '네이버 쇼핑·플러스스토어 탭'
    return '기타 외부 검색'

surf = defaultdict(lambda: dict(impressions=0, clicks=0, cost_krw=0, conversion_events=0, rank_x_imp=0.0))
for row in source['rows']:
    s = surf[(surface(row[1], row[3]), row[2])]
    add(s, row)
    s['rank_x_imp'] += number(row[4]) * float(re.sub(r'[^0-9.]', '', row[9]) or 0)
surfaces = []
for (name, device), v in surf.items():
    surfaces.append(dict(surface=name, device=device, impressions=v['impressions'], clicks=v['clicks'],
                         cost_krw=v['cost_krw'], conversion_events=v['conversion_events'],
                         ctr_pct=v['clicks'] / v['impressions'] * 100 if v['impressions'] else None,
                         avg_rank_imp_weighted=round(v['rank_x_imp'] / v['impressions'], 1) if v['impressions'] else None))
surfaces.sort(key=lambda r: (r['device'] != '모바일', -r['clicks'], -r['impressions']))
mobile_rows = [r for r in surfaces if r['device'] == '모바일']
assert sum(r['clicks'] for r in mobile_rows) == 104 and sum(r['impressions'] for r in mobile_rows) == 25657
carrot = next(r for r in mobile_rows if r['surface'] == '당근마켓 검색')
naver_int_m = next(r for r in mobile_rows if r['surface'] == '네이버 통합검색')
assert (carrot['impressions'], carrot['clicks'], carrot['cost_krw']) == (12546, 34, 2640)
assert (naver_int_m['clicks'], naver_int_m['conversion_events']) == (47, 1)

naver_search_imp = sum(d['impressions'] for (dev, ch), d in cross.items() if ch == '네이버 검색')
external_search_imp = sum(d['impressions'] for (dev, ch), d in cross.items() if ch == '외부 검색')
top3 = ['청송사과즙', '형제농원', '얼음골사과즙']
top3_imp = sum(int(queries[q]['노출']) for q in top3)
query_mix_bound = dict(
    clicked_query_impressions=query_totals['노출'], naver_search_impressions=naver_search_imp,
    external_search_impressions=external_search_imp,
    min_external_impressions_in_clicked_queries=query_totals['노출'] - naver_search_imp,
    top3_queries=top3, top3_impressions=top3_imp,
    min_external_share_of_top3_pct=(top3_imp - naver_search_imp) / top3_imp * 100,
    logic='클릭된 검색어 노출이 네이버 검색 매체 전체 노출보다 크므로 차이만큼은 반드시 외부 검색(대부분 당근) 노출이다. 검색어x매체 교차표는 없다.')
assert query_mix_bound['min_external_impressions_in_clicked_queries'] == 6826

tool = {}
for b in read('juice_keyword_cells_2026-10-28.json')['batches']:
    for r in b['rows']:
        tool.setdefault(r[1], (r[2], r[3]))

def upper(v):
    return 9 if '<' in v else number(v)

volume_check = []
for q in ['청송사과즙', '얼음골사과즙', '청송얼음골사과즙']:
    pc, mo = tool[q]
    volume_check.append(dict(query=q, ad_impressions_3m=int(queries[q]['노출']),
                             ad_impressions_per_month=round(int(queries[q]['노출']) / 3),
                             keyword_tool_monthly_pc=pc, keyword_tool_monthly_mobile=mo,
                             keyword_tool_monthly_upper=upper(pc) + upper(mo),
                             period_note='키워드도구 값은 2026-10 조회 시점의 최근 월간값, 광고는 2025-11~2026-01'))
name_collision = dict(
    clicked_query_other_region=[q for q in queries if '밀양' in q or '청도' in q],
    keyword_tool_other_brand=[k for k in tool if '사과하나' in k and k != '사과하나'],
    note='얼음골은 밀양 얼음골사과와 겹치고, 사과하나는 다른 업체명과 결합된 검색어가 있다. 실제 의도 비중은 미확인.')

monthly = read('ads_history_expanded_2026-10-20.json')['monthly']
revenue_per_event = [dict(month=m['month'], conversion_events=m['conversions'], revenue_krw=m['revenue'],
                          revenue_per_event=round(m['revenue'] / m['conversions']))
                     for m in monthly if m['conversions']]
after_sep = [m for m in monthly if m['month'] >= '2026.09']
apr_may = [m for m in monthly if m['month'] in ('2026.04', '2026.05')]
p_apr_may = sum(m['conversions'] for m in apr_may) / sum(m['clicks'] for m in apr_may)
clicks_after = sum(m['clicks'] for m in after_sep)
price_signal = dict(revenue_per_event=revenue_per_event,
                    apr_may_event_rate=p_apr_may, clicks_since_2026_09=clicks_after,
                    events_since_2026_09=sum(m['conversions'] for m in after_sep),
                    prob_zero_if_apr_may_rate=(1 - p_apr_may) ** clicks_after,
                    note='전환당 귀속매출이 24,900->29,900->40,000원대로 바뀜. 옵션/가격 이력 미확인. 9~10월 무전환은 4~5월 비율이 유지돼도 나올 수 있어 가격 탓으로 판정하지 않음.')

dates = dict(manufactured=listing['manufactured'], valid=listing['valid'], expiry=listing['expiry'],
             all_year_boundary=all(v[5:] in ('01-01', '12-31') for v in [listing['manufactured'], listing['valid'], listing['expiry']]),
             shipping_display=listing['shipping_display'],
             seller_conflicts=seller['conflicts'][:2],
             related_review_friction=[t for t in seller['review_sample']['friction_themes'] if '배송' in t['theme']],
             current_screen_rechecked=False,
             reason_not_rechecked='2026-10-28 Claude Code 세션에서 smartstore.naver.com 접속이 도구 안전 제한으로 거부됨')

result['claude_75'] = dict(session='Claude-20261028-75', mobile_surfaces=surfaces,
                           mobile_click_split={r['surface']: r['clicks'] for r in mobile_rows},
                           mobile_impression_split={r['surface']: r['impressions'] for r in mobile_rows},
                           query_mix_bound=query_mix_bound, query_volume_check=volume_check,
                           name_collision=name_collision, price_signal=price_signal, listing_dates=dates,
                           verdicts={'E01': '부분 수용: 모바일 효율우위 기각은 수용. 점검 단위를 기기에서 지면(네이버 통합검색 모바일 / 당근 / 쇼핑탭)으로 변경',
                                     'E02': '부분 수용: 제목 재변경 금지와 실적 회수는 수용. 11.86% 대 0.55% 비교는 지면 혼합과 검색량 불일치 때문에 의도 차이의 근거로 약함',
                                     'E03': '수용·보강: 세 날짜가 모두 연초/연말 값이라 실제 로트보다 미갱신 기본값 가능성. 현재 화면 미재확인'})
(R / 'juice_eda_decisions_2026-10-28.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Figure 17: where the mobile clicks actually came from
order = ['네이버 통합검색', '당근마켓 검색', '네이버 쇼핑·플러스스토어 탭', '네이버 콘텐츠·추천 지면', '네이버 통합검색 내 플러스스토어 영역', '기타 외부 검색']
mrow = {r['surface']: r for r in mobile_rows}
fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6), sharey=True)
fig.subplots_adjust(left=.27, right=.97, top=.80, bottom=.24, wspace=.08)
ys = list(range(len(order)))[::-1]
for ax, key, title in [(axes[0], 'impressions', '모바일 노출 (총 25,657회)'), (axes[1], 'clicks', '모바일 클릭 (총 104회)')]:
    tot = sum(mrow[s][key] for s in order)
    for y, s in zip(ys, order):
        v = mrow[s][key]
        color = blue if s in ('네이버 통합검색', '당근마켓 검색') else gray
        ax.barh(y, v / tot * 100, color=color, height=.55)
        ax.text(v / tot * 100 + 1, y, f'{v / tot * 100:.0f}% ({v:,})', va='center', fontsize=10.5)
    ax.set_xlim(0, 70)
    ax.set_title(title, fontsize=12.5, loc='left')
    ax.spines[['left', 'right', 'top']].set_visible(False)
    ax.set_xlabel('모바일 안에서 차지하는 비중 (%)')
axes[0].set_yticks(ys, [f"{s}\n클릭률 {mrow[s]['ctr_pct']:.2f}% · 평균순위 {mrow[s]['avg_rank_imp_weighted']}" for s in order], fontsize=10)
fig.suptitle('모바일 클릭은 네이버 통합검색과 당근마켓, 서로 다른 두 화면에서 나왔습니다', x=.03, ha='left', fontsize=16, fontweight='bold')
fig.text(.03, .11, '그림 17. 광고그룹 매체 리포트, 2025.11.01~2026.01.31, 모바일 행만. 괄호 = 횟수. 진한 막대 = 클릭이 많은 두 지면.', fontsize=10.5)
fig.text(.03, .05, '귀속 전환 1건은 네이버 통합검색 모바일. 지면마다 광고 위치(평균순위)가 달라 클릭률 차이를 화면 품질 차이로 단정하지 않습니다.', fontsize=10.5)
fig.savefig(R / 'juice_figures/17_mobile_surfaces_2026-10-28.png', dpi=160)
plt.close(fig)

# Figure 18: clicked-query impressions exceed all Naver search impressions
fig, ax = plt.subplots(figsize=(11, 4.9))
fig.subplots_adjust(left=.30, right=.95, top=.78, bottom=.33)
bars = [('클릭이 있는 검색어 23개의 노출', query_totals['노출'], blue),
        ('같은 기간 네이버 검색 매체 전체 노출', naver_search_imp, gray)]
for y, (label, v, c) in zip([1, 0], bars):
    ax.barh(y, v, color=c, height=.5)
    ax.text(v + 150, y, f'{v:,}회', va='center', fontsize=11.5)
ax.set(yticks=[1, 0], yticklabels=[b[0] for b in bars], xlim=(0, 18500), xlabel='노출 수 (회)')
ax.spines[['left', 'right', 'top']].set_visible(False)
fig.suptitle('검색어별 클릭률에는 당근 등 외부 검색 노출이 최소 6,826회 섞여 있습니다', x=.03, ha='left', fontsize=16, fontweight='bold')
fig.text(.03, .10, '그림 18. 2025.11.01~2026.01.31. 위 막대가 아래 막대보다 큰 만큼(6,826회)은 네이버가 아닌 외부 검색 노출입니다.', fontsize=10.5)
fig.text(.03, .04, '검색어x매체 교차표가 없어 검색어별 비율은 모릅니다. 그래서 검색어 사이 클릭률 차이를 검색 의도 차이만으로 읽지 않습니다.', fontsize=10.5)
fig.savefig(R / 'juice_figures/18_query_surface_mix_2026-10-28.png', dpi=160)
plt.close(fig)
print('#75: surfaces, query-mix bound, volume check, price and date signals saved; figures 17/18.')

# Insert/refresh the #75 section above #73 in the analytical report.
SECTION_75 = '''## 10/28 Claude Code 재검증: 기기가 아니라 광고 지면으로 나누면 결정이 바뀝니다 (#75)

수행: Claude Code (Opus 5.5), 세션 Claude-20261028-75. 아래 #73(Codex)의 수치는 같은 원자료로 다시 계산해 모두 일치했습니다. 이번에 새로 확인한 것은 **기기(모바일/PC)라는 단위가 서로 다른 두 화면을 섞고 있었다는 점**입니다. 그래서 #73의 세 결정 중 두 개는 범위를 고치고, 하나는 근거를 보강합니다.

| #73 결정 | 판정 | 이유 |
|---|---|---|
| E01 모바일 화면 점검 | **부분 수용** | 모바일 효율 우위 기각은 맞음. 그러나 모바일 클릭의 33%는 당근마켓 검색 지면이라 ‘모바일 화면 하나’를 점검 대상으로 삼으면 틀린 화면을 고칠 수 있음 → 지면별로 나눔 |
| E02 제목 재변경 금지·실적 회수 | **부분 수용** | 제목을 다시 바꾸지 않는 판단은 유지. 다만 11.86% 대 0.55% 비교는 외부 검색 노출이 섞여 있어 ‘이름을 알고 찾는 사람’의 근거로는 약함 |
| E03 날짜·출고 정보 대조 | **수용·보강** | 세 날짜가 모두 연초·연말 값이라 실제 로트보다 갱신 안 된 기본값일 가능성이 큼. 현재 화면은 이번에도 다시 확인하지 못함 |

### 발견 1. ‘모바일 클릭’은 한 화면이 아니라 네이버 통합검색과 당근마켓 두 화면이었습니다

![모바일 노출과 클릭의 지면별 구성](juice_figures/17_mobile_surfaces_2026-10-28.png)

1. **놓치기 쉬웠던 관찰:** 모바일 노출의 49%(12,546회)는 네이버가 아니라 **당근마켓 검색**에서 나왔습니다.
2. **직접 확인한 수치:** 광고그룹 매체 리포트 51행, 2025.11.01~2026.01.31, 모바일 행만.

   | 모바일 지면 | 노출 | 클릭 | 클릭률 | 평균순위(노출가중) | 광고비 | 귀속전환 |
   |---|---:|---:|---:|---:|---:|---:|
   | 네이버 통합검색 | 4,539 | 47 | 1.04% | 3.4 | 3,432원 | 1 |
   | 당근마켓 검색 | 12,546 | 34 | 0.27% | 7.6 | 2,640원 | 0 |
   | 네이버 쇼핑·플러스스토어 탭 | 1,567 | 10 | 0.64% | 8.4 | 814원 | 0 |
   | 네이버 콘텐츠·추천 지면 | 5,146 | 6 | 0.12% | 8.1 | 616원 | 0 |
   | 네이버 통합검색 내 플러스스토어 영역 | 1,691 | 5 | 0.30% | 1.0 | 275원 | 0 |
   | 기타 외부 검색 | 168 | 2 | 1.19% | 3.8 | 187원 | 0 |
   | 합계 | 25,657 | 104 | 0.41% | | 7,964원 | 1 |

3. **추가 비교로 새로 안 점:** 같은 네이버 통합검색 안에서도 PC는 287노출·5클릭(1.74%, 평균순위 1.7), 모바일은 1.04%(평균순위 3.4)입니다. 기기 간 클릭률 차이는 광고 위치 차이와 같은 방향입니다. 지면을 섞은 기기 비교는 **노출 위치와 지면 구성의 차이를 기기 차이로 읽게 만듭니다.**
4. **가능한 설명과 구분하지 못한 설명:**
   - 당근 지면은 지역 중고·생활 검색 화면이라 사과즙 구매 의도가 약할 수 있음.
   - 당근 사용자는 농원의 당근 프로필(단골 986명, 가격표 ‘24,900원부터’ 표시)을 이미 알 수 있음. 네이버 광고를 눌러 39,900원을 보고 이탈했거나 당근에서 직접 샀을 수 있으나, 이 경로는 네이버 전환 추적에 잡히지 않아 **구분 불가**.
   - 당근의 평균순위 7.6은 노출 위치가 낮다는 뜻일 수 있어 낮은 클릭률이 화면 품질 때문인지 위치 때문인지 구분 불가.
5. **판매에 중요한 이유:** 화면을 고치거나 입찰을 바꿀 때 어느 지면을 기준으로 삼느냐에 따라 행동이 달라집니다. 유일한 귀속 전환은 네이버 통합검색 모바일에서 나왔고, 이 지면이 모바일 클릭의 45%입니다.
6. **지금 할 일 / 보류할 일:**
   - 할 일: 화면 점검 1순위를 **네이버 통합검색 모바일의 쇼핑 광고 카드**로 좁힙니다. 점검할 정보는 카드의 대표사진(파우치와 박스가 작은 썸네일에서 사과즙·50포로 보이는지), 제목 앞부분(`청송사과즙 얼음골 사과하나`가 잘리지 않고 읽히는지), 표시가격·배송 문구입니다. 클릭 후 상품 첫 화면은 용량×포수, 사과 100%, 날짜·출고 안내가 첫 화면에 있는지 봅니다. **이번 세션은 화면 검수를 하지 않았습니다.**
   - 할 일: 다음 광고 리포트부터 **매체(지면)×검색어**로 받아 네이버와 당근을 나눠 기록합니다.
   - 보류: 모바일 입찰 일괄 증액, 당근 지면 중단. 당근 지면은 3개월 2,640원으로 비용 규모가 작아 ‘절감’보다 ‘측정 분리’가 먼저입니다.
7. **결정을 바꿀 확인 결과:** 지면별 리포트에서 당근 클릭이 계속 주문 0이고 스토어 주문에도 당근 유입이 없으면 당근 지면 제외를 검토합니다. 반대로 스토어 주문에서 당근 유입 구매가 확인되면 당근 카드도 점검 대상에 넣습니다.

### 발견 2. 검색어별 클릭률 비교에는 외부 검색 노출이 최소 6,826회 섞여 있습니다

![클릭된 검색어 노출과 네이버 검색 전체 노출 비교](juice_figures/18_query_surface_mix_2026-10-28.png)

1. **놓치기 쉬웠던 관찰:** 클릭이 있는 검색어 23개의 노출 합계(15,283회)가 같은 기간 **네이버 검색 매체 전체 노출(8,457회)보다 큽니다.**
2. **직접 확인한 수치:** 검색어 리포트 23행(클릭 합계 104 = 검색 매체 클릭 104, 광고비 7,678원 = 검색 매체 광고비)과 매체 리포트 51행, 2025.11.01~2026.01.31.
3. **추가 비교로 새로 안 점:**
   - 차이 6,826회는 반드시 외부 검색(대부분 당근) 노출입니다. 노출이 큰 세 검색어(`청송사과즙`·`형제농원`·`얼음골사과즙`, 14,585회)만 봐도 최소 42%가 외부 검색입니다.
   - 키워드 도구의 월간 검색수(2026-10 조회)와 비교하면 `청송사과즙` 광고 노출은 월 2,672회로 월간 검색수 710회보다 크고, `청송얼음골사과즙`은 월 59회로 월간 검색수 상한 18회보다 큽니다. 기간이 달라 직접 비교는 못 하지만, **광고 노출 수를 네이버 검색 수로 읽으면 안 된다**는 점은 분명합니다.
   - 이름 충돌 단서: 클릭된 검색어에 `얼음골사과밀양주스`, `청도형제사과즙`이 있고, 키워드 도구에 `산지애사과하나`가 있습니다. `얼음골`은 밀양 얼음골사과와, `사과하나`는 다른 업체명과 겹칠 수 있습니다.
4. **가능한 설명과 구분하지 못한 설명:** `청송사과즙`의 낮은 클릭률은 (가) 당근 노출 비중이 커서, (나) 넓은 검색이라 경쟁 상품이 많아서, (다) 광고 위치가 낮아서일 수 있습니다. `청송얼음골사과즙`의 높은 클릭률은 (가) 제품을 알고 찾은 사람, (나) 판매자·관계자의 확인 검색, (다) 네이버 지면 위주 노출일 수 있습니다. 검색어×매체 교차표와 고유 사용자 수가 없어 **어느 것도 구분할 수 없습니다.**
5. **판매에 중요한 이유:** 이 비교를 근거로 ‘구체적인 이름 키워드를 늘리자’거나 ‘청송사과즙은 효율이 나쁘다’고 판단하면, 지면 구성 차이를 키워드 가치로 잘못 옮기게 됩니다. `청송사과즙`은 월간 검색수가 가장 큰 사과즙 산지 검색어입니다.
6. **지금 할 일 / 보류할 일:**
   - 할 일: 현재 제목 `청송사과즙 얼음골 사과하나 120ml 50포`는 유지하고(#73 E02 수용) 변경 후 실적을 지면×검색어로 회수합니다.
   - 할 일: `사과하나`가 친구 제품 포장의 고유 표기인지, 다른 업체의 상표·상품명인지 판매자에게 확인합니다. 다른 업체 상표라면 이는 시험이 아니라 **정정 대상**입니다(스킬 `smartstore-listing-seo`의 ‘타 브랜드명 금지’ 항목).
   - 보류: 구체 이름 키워드 확대, `청송사과즙` 비중 축소, `얼음골` 계열 제외.
7. **결정을 바꿀 확인 결과:** 네이버 지면만 놓고도 `청송얼음골사과즙`의 클릭률이 크게 높으면, 제품 인지 고객의 검색이 있다는 해석이 강해지고 포장명 연결(사진·상세에서 청송·얼음골·사과하나를 한 제품으로 보여주기)에 더 투자합니다. 차이가 사라지면 이 비교는 보고서에서 내립니다.

### 발견 3. 날짜 세 개가 모두 연초·연말 값입니다: 실제 로트보다 갱신 안 된 기본값일 가능성

1. **놓치기 쉬웠던 관찰:** 10/27 저장 상품정보의 제조일 `2025-01-01`, 소비기한 `2025-12-31`, 유효일 `2026-12-31`은 모두 1월 1일 또는 12월 31일입니다.
2. **직접 확인한 수치:** `juice_own_listing_2026-10-27.json`, `juice_seller_evidence_2026-10-28.json`의 충돌 목록. 출고 마감은 구조화 안내 11시, 상세 설명 12시. 쿠팡 후기 표본에 2026-02-27 ‘장기간 배송 대기’ 지적 1건.
3. **추가 비교로 새로 안 점:** 실제 생산 로트가 정확히 연초·연말에 걸릴 가능성보다, 등록 당시 입력한 기본값이 갱신되지 않았을 가능성이 큽니다. 제조원도 네이버 필드는 `청송 삼형제농원`, 상세 라벨은 `청송사과식품`으로 다르고, 광고 카탈로그의 브랜드·제조사는 `미입력`입니다.
4. **가능한 설명과 구분하지 못한 설명:** 옛 필드 미갱신 / 옛 상세 이미지 / 실제 재고가 오래된 로트 중 무엇인지 구분할 수 없습니다. **실제 제품이 소비기한을 지났다고 판단하지 않습니다.** 이번 세션도 현재 화면 접속이 도구 제한으로 거부되어 지금도 같은 값인지 확인하지 못했습니다.
5. **판매에 중요한 이유:** 클릭 후 첫 화면에서 ‘소비기한 2025-12-31’이 보이면 구매를 망설일 수 있습니다. 다만 이 문제가 과거(2025-11~2026-01) 광고 성과의 원인이었다고는 연결하지 않습니다. 관찰 시점이 다릅니다.
6. **지금 할 일 / 보류할 일:**
   - 할 일(가장 먼저): 판매자에게 실제 출고 로트 라벨 사진과 출고 마감 시각을 받아 네이버 상품정보·상세·배송 안내를 한 값으로 맞춥니다. 제조원·판매원·브랜드 필드도 같은 기회에 실제 라벨과 맞춥니다. 오류 정정은 효과 시험이 아니므로 비교군으로 남기지 않습니다.
   - 보류: 정정 전 광고 확대·디자인 시험.
7. **결정을 바꿀 확인 결과:** 현재 화면에서 이미 고쳐져 있으면 E03은 종료하고 발견 1의 화면 점검으로 바로 넘어갑니다. 실제 재고 로트가 오래된 것이면 판매 재개 전 재고 정리가 먼저입니다.

### 결론을 바꾸지 않아 주력으로 올리지 않은 신호

| 작은 신호 | 확인한 것 | 이번 판단 |
|---|---|---|
| 전환당 귀속매출 변화 | 2025-05·06 24,900원 → 2026-01 28,900원 → 2026-02 29,900원 → 2026-04 40,000원. 3월 3건 99,800원, 5월 2건 69,900원 | 가격·옵션 이력이 바뀐 흔적. 과거 귀속매출 318,300원은 현재가 39,900원 기준이 아니므로 현재 손익 계산에 그대로 쓰지 않음 |
| 9~10월 26클릭·전환 0 | 4~5월 비율(3/54)이 그대로여도 0건이 나올 확률 약 23% | 가격 인상 탓으로 판정하지 않음 |
| `청송사과` 단독 검색 | 10/28 진단에서 사과즙 상품은 카테고리 불일치로 광고 노출 불가(기존 기록) | `청송사과`는 상품명·신원 표현으로 유지하고, 성과 측정은 `청송사과즙`으로 함 |
| `형제농원` 3,896노출·1클릭·55원 | 노출 규모는 크지만 비용은 작음. 외부 검색 노출일 가능성 | 비용 낭비가 아니라 지면 혼합의 예시로만 사용 |

### 프로젝트 SEO 스킬 기준으로 다시 본 항목

`.agents/skills/`의 세 스킬(`search-demand-capture`, `smartstore-listing-seo`, `naver-keyword-research`) 기준을 적용했습니다.

- **search-demand-capture:** 병목은 한 번에 하나, 0→1건으로 승패를 정하지 않음, 광고 귀속과 스토어 주문을 구분함. 위 세 발견 모두 이 기준을 따라 ‘지금 할 일’을 하나씩만 둡니다. 스토어 주문(주말 매니저 권한 이후)이 없어 순주문·팩 수량은 여전히 미확인입니다.
- **smartstore-listing-seo:** ‘타 브랜드명 금지’(→ `사과하나` 확인), ‘상품정보와 실제 상품 일치’(→ 날짜·제조원·출고 마감), ‘브랜드/제조사 필드’(→ 광고 카탈로그 미입력), ‘한 번에 한 요소 변경’(→ 제목 유지) 항목이 이번 결정과 직접 연결됩니다.
- **naver-keyword-research:** 키워드 도구 월간 검색수는 통합검색 기준이라 광고 노출 수와 같은 단위가 아님(발견 2). `< 10`은 구간으로 보존했습니다.
- 사과즙(가공품)에 맞춘 점검 항목을 두 스킬에 추가했습니다(용량×포수·날짜 필드·제조원·지면별 측정). 네이버 쇼핑 전용 외부 스킬은 이전 조사에서 찾지 못해 새로 내려받지 않았습니다.

### 지금 내릴 결정 순서

1. **상품 정보 정정(E03):** 로트 라벨·출고 마감·제조원을 판매자와 맞춤 → 정정.
2. **측정 단위 변경:** 광고 리포트를 매체(지면)×검색어로 받고 네이버/당근을 분리. 스토어 주문은 주말 매니저 권한 이후 광고 귀속 10건과 대조.
3. **화면 점검(E01 수정):** 네이버 통합검색 모바일 쇼핑 광고 카드 → 클릭 후 첫 화면 순서. 사진 한 요소씩 바꾸고 날짜를 기록.
4. **제목 유지(E02):** 변경 후 실적 회수. `사과하나` 상표 확인 결과에 따라 정정 여부만 결정.

새로 확인하지 않은 판매 증가·A/B 효과는 주장하지 않습니다.

### 디자인에 전달할 검증 결과

| 주장 | 사용할 그림 | 핵심 수치 | 캡션 | 쉬운 해석 | 행동 | 미확인 |
|---|---|---|---|---|---|---|
| 1. 모바일 클릭은 두 화면에서 나왔다 | `juice_figures/17_mobile_surfaces_2026-10-28.png` | 모바일 클릭 104 = 네이버 통합검색 47 + 당근 34 + 기타 23. 노출은 당근 49% | 광고그룹 매체 리포트, 2025.11.01~2026.01.31, 모바일만 | ‘휴대폰 화면’ 하나가 아니라 네이버 검색 화면과 당근 화면이 따로 있다 | 네이버 통합검색 모바일 광고 카드부터 점검. 모바일 입찰 일괄 증액 보류 | 당근에서 본 사람이 실제로 샀는지, 화면 품질 문제인지 위치 문제인지 |
| 2. 검색어 비교에 다른 화면이 섞였다 | `juice_figures/18_query_surface_mix_2026-10-28.png` (보조: `16_query_specificity_2026-10-28.png`) | 클릭된 검색어 노출 15,283 > 네이버 검색 전체 8,457 → 외부 최소 6,826 | 같은 기간. 검색어×매체 교차표 없음 | 검색어끼리 클릭률을 비교하기 전에 어느 화면에서 보였는지 나눠야 한다 | 제목 유지, 다음 리포트를 지면×검색어로 받기, `사과하나` 상표 확인 | 검색어별 네이버/당근 비율, 제품 인지 고객 여부 |
| 3. 날짜 정보부터 맞춘다 | 그림 없음. 표 1개(제조일·소비기한·유효일·출고 마감 11시/12시) | 세 날짜 모두 1/1 또는 12/31. 제조원 필드와 라벨 불일치 | 10/27 저장 화면 기준, 현재 화면 미재확인 | 고객이 읽는 날짜와 출고 안내가 서로 맞아야 한다 | 판매자 로트 라벨로 정정 후 광고·디자인 진행 | 현재 화면 상태, 실제 재고 로트 |

디자인 주의: 92.9%는 과거 광고그룹 클릭 비중이며 전체 고객의 휴대폰 사용률이 아닙니다. 판매 증가·A/B 효과는 확인되지 않았습니다. 최저가 소구를 쓰지 않습니다. 실제 사진(`juice_original_product_2026-10-28.webp`)과 보정 시안(`juice_real_ad_01~03_2026-10-27.png`)을 구분해 표시합니다.

**출처·재현:** [매체51행](ads_media_2025-11-01_2026-01-31.json), [클릭 있는 검색어23개](ads_search_term_clicks_2025-11-01_2026-01-31.csv), [키워드 도구](juice_keyword_cells_2026-10-28.json), [월별 광고](ads_history_expanded_2026-10-20.json), [10/27 상품정보](juice_own_listing_2026-10-27.json), [판매자 근거](juice_seller_evidence_2026-10-28.json). 재계산 결과는 [JSON](juice_eda_decisions_2026-10-28.json)의 `claude_75`, 재현 `py -3.12 scripts/analyze_eda_decisions.py`.

'''
marker_75 = '## 10/28 Claude Code 재검증: 기기가 아니라 광고 지면으로 나누면 결정이 바뀝니다 (#75)'
marker_73 = '## 10/28 작은 관찰에서 문제와 실행을 연결한 재검토 (#73)'
text = report.read_text(encoding='utf-8')
if marker_75 in text:
    a = text.index(marker_75)
    b = text.index(marker_73)
    text = text[:a] + SECTION_75 + text[b:]
else:
    b = text.index(marker_73)
    text = text[:b] + SECTION_75 + text[b:]
text = text.replace('# 청송사과즙의 작은 관찰을 비교해 다음 검증을 정합니다',
                    '# 청송사과즙: 작은 관찰을 지면과 분모로 다시 나눠 다음 검증을 정합니다', 1)
report.write_text(text, encoding='utf-8')
print('#75 section written above #73.')
