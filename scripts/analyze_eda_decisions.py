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
