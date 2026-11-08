"""Reconcile saved, non-personal UI aggregates. py -3.12 -X utf8 scripts/analyze_juice_followup_2026-11-08.py"""
from pathlib import Path
from datetime import date, timedelta
import json
import re

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / 'result'
PRODUCT = '11659930652'
OLD = 'juice_access_data_followup_2026-11-05.json'
NEW = 'juice_access_data_followup_2026-11-08.json'


def read(name):
    return json.loads((RESULT / name).read_text(encoding='utf-8'))


def normalize_sales(window):
    cells = window.get('table_cells', [])
    names = [r for r in cells if len(r) == 4 and re.fullmatch(r'\d{4}-\d{2}-\d{2} ~ \d{4}-\d{2}-\d{2}', r[1])]
    values = [r for r in cells if len(r) == 3 and r[0].isdigit() and r[1].isdigit()]
    if names:
        assert len(names) == len(values), 'Incomplete UI table; do not silently zip partial rows'
        rows = [dict(product_id=n[3], product_name=n[2], payments=int(v[0]), refunds=int(v[1])) for n, v in zip(names, values)]
        total, products = rows[0], rows[1:]
        assert total['product_id'] == '전체'
        assert sum(p['payments'] for p in products) == total['payments']
        assert sum(p['refunds'] for p in products) == total['refunds']
        target = next((p for p in products if p['product_id'] == PRODUCT), None)
        payments, refunds = (target['payments'], target['refunds']) if target else (0, 0)
        method = '상품 ID와 결제/환불 열을 직접 대응'
    elif window.get('table_rows') and window['period'] == ['2025-10-01', '2025-11-29']:
        # This capture retained concatenated rows. Do not parse ambiguous joined digits.
        raw = window['table_rows']
        product_lines = [r for r in raw if re.search(r'\d{11}$', r)]
        assert len(product_lines) == 3 and all(PRODUCT not in r for r in product_lines)
        assert all('사과즙' not in r for r in product_lines)
        payments, refunds = 0, 0
        method = '완전한 상품 목록 3개가 전부 생과. 결합된 숫자 문자열은 미해석'
    else:
        assert any('상품결제건수 0 건' == m for m in window['metrics_display'])
        payments, refunds = 0, 0
        method = '스토어 전체 결제 0, 상품 데이터 행 없음'
    return dict(period=window['period'], product_id=PRODUCT, payments=payments, refunds=refunds,
                payment_minus_refund=payments-refunds, method=method,
                warning='상품결제건수·환불건수. 현재 확정 주문/박스 수·순매출과 동일하지 않음')


def main():
    old, new = read(OLD), read(NEW)
    windows = [normalize_sales(w) for w in old['sales_windows']]
    for prev, cur in zip(windows, windows[1:]):
        assert date.fromisoformat(prev['period'][1]) + timedelta(days=1) == date.fromisoformat(cur['period'][0])
    payments = sum(w['payments'] for w in windows)
    refunds = sum(w['refunds'] for w in windows)
    assert (payments, refunds) == (6, 2)
    visits = old['recent_juice_visits']
    assert (visits['visits'], visits['payment_count']) == (13, 0)
    a = new['ads']
    assert a['total_conversion_value_krw'] - a['purchase_complete_value_krw'] == a['other_conversion_value_krw']
    assert a['purchase_complete_events'] <= a['total_conversion_events']
    facts = dict(request_ids=[94, 103, 104], computed_on='2026-11-08', source_files=[OLD, NEW],
                 product_id=PRODUCT, sales_windows=windows,
                 sales_totals=dict(period=[windows[0]['period'][0], windows[-1]['period'][1]],
                                   payments=payments, refunds=refunds, payment_minus_refund=payments-refunds,
                                   confirmed_orders=None, boxes=None, net_revenue_krw=None),
                 recent_juice_visits=visits['visits'], recent_juice_payments=visits['payment_count'],
                 recent_store_period=visits['period'], ads=a,
                 ad_ctr_percent=round(a['clicks']/a['impressions']*100, 2),
                 validation=dict(window_boundaries='연속·중복 없음',
                                 product_and_total_rows='합계 일치', source_scope='해당 상품만 집계',
                                 causal_effect='미측정', order_ledger='2단계 인증으로 재조회 미완료'),
                 limitations=['스토어 저장 자료는 11/3까지, 광고 자료는 11/7까지. 같은 기간의 전환율로 결합 금지.',
                              '구매완료 1건은 광고 귀속 이벤트. 실제 취소/반품·증분 효과 미확인.',
                              '총 전환 2건 및 89,900원을 구매 2건/구매매출로 보고하지 않음.',
                              '이전 세션에서 주문통합검색을 열었으나 원장 행이 파일에 남지 않아 확정 주문 집계에 사용하지 않음.',
                              '2024-01-01부터의 전 기간, 기기별 최신 실적, 매체×검색어×기기 최신 교차 자료는 미확인.'])
    (RESULT/'juice_followup_summary_2026-11-08.json').write_text(json.dumps(facts, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    table = '\n'.join(f"| {w['period'][0]} ~ {w['period'][1]} | {w['payments']} | {w['refunds']} |" for w in windows)
    report = f'''# 청송사과즙 조회 재개 결과 · 2026-11-08

대상: 삼형제농원 사과즙 상품 {PRODUCT}. **실적 확인 자료이며 A/B 테스트 결과가 아니다.**

## 확인한 변화

- 광고주센터 1755169의 J-TITLE-02: **구매완료 전환 1건·39,900원**이 표시된다.
- 조회 기간 2026-10-28~2026-11-07: 노출 **594회**, 클릭 **3회**, 광고비 **166원**, 클릭률 **0.51%**.
- 총 전환은 2건·89,900원이지만 구매완료는 그중 1건이다. 나머지 50,000원은 유형 미확인 전환값이며 구매매출에서 제외한다.
- 클릭 3회뿐이므로 성과가 안정적이거나 새 문구가 판매를 늘렸다고 판정하지 않는다. 실제 주문의 취소 여부와 광고의 귀속 기간도 추가 대조가 필요하다.

## 사과즙만 분리한 과거 판매 리포트

자료: 11월 5일 저장한 스마트스토어 판매 리포트. 상품 ID로 생과를 제외했다.

| 조회 기간 | 상품결제건수(건) | 환불건수(건) |
|---|---:|---:|
{table}
| 합계 | **{payments}** | **{refunds}** |

- 기간은 연속이고 중복이 없다. 결제 6건에서 환불 2건을 빼면 4건이지만, 이를 현재 구매확정 주문 4건 또는 4박스로 바꾸어 쓰지 않는다.
- 상품결제건수·환불건수는 보고서 지표다. 환불 반영 시점과 주문 원장을 맞추기 전 순주문·정확한 판매 수량·순매출은 미확인이다.
- 생과 매출이 큰 겨울 기간의 스토어 전체 실적을 사과즙의 판매 실적으로 사용하지 않는다.

## 최근 방문과 주문을 분리해서 읽기

| 자료 | 기간 | 확인 값 | 해석 범위 |
|---|---|---|---|
| 사과즙 방문 리포트 | 10/28~11/3 | 방문 13건·결제 0건 | 해당 상품의 저장된 방문 리포트 |
| 스토어 전체 방문 리포트 | 10/28~11/3 | 방문 21건·결제 0건 | 사과즙 외 상품 포함 |
| 스토어 검색 리포트 | 10/28~11/3 | 데이터 없음 | 전체 유입·광고 클릭 0의 뜻이 아님 |
| 광고 구매완료 | 10/28~11/7 | 1건·39,900원 | 광고 귀속값, 스토어 원장 미대조 |

**기간과 집계 기준이 다르므로 1건 ÷ 방문 13건으로 전환율을 계산하지 않는다.** 검색 리포트는 9/5~11/3 및 과거 11/30~1/28로 넓혀도 데이터가 없었다. 권한 오류는 표시되지 않았다.

## 실행 전에 맞춰야 할 것

- 현재 광고 연결 상품은 **39,900원·무료배송**, 브랜드·제조사는 미입력이다. 준비한 29,900원·무료배송 및 새 상품명은 적용 완료로 보지 않는다.
- 광고 제목은 `청송사과즙 얼음골 사과하나 120ml 50포`로 유지돼 있다. 상품명 후보 `청송사과즙 얼음골 120ml 50포 삼형제농원`과 구분한다.
- 영상 2종은 1080×1920 / 1080×1080, 15초·450프레임으로 재조립·검수 완료. 생성 장면 사진에 팬·줌·자막을 넣은 무음 영상이다. 실광고에 업로드하지 않았다.
- 영상의 29,900원 자막은 시안값이다. 실제 상품 39,900원과 일치하지 않으므로 현재 그대로 게재 가능한 최종본으로 취급하지 않는다. 가격 변경 또는 영상 문구 수정은 사용자 결정 뒤 진행한다.

## 다음 순서와 남은 확인

1. 판매자 이메일 2단계 인증 완료 → 사과즙 주문 원장에서 구매확정·취소·반품·수량·금액을 대조한다. 개인정보 포함 원본 엑셀은 저장하지 않는다.
2. 광고 구매완료 1건의 실제 주문 및 취소 상태, 전환 유형·기여기간을 확인한다. 최신 매체×검색어×기기 자료를 수집한다.
3. 제조/소비기한, 실제 출고 안내, 현재 상품명·속성·구매제한을 다시 읽고, 가격과 영상 자막까지 일치하는 변경표를 만든다.
4. 적용 승인 후에만 상품·소재를 변경한다. 이번 요청에서는 설정·예산·입찰·충전·광고 활성화·권한을 바꾸지 않았다.

현재는 이메일 인증 대기다. 조회하던 브라우저 탭이 닫혀 추가 원장·교차 보고서는 미완료로 남겼다. 11/8 현재 전체 판매 실적이 0이라고 결론 내리지 않는다.

근거: [{OLD}]({OLD}), [{NEW}]({NEW}), [재계산 값](juice_followup_summary_2026-11-08.json). 재현: `py -3.12 -X utf8 scripts/analyze_juice_followup_2026-11-08.py`.
'''
    (RESULT/'juice_followup_report_2026-11-08.md').write_text(report, encoding='utf-8')
    print(json.dumps({'windows':len(windows),'payments':payments,'refunds':refunds,'ad_purchase_complete':a['purchase_complete_events'],'ctr_percent':facts['ad_ctr_percent']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
