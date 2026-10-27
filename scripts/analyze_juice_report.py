"""Reproduce the juice report from reviewed, non-personal source files."""
import sys, json, csv, re, math, calendar, statistics
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.venv-report'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

R = ROOT / 'result'
F = R / 'juice_figures'
F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'Malgun Gothic','axes.unicode_minus':False,'font.size':11,
    'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.facecolor':'white',
    'savefig.facecolor':'white','axes.titlepad':16})
BLUE, GOLD, GRAY = '#286491', '#bd7d22', '#85929e'
def num(s):
    return float(re.sub(r'[^\d.\-]', '', str(s)) or 0)
def load(name):
    return json.loads((R/name).read_text(encoding='utf-8-sig'))
def savefig(name):
    plt.tight_layout(pad=1.8); plt.savefig(F/name,dpi=160,bbox_inches='tight'); plt.close()
def aggregate(rows):
    out={k:sum(r[k] for r in rows) for k in ['impressions','clicks','cost','conversions','direct','indirect','revenue']}
    out.update(rows=len(rows),ctr=out['clicks']/out['impressions']*100 if out['impressions'] else None,
        cpc=out['cost']/out['clicks'] if out['clicks'] else None,
        event_rate=out['conversions']/out['clicks']*100 if out['clicks'] else None)
    return out
raw=load('ads_history_expanded_2026-10-20.json')
rows=[]
for r in raw['rows']:
    rows.append(dict(date=datetime.strptime(r[4],'%Y.%m.%d.').date(),impressions=num(r[5]),clicks=num(r[6]),
        cost=num(r[9]),conversions=num(r[10]),direct=num(r[11]),indirect=num(r[12]),revenue=num(r[14])))
assert len(rows)==322 and len({r['date'] for r in rows})==322
total=aggregate(rows)
assert [total[k] for k in ['impressions','clicks','cost','conversions','revenue']]==[86025,348,26664,10,318300]
assert all(r['direct']+r['indirect']==r['conversions'] for r in rows)
months=defaultdict(list)
for r in rows: months[r['date'].strftime('%Y-%m')].append(r)
monthly=[dict(month=k,**aggregate(v),calendar_days=calendar.monthrange(int(k[:4]),int(k[5:]))[1]) for k,v in sorted(months.items())]
for m in raw['monthly']:
    found=next(x for x in monthly if x['month']==m['month'].replace('.','-'))
    assert all(found[k]==m[k] for k in ['impressions','clicks','cost','conversions','revenue'])
weekdays=[dict(weekday=n,**aggregate([r for r in rows if r['date'].weekday()==i])) for i,n in enumerate(['월','화','수','목','금','토','일'])]
periods={name:aggregate([r for r in rows if lo<=str(r['date'])<=hi]) for name,lo,hi in [
    ('2025-11~12','2025-11-01','2025-12-31'),('2026-01~05','2026-01-01','2026-05-31'),
    ('2026-09~10/19','2026-09-01','2026-10-19')]}
gaps=[]
ordered=sorted(rows,key=lambda x:x['date'])
for a,b in zip(ordered,ordered[1:]):
    if (b['date']-a['date']).days>1: gaps.append({'after':str(a['date']),'before':str(b['date']),'missing_days':(b['date']-a['date']).days-1})
convrows=[{**r,'date':str(r['date'])} for r in rows if r['conversions']]
media=[]
for r in load('ads_media_2025-11-01_2026-01-31.json')['rows']:
    media.append(dict(name=r[1],device=r[2],type=r[3],impressions=num(r[4]),clicks=num(r[5]),cost=num(r[8]),
        conversions=num(r[10]),revenue=num(r[12]),direct=0,indirect=0))
assert [sum(r[k] for r in media) for k in ['impressions','clicks','cost','conversions','revenue']]==[26783,112,8481,1,28900]
season=aggregate([r for r in rows if '2025-11-01'<=str(r['date'])<='2026-01-31'])
assert all(season[k]==sum(r[k] for r in media) for k in ['impressions','clicks','cost','conversions','revenue'])
groups={}
for k,flt in [('네이버 검색',lambda r:r['type']=='검색' and '네이버' in r['name']),
              ('외부 검색',lambda r:r['type']=='검색' and '네이버' not in r['name']),
              ('콘텐츠',lambda r:r['type']=='콘텐츠')]: groups[k]=aggregate([r for r in media if flt(r)])
devices={k:aggregate([r for r in media if r['device']==k]) for k in sorted({r['device'] for r in media})}
queries=[]
with (R/'ads_search_term_clicks_2025-11-01_2026-01-31.csv').open(encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        queries.append(dict(keyword=r['검색어'],impressions=num(r['노출']),clicks=num(r['클릭']),cost=num(r['광고비(원)']),conversions=num(r['전체전환'])))
qtotal={k:sum(r[k] for r in queries) for k in ['impressions','clicks','cost','conversions']}
qtop=sorted(queries,key=lambda x:x['clicks'],reverse=True)[:3]
top3={k:sum(r[k] for r in qtop) for k in ['impressions','clicks','cost','conversions']}
zero_upper={str(n):100*(1-0.05**(1/n)) for n in [3,26,44,65,82]}
top_days={str(n):sum(x['clicks'] for x in sorted(rows,key=lambda x:x['clicks'],reverse=True)[:n])/total['clicks']*100 for n in [5,10,20]}
summary=dict(total=total,monthly=monthly,weekdays=weekdays,periods=periods,gaps=gaps,conversion_rows=convrows,
    media_groups=groups,devices=devices,queries=queries,clicked_query_totals=qtotal,top3=top3,
    zero_event_upper_95_pct=zero_upper,top_day_click_share=top_days,
    max_daily_cost=max(r['cost'] for r in rows),nonzero_click_days=sum(r['clicks']>0 for r in rows),
    scope='광고 귀속 전체전환 이벤트; 순주문/증분매출/이익 미확인. 지표행 없음은 영업중단 확정 아님.')
(R/'juice_extended_metrics_2026-10-27.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')

# Calendar timeline retains missing months as missing, rather than reported zeros.
labels=[]; y=2025; mo=5
while (y,mo)<=(2026,10):
    labels.append(f'{y}-{mo:02}');mo+=1
    if mo==13:y+=1;mo=1
by={m['month']:m for m in monthly}
fig,axes=plt.subplots(3,1,figsize=(12,10),sharex=True)
for ax,key,title,color in zip(axes,['impressions','clicks','conversions'],['노출수','클릭수','전체전환 이벤트'],[BLUE,BLUE,GOLD]):
    vals=[by[k][key] if k in by else float('nan') for k in labels]
    ax.bar(range(len(labels)),vals,color=color,width=.7);ax.set_ylabel(title);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    for i,k in enumerate(labels):
        if k not in by:ax.axvspan(i-.45,i+.45,color='#eef0f2');ax.text(i,.5,'미확인',rotation=90,ha='center',va='center',transform=ax.get_xaxis_transform(),fontsize=9)
axes[0].set_title('월별 광고 실적: 수확철 밖에도 전환 이벤트가 관측됨')
axes[-1].set_xticks(range(len(labels)),[k[2:] for k in labels],rotation=0,fontsize=9)
fig.text(.02,.005,'2025-05·07·10, 2026-05·09·10은 지표행/기간 일부. 공백을 0으로 채우지 않음. 주문수·시장 계절성으로 해석 불가.',fontsize=10)
savefig('01_monthly.png')

fig,axes=plt.subplots(1,3,figsize=(13,4.8))
names=list(groups)
for ax,key,title in zip(axes,['impressions','clicks','cost'],['노출수','클릭수','광고비 (원)']):
    vals=[groups[k][key] for k in names];ax.barh(names,vals,color=[BLUE,GRAY,GOLD]);ax.invert_yaxis();ax.set_title(title);ax.grid(axis='x',alpha=.12);ax.set_axisbelow(True);ax.set_xlim(0,max(vals)*1.22)
    for i,v in enumerate(vals):ax.text(v+max(vals)*.025,i,f'{v:,.0f}',va='center',fontsize=10)
fig.suptitle('2025-11~2026-01: 외부검색 비용 비중과 전환 표본을 따로 봐야 함',y=1.03)
savefig('02_media.png')

fig,axes=plt.subplots(1,2,figsize=(13,5.8))
qs=sorted(queries,key=lambda x:x['cost'],reverse=True)[:8]
for ax,key,title in zip(axes,['clicks','cost'],['클릭수','광고비 (원)']):
    vals=[q[key] for q in qs];ax.barh([q['keyword'] for q in qs],vals,color=BLUE);ax.invert_yaxis();ax.set_title(title);ax.set_xlim(0,max(vals)*1.20)
    for i,v in enumerate(vals):ax.text(v+max(vals)*.02,i,f'{v:,.0f}',va='center')
fig.suptitle('클릭 상위 3개 검색어에 지출이 집중됐지만 귀속전환은 0건',y=1.03)
savefig('03_queries.png')

fig,axes=plt.subplots(1,2,figsize=(12,4.8))
for ax,key,title in zip(axes,['ctr','cpc'],['지표가 있는 날의 합산 CTR (%)','평균 CPC (원)']):
    vals=[r[key] or 0 for r in weekdays];ax.bar([r['weekday'] for r in weekdays],vals,color=BLUE);ax.set_title(title);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.text(.04,.005,'시간대·순주문·요일별 노출기회가 미확인. 이 그림만으로 요일 광고를 끄거나 입찰 가중치를 정하지 않음.',fontsize=10)
savefig('04_weekdays.png')

fig,ax=plt.subplots(figsize=(11,5))
names=['0/3 클릭','0/26 클릭','0/44 클릭','0/65 클릭','0/82 클릭'];vals=[zero_upper[str(n)] for n in [3,26,44,65,82]]
ax.barh(names,vals,color=GOLD);ax.invert_yaxis();ax.set_xlabel('전체전환 이벤트율의 단측 95% 상한 (%)');ax.set_title('전환 0건도 클릭 표본에 따라 의미가 크게 다름')
for i,v in enumerate(vals):ax.text(v+.5,i,f'{v:.1f}%',va='center')
ax.set_xlim(0,72);fig.text(.03,.005,'동일·독립 전환확률의 이항 모형 가정. 구매율 추정·성과 예측이 아니며 반복클릭/귀속 지연은 별도 한계.',fontsize=10)
savefig('05_uncertainty.png')

fig,ax=plt.subplots(figsize=(11,5.2))
cvrs=[.005,.01,.02,.03,.05];margins=[3000,5000,8000,12000,16000]
grid=[[m*c for c in cvrs] for m in margins]
im=ax.imshow(grid,cmap='Blues',aspect='auto',vmin=0,vmax=800)
for i,row in enumerate(grid):
    for j,v in enumerate(row):ax.text(j,i,f'{v:,.0f}원',ha='center',va='center',color='white' if v>=600 else '#182838')
ax.set_xticks(range(5),['0.5%','1%','2%','3%','5%']);ax.set_yticks(range(5),[f'{x:,}원' for x in margins]);ax.set_xlabel('가정한 순구매 전환율');ax.set_ylabel('주문당 허용 광고비');ax.set_title('입찰 증액 전 필요한 손익 조건: 허용 CPC 시나리오')
fig.text(.03,.005,'모든 셀은 가정. 실제 원가/순주문/확보할 이익 미확인. 광고비와 마진의 VAT 기준을 맞춰 적용.',fontsize=10)
savefig('06_cpc_scenarios.png')

fig,ax=plt.subplots(figsize=(11,4.8))
prices=[24900,28500,29900,30000,30500,39900];labels2=['24,900','28,500','29,900','30,000','30,500','현재39,900']
uplift=[39900/p-1 for p in prices]
ax.bar(labels2,[100*x for x in uplift],color=[GRAY]*5+[BLUE]);ax.set_ylabel('같은 매출을 위한 주문 증가율 (%)');ax.set_title('가격을 낮추면 같은 매출에도 더 많은 주문이 필요함')
for i,v in enumerate(uplift):ax.text(i,100*v+1,f'{100*v:.1f}%',ha='center')
fig.text(.03,.005,'현재가39900원 대비 단순 매출 산술. 이익 유지에 필요한 증가량은 원가에 따라 더 큼. 권장 가격/수요 예측 아님.',fontsize=10)
savefig('07_price_tradeoff.png')

competitors=load('juice_competitors_2026-10-27.json')['products']
fig,ax=plt.subplots(figsize=(11,6))
offers=sorted([(c['seller'],c['price']) for c in competitors]+[('삼형제농원',39900)],key=lambda x:x[1])
ax.barh([v[0] for v in offers],[v[1] for v in offers],color=[BLUE if v[0]=='삼형제농원' else GRAY for v in offers]);ax.invert_yaxis();ax.set_xlim(0,46000);ax.set_xlabel('120ml × 50포 · 일반배송 포함 가격 (원)');ax.set_title(f'관찰한 {len(competitors)}개 경쟁 제안은 28,000~30,500원')
for i,(_,p) in enumerate(offers):ax.text(p+400,i,f'{p:,}원',va='center')
fig.text(.03,.005,'2026-10-27 검색·상세 편의표본. 솔스윗 옵션검증10/25. 조건부 쿠폰 제외. 품질동등/시장평균 아님.',fontsize=10)
savefig('08_competitors.png')

fig,ax=plt.subplots(figsize=(11,5))
demand=[('사과즙',1440,7170),('청송사과즙',80,620),('사과즙50포',40,400)]
for i,(k,pc,mobile) in enumerate(demand):
    ax.barh(i,pc,color=GOLD,label='PC' if i==0 else None);ax.barh(i,mobile,left=pc,color=BLUE,label='모바일' if i==0 else None);ax.text(pc+mobile+100,i,f'{pc+mobile:,}',va='center')
ax.set_yticks(range(3),[x[0] for x in demand]);ax.invert_yaxis();ax.legend();ax.set_xlim(0,10000);ax.set_xlabel('키워드도구 월간 통합검색수 (회)');ax.set_title('사과즙 구매 의도가 있는 수요를 넓게 확인할 필요가 있음')
fig.text(.03,.005,'2026-10-27조회. 쇼핑 검색량·순방문·주문수 아님. 키워드 간 검색수는 중복 가능해 합산하지 않음.',fontsize=10)
savefig('09_demand.png')
print(json.dumps({'totals':total,'periods':periods,'groups':groups,'devices':devices,'qtotal':qtotal,'top3':top3,'weekdays':weekdays},ensure_ascii=False))
