"""Review query intent, visible ad patterns and account diagnostics without inferring market CTR."""
from pathlib import Path
import sys, json, csv, re, base64, html
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'result'; F=R/'juice_figures'
sys.path.insert(0,str(ROOT/'.venv-report'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'Malgun Gothic','axes.unicode_minus':False,'font.size':11,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False})
def read(name): return json.loads((R/name).read_text(encoding='utf-8-sig'))
def savefig(name):
    plt.tight_layout(pad=2); plt.savefig(F/name,dpi=160,bbox_inches='tight'); plt.close()
def picture(name):
    data=base64.b64encode((F/name).read_bytes()).decode()
    return f'<img style="width:100%" alt="{name}" src="data:image/png;base64,{data}">'
def bounds(v):
    return (0,9) if v.strip()=='< 10' else (int(v.replace(',','')),)*2

raw=read('juice_keyword_cells_2026-10-28.json')
unique={}; conflicts=[]
for bi,b in enumerate(raw['batches']):
    for row in b['rows']:
        assert len(row)==10
        k=row[1].split('\n')[0].strip()
        if k in unique and unique[k]['cells'][2:4]!=row[2:4]: conflicts.append(k)
        lo1,hi1=bounds(row[2]); lo2,hi2=bounds(row[3])
        unique[k]={'keyword':k,'pc':row[2],'mobile':row[3],'monthly_lower':lo1+lo2,'monthly_upper':hi1+hi2,'competition_powerlink':row[8],'cells':row,'last_batch':bi+1}
core={'청송사과즙','사과즙','사과즙50포','사과즙120ML','얼음골사과즙'}
identity={'청송얼음골사과즙','사과하나'}
def classify(k):
    if k in core: return 'P1 구매 의도 핵심','사과즙·현재50포/120ml 적합; 실제 매칭·순판매량 검증'
    if k in identity: return 'P2 포장명 연결','실물 포장명과 연결; 인지도나 판매 효과 미입증'
    if k in {'청송사과','사과주스'}: return '현재 카테고리 진단 불가','10/28 단일조건에서 카테고리 연관성 부족. 상품에 맞지 않게 카테고리 변경하지 않음'
    if '사과' not in k: return '주력 대상 아님','연관어 도구의 확장 결과. 우리상품과 적합성 미확인'
    if any(x in k for x in ['효능','부작용','만들기','당뇨','다이어트','살찌','칼로리']): return '정보형 / 콘텐츠 검토','상품명·유료 구매형 핵심에서 제외. 효능 주장으로 전용하지 않음'
    if any(x in k.upper() for x in ['NFC','유기농','저온','무설탕','무첨가','착즙','생사과즙']): return '제품 증빙 선행','공정·인증·표시 근거 확보 전 광고 주장에 사용하지 않음'
    if any(x in k.upper() for x in ['100포','30포','20포','10포','5KG','10KG','홍로','부사','문경','밀양']): return '다른 구성·생과·산지 검토','현재50포 사과즙에 해당하는지 확인 전 활용 보류'
    return '사과 관련 추가 검토','타브랜드/생과/상황어 혼재. 구매 의도와 제품 사실 수동 검토 필요'
for k,v in unique.items(): v['group'],v['use_condition']=classify(k)
assert len(unique)==364, 'Recheck source row completeness if collection changes'
fields=['keyword','group','pc','mobile','monthly_lower','monthly_upper','competition_powerlink','use_condition']
with (R/'juice_keyword_priority_2026-10-28.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(sorted(unique.values(),key=lambda x:(x['group'],-x['monthly_upper'],x['keyword'])))

serp=read('juice_market_serp_2026-10-27.json'); plus=read('juice_plus_serp_2026-10-27.json')
cards=[x for s in serp['samples'] for x in s['cards']]
ads=[x for x in cards if x['ad']]
features={'무료배송':r'배송비\s*무료','오늘출발':r'오늘출발','원료·가공 표현':r'NFC|착즙|국내산|국산|원산지|당일도정','교환·반품 혜택':r'무료교환반품','구성·수량 표현':r'\d+\s*(?:포|봉|팩|개입|kg|KG)'}
feature_counts={k:sum(bool(re.search(p,x['text'])) for x in ads) for k,p in features.items()}
diag=read('juice_diagnostics_2026-10-28.json')
for q in diag['queries']:
    t=q.get('result','') or ''
    q['classification']='카테고리 연관성 부족' if '카테고리 아님' in t else ('노출요건 충족' if '모두 갖추' in t else '매칭힌트 확인 요청 / 판정 유보')
trial=read('juice_title_trial_2026-10-28.json')
summary={'date':'2026-10-28','keyword_rows':sum(len(x['rows']) for x in raw['batches']),'keyword_unique':len(unique),'keyword_apple_related':sum('사과' in k for k in unique),'conflicting_monthly_rows':sorted(set(conflicts)),'keyword_groups':dict(Counter(x['group'] for x in unique.values())),'price_comparison_scope':'10/27 PC카드 표시. 새광고3개는최종옵션/결제미검증. 과거8개상세검증표본과구분.','serp_queries':len(serp['samples']),'serp_cards':len(cards),'serp_ad_cards':len(ads),'plus_cards_including_duplicates':len(plus['cards']),'visible_features_in_ad_cards':feature_counts,'diagnostics':diag['queries'],'trial':trial,'limitations':['시장전체노출률·경쟁사CTR미확보','카드반복·개인화·지연로딩·서로다른표본수','파워링크통계는쇼핑광고기대CTR아님','주문/환불/원가미확보','단일조건 진단은노출보장/고정순위가아님']}
(R/'juice_market_reviewed_2026-10-28.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')

selected=['사과즙','사과주스','사과쥬스','청송사과즙','생사과즙','얼음골사과즙','사과즙50포','사과즙100포','사과즙추천','사과즙120ML']
fig,ax=plt.subplots(figsize=(10,6))
ax.barh(selected,[unique[k]['monthly_upper'] for k in selected],color=['#ba5445' if k in ['사과주스'] else '#427658' for k in selected]);ax.invert_yaxis();ax.set_xlabel('월간 PC+모바일 검색수 · 통합검색, 쇼핑 주문 수 아님')
for i,k in enumerate(selected):ax.text(unique[k]['monthly_upper']+60,i,f"{unique[k]['monthly_upper']:,}",va='center',fontsize=10)
ax.set_xlim(0,10500);ax.set_title('검색량이 커도 현재 광고가 노출 가능한 것은 아닙니다\n빨강: 사과주스는 현재 카테고리 진단에서 노출 불가 · 10/28')
savefig('12_keyword_intent_2026-10-28.png')
fig,ax=plt.subplots(figsize=(10,5))
ax.barh(list(feature_counts),list(feature_counts.values()),color='#427658');ax.invert_yaxis();ax.set_xlim(0,len(ads)+3)
for i,n in enumerate(feature_counts.values()):ax.text(n+.3,i,str(n),va='center')
ax.set_xlabel(f'관찰된 광고 카드 {len(ads)}개 중 표현·표시가 확인된 카드 수 (중복 집계)')
ax.set_title('식품 광고는 원료·공정·구성·배송 조건을 함께 보여줍니다\n12검색의 PC 편의표본 · 성공광고 비율이나 CTR이 아님')
savefig('13_food_ad_patterns_2026-10-28.png')
fig,ax=plt.subplots(figsize=(10,4.8))
labels=['사과잡스 광고 카드','시골냉장고 광고 카드','기존 상세검증8개 중앙값','우리 배송포함 제안(미적용)','우리 기존 표시가격']
prices=[24900,27900,30000,29900,39900]
ax.barh(labels,prices,color=['#859b86','#859b86','#aab3aa','#d0a049','#b34b3d']);ax.invert_yaxis();ax.set_xlim(0,47000)
for i,n in enumerate(prices):ax.text(n+300,i,f'{n:,}원',va='center')
ax.set_title('29,900원은 검토 가능한 가격대이지 최저가 우위는 아닙니다\n120ml×50포 표시 기준 · 새 경쟁광고는 카드 조건만 관찰')
ax.set_xlabel('기본 배송비 포함 표시가격 / 제안가 · 조건부 쿠폰 제외')
savefig('14_expanded_price_2026-10-28.png')

links={
'노출 순위':'https://ads.naver.com/help/faq/253',
'노출 안 될 때':'https://ads.naver.com/help/faq/1487',
'매칭과 제외':'https://ads.naver.com/help/faq/1433',
'ADVoost 개요':'https://ads.naver.com/help/faq/1361',
'상품 연동':'https://ads.naver.com/help/faq/1372',
'스토어 광고와 차이':'https://ads.naver.com/help/faq/951',
'외부 부스트업':'https://ads.naver.com/help/faq/1499',
'모바일 지면 확대':'https://ads.naver.com/notice/34090',
'상품명 기준':'https://ads.naver.com/adguide/1014',
'이미지 기준':'https://ads.naver.com/adguide/1018',
'식품 연구':'https://www.navercorp.com/api/article/download/7891e840-366c-4922-9b37-2f8a29903b93'}
table=''.join(f'<tr><td>{html.escape(q["keyword"])}</td><td>{q["classification"]}</td></tr>' for q in diag['queries'])
ktop=['청송사과즙','사과즙','얼음골사과즙','사과즙50포','사과즙120ML','사과하나','청송얼음골사과즙','사과주스','사과쥬스','생사과즙','착즙사과즙','사과즙추천','사과즙선물','사과즙효능','사과즙30포','사과즙100포']
ktable=''.join(f'<tr><td>{k}</td><td>{unique[k]["pc"]} / {unique[k]["mobile"]}</td><td>{unique[k]["group"]}</td></tr>' for k in ktop)
source_links=' · '.join(f'<a href="{v}">{k}</a>' for k,v in links.items())
block=f'''<section><div class="eyebrow">2026.10.28 최신 조사 · 광고 전체 → 식품 → 사과즙 → 실제 시험</div>
<h2>노출을 늘릴 시장과, 버려야 할 검색 의도를 구분했습니다</h2>
<div class="cards"><div class="card">키워드 수집<b>{summary['keyword_rows']}행 → {len(unique)}개</b><small>중복제거. 사과 포함 {summary['keyword_apple_related']}개도 모두 광고 후보는 아님.</small></div><div class="card">공개 검색 관찰<b>12검색 · 119카드</b><small>가격비교72 + 플러스47. 반복·개인화 포함.</small></div><div class="card">우리 소재 실제 진단<b>{len(diag['queries'])}검색어</b><small>광고주센터 도구. 예상 순위 숫자는 미제공.</small></div></div>
<div class="callout"><b>실제 발견:</b> 청송사과(생과 의도)·사과주스(다른 음료 카테고리)는 현재 소재의 카테고리 연관성이 부족해 노출 불가로 진단됐습니다. 필수 표현 청송사과는 유지하되 <b>청송사과즙</b>으로 구매 의도를 연결해야 합니다. 카테고리를 억지로 바꿔 양쪽 시장을 모두 잡는 안은 제안하지 않습니다.</div>
<h3>1. 네이버 쇼핑에서 노출이 결정되는 구조</h3>
<table><tr><th>광고/영역</th><th>무엇으로 노출되는가</th><th>우리의 적용 순서</th></tr>
<tr><td>쇼핑검색 쇼핑몰상품형</td><td>상품정보 자동 매칭 + 품질지수·입찰. 검색·추천 지면을 구분.</td><td>현재 운영. 카테고리/실제검색어/제목/제품사진을 검증.</td></tr>
<tr><td>ADVoost 쇼핑</td><td>상품 피드와 구매전환 신호를 활용한 자동 지면·입찰 최적화. 광고 제목/이미지는 피드 기반.</td><td>식품 확장 시험 후보. 출고·전환추적·허용광고비 확인 뒤 한 캠페인씩.</td></tr>
<tr><td>스마트스토어 광고</td><td>ADVoost와 같은 기술, 판매자센터의 간소화된 운영 방식.</td><td>ADVoost와 노출 우선순위가 다르지 않으므로 중복 시작할 이유 없음.</td></tr>
<tr><td>파워링크</td><td>선택 키워드에 텍스트·랜딩 메시지를 맞추는 검색 광고.</td><td>키워드 직접 운영이 필요할 때 별도 검토. 쇼핑 상품형의 키워드 목록과 혼동 금지.</td></tr>
<tr><td>성과형 디스플레이·카탈로그</td><td>발견/관심/재방문을 위한 이미지·상품 카탈로그와 타깃.</td><td>제품정보·판매 측정이 준비된 뒤 신규유입과 재방문 효과를 나눠 시험.</td></tr>
<tr><td>브랜드검색·쇼핑브랜드형·신제품검색</td><td>브랜드 계약/비즈채널/자격 등 각 상품의 조건 필요.</td><td>등록 가능성을 확인하기 전 일반 사과즙 광고처럼 제안하지 않음. 현재 확장 최우선 아님.</td></tr>
<tr><td>부스트업·보장형·라이브/프로모션 연계</td><td>외부 노출 또는 기간/지면/행사 조건. 단순 키워드 추가와 다른 수단.</td><td>부스트업은 네이버 밖의 매체이므로 요청 범위와 구분. 라이브는 별도 판매 콘텐츠/재고 운영 준비 필요.</td></tr></table>
<p>공식 기준은 품질·관련성과 입찰을 함께 봅니다. “돈을 많이 쓰는 광고”나 “예쁜 광고”가 무조건 먼저 나가는 것은 아닙니다. 가격비교의 랭킹순, 플러스스토어의 개인화 추천순, 통합검색 쇼핑 블록은 서로 같은 고정 순위가 아닙니다.</p>
<p class="note">쇼핑 상품형에서 키워드를 직접 추가할 수 없습니다. 키워드 연구는 상품정보·관련 검색어의 적합성과 제외 여부를 결정하는 입력입니다. 별도 광고 제목만 바꾸어 매칭 범위가 반드시 늘어난다고 주장하지 않습니다. 10/12 모바일 트렌드Pick 지면 확대도 모든 상품의 노출을 보장하지 않습니다.</p>
<h3>2. 식품 광고에서 가져올 방향</h3>
<p>네이버의2025 D광고리포트는 패션·식품 판매자를104주 자료와 패널 회귀로 분석하고, 식품에서 ADVoost 단독 또는 쇼핑검색 조합의 상대적 성과를 보고합니다. 이는 확장 후보를 고르는 참고이며, 우리상품의 예상 매출 증가율이나 무작위 실험 결과가 아닙니다. 사업 규모·예산·운영 역량 차이가 남으므로 지금 여러 광고를 동시에 켜는 근거로 사용하지 않습니다. <a href="{links['식품 연구']}">원문 p8·p16</a></p>
{picture('13_food_ad_patterns_2026-10-28.png')}
<p>실제 쌀 광고는 수확연도·품종·도정/배송, 견과는 원물 구성·봉수·선물 제안, 과일즙은 원료·공정·포수·배송을 보여줬습니다. <b>시각적 원칙은 제품별 구매 불안을 실제 정보로 해소하는 것</b>입니다. 상위에 보였다는 이유만으로 해당 표현이 클릭을 높였다고 확정하지 않습니다. 경쟁사의 NFC·HACCP·무설탕·아이 안전 주장은 우리 증빙 없이 가져오지 않습니다.</p>
<h3>3. 사과와 사과즙을 같은 키워드 시장으로 다루면 안 됩니다</h3>
{picture('12_keyword_intent_2026-10-28.png')}
<table><tr><th>검색어</th><th>PC / 모바일 월간 검색수</th><th>현재 분류</th></tr>{ktable}</table>
<p class="note">10/28 키워드도구3배치 결과. 364개 중복제거·최근 배치값 우선. &lt;10은0–9범위를 유지하며 합산검색량을 전체시장 규모로 쓰지 않습니다. 도구의 경쟁도·클릭률·노출광고수는 파워링크 통계이지 쇼핑광고의 성과 목표가 아닙니다. 100포/30포는 현재50포 상품명에 억지로 넣지 않습니다.</p>
<h3>4. 광고주센터에서 실제로 실행한 진단</h3>
<table><tr><th>검색어</th><th>판정</th></tr>{table}</table>
<p class="note">연령·성별 알 수 없음,10/28 단일시점·등록소재 조건. 초기2개는 통합검색모바일 기본영역, 이후 쇼핑검색모바일을 선택했습니다. 청송얼음골사과즙은 매칭힌트 확인 요청으로, 무조건 노출 불가라고 단정하지 않습니다. 숫자 순위를 제공받지 못했으므로 상위노출율을 계산하지 않았습니다.</p>
<h3>5. 경쟁 광고를 포함하니 가격 판단도 달라졌습니다</h3>
{picture('14_expanded_price_2026-10-28.png')}
<p>기존8개 상세검증 표본의 중앙값30,000원은 보존합니다. 새 관찰에서는 사과잡스24,900원·시골냉장고27,900원 배송포함 광고 카드도 보였습니다. <b>우리29,900원 배송포함 제안은 가격대 진입이지 최저가 차별점은 아닙니다.</b> 제품/제조 품질은 동등 비교가 아니며 새 광고 카드의 옵션·결제 조건은 추가 검증 대상입니다. 상품가24,900원 하한을 낮추는 쿠폰을 제안하지 않습니다.</p>
<h3>6. 기존 B안보다 차이를 명확히 한 실제 제목 시험</h3>
<table><tr><th>이전 제목</th><td>{trial['before_title']}</td></tr><tr><th>시험 제목</th><td>{trial.get('after_title',trial['candidate_title'])}</td></tr><tr><th>가설</th><td>청송사과즙을 찾는 사람에게 실제 포장의 얼음골·사과하나를 연결하면 상품 정체성을 더 쉽게 이해할 수 있다.</td></tr><tr><th>등록 상태</th><td>{'저장 완료 · 운영 가능 확인' if trial['status']=='saved_operating_ui' else html.escape(trial['status'])} · 제목24자, 기존25자 한도 이내. 실제 효과 미확인.</td></tr><tr><th>변경 전 기준선</th><td>10/21–27 전체 소재623노출·1클릭·110원(VAT포함)·전환0. 확장문구 통계와 분모가 다름.</td></tr></table>
<p>제목 변경 직후 청송얼음골사과즙을 다시 진단했으나 매칭힌트 확인 요청이 그대로 나왔습니다. 제목 변경만으로 이 검색어의 매칭 개선이 입증되지는 않았습니다. 등록 상태와 실제 검색 노출·클릭 효과를 구분합니다.</p>
<p>J-COPY-01의50포→120ml 비교는 의미가 약한 운영 확인으로 정리합니다. J-TITLE-02는 제목의 정보 우선순위를 바꾼 <b>순차 관찰형 시험</b>이며 무작위 A/B가 아닙니다. 기존 확장문구는 유지하므로 이전 문구 시험의 독립적인 효과 판정은 종료합니다. 승인/교체일을 제외하고 첫 완전 노출일 이후 완료3일을 먼저 점검하되 적은 표본으로 승자를 선언하지 않습니다.</p>
<p>소재는 동일1개로 유지합니다. 가격39,900원·입찰100원(VAT별도)·기존일예산10,000원·사진·카테고리를 바꾸지 않았습니다. ADVoost 추가 등록 체크를 해제했고 신규 캠페인/부스트업은 만들지 않았습니다. 광고 상세의 브랜드/제조사 항목 미입력도 확인했으며 스토어 연결 후 실제 제조사/브랜드 근거에 따라 보완할 항목입니다.</p>
<h3>7. 가능한 시험을 모두 동시에 집행하지 않는 이유와 준비한 순서</h3>
<table><tr><th>시험</th><th>현재 상태 / 실행 조건</th><th>판단 지표</th></tr><tr><td>키워드·카테고리 진단</td><td>6검색어 실행완료. 반복 노출률이나 광고효과 시험은 아님.</td><td>적합성 판정·불가 사유</td></tr><tr><td>포장명 연결 제목</td><td>저장·운영 가능 확인. 첫 실제 노출과 후속 효과 확인 필요.</td><td>같은검색어·매체의 노출/CTR·CPC와순주문</td></tr><tr><td>제품 단품 vs 박스+파우치 사진</td><td>실사진 준비됨. 현재제목시험과 분리, 이미지기준 검수 후 한 요소만 교체.</td><td>모바일 상품 식별·CTR·클릭 후 순주문</td></tr><tr><td>가격/배송 제안</td><td>29,900배송포함 대24,900+실배송비. 사용자 가격보류 유지.</td><td>총결제금액·순판매포수·광고후공헌이익</td></tr><tr><td>입찰·매체</td><td>최소노출/경쟁입찰 진단과 원가·총손실한도확보 후. 현재증액안함.</td><td>추가노출의CPC·순주문·허용CPA</td></tr><tr><td>ADVoost 확대</td><td>출고·전환추적·상품피드/예산 준비 후 독립 시험. 현재미생성.</td><td>중복귀속제거한총순판매·매출대비공헌이익</td></tr></table>
<div class="callout"><b>이제 필요한 의사결정:</b> 구매형핵심 청송사과즙·사과즙·50포/120ml부터 노출→클릭을 확인합니다. 생과 청송사과·주스음료 수요를 억지로 섞지 않습니다. 스토어 연결 후 순주문·유입·원가를 붙여야 광고를 확대할 수익성 근거가 생깁니다. 준비 없는 캠페인 다각화로 데이터와 예산을 흩트리지 않습니다.</div>
<h3>노출률·클릭률에서 아는 것과 모르는 것</h3>
<p>우리 광고의 노출수·클릭률은 계정 자료로 확인할 수 있습니다. 경쟁사의 전체 노출수·클릭수·노출점유율은 공개 카드로 알 수 없습니다. 광고 카드 몇 개가 보였는지나 한 번의 진단으로 전체 시장 노출률을 만들지 않습니다. 지면별 전체 광고 효과의 단일 순위 역시 이번 자료로 확정하지 않습니다.</p>
<p class="note">공식자료 확인 10/27–28: {source_links}</p></section>'''
(ROOT/'scripts/shopping_market_section.html').write_text(block,encoding='utf-8')
print(json.dumps({'rows':summary['keyword_rows'],'unique':len(unique),'apple_related':summary['keyword_apple_related'],'serp_ads':len(ads),'feature_counts':feature_counts,'diagnostics':[(q['keyword'],q['classification']) for q in diag['queries']]},ensure_ascii=False))
