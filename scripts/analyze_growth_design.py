"""Prospective designs, not completed experiments or observed purchase effects."""
import sys, math, json
from pathlib import Path
from statistics import NormalDist
R=Path(__file__).resolve().parents[1]/'result'
sys.path.insert(0,str(R.parent/'.venv-report'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'Malgun Gothic','axes.unicode_minus':False,'font.size':12,
 'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
z=NormalDist().inv_cdf(.975); zb=NormalDist().inv_cdf(.8)
cases=[]
for a,b in [(.01,.02),(.02,.03),(.02,.04),(.04,.06)]:
 p=(a+b)/2
 n=math.ceil((z*math.sqrt(2*p*(1-p))+zb*math.sqrt(a*(1-a)+b*(1-b)))**2/(b-a)**2)
 cases.append(dict(control_rate=a,treatment_rate=b,per_arm=n,total=2*n))
fig,ax=plt.subplots(figsize=(11,5.2))
labels=[f"{x['control_rate']:.0%} → {x['treatment_rate']:.0%}" for x in cases]
vals=[x['total'] for x in cases]
ax.barh(labels,vals,color='#286491');ax.invert_yaxis();ax.set_xlim(0,max(vals)*1.2)
for i,x in enumerate(cases):ax.text(x['total']+60,i,f"총 {x['total']:,}명 · 그룹당 {x['per_arm']:,}명",va='center',fontsize=11)
ax.set_xlabel('독립적인 적격 사용자 수 (A+B 합계)');ax.set_title('구매율 A/B 검증에는 수천 명 규모의 표본이 필요할 수 있습니다')
fig.text(.02,.01,'모두 가정한 구매율. 양측 α=5%, 검정력80%, 1:1배정 정규근사. 반복클릭·귀속이벤트 수로 대체 불가.',fontsize=10)
plt.tight_layout(rect=(0,.06,1,1));plt.savefig(R/'juice_figures/10_experiment_sample.png',dpi=160,bbox_inches='tight');plt.close()
promo=[]
fig,ax=plt.subplots(figsize=(11,5.3))
discounts=[0,1000,2000,3000,4000,5000]
for cost,color in [(22000,'#85929e'),(28000,'#286491'),(34000,'#bd7d22')]:
 ratios=[(39900-cost)/(39900-d-cost) if 39900-d-cost>0 else None for d in discounts]
 promo.append(dict(assumed_variable_cost=cost,discounts=discounts,required_order_ratio=ratios))
 ax.plot(discounts,ratios,marker='o',color=color,label=f'변동비 {cost:,}원 가정')
ax.axhline(1,color='#222',linestyle='--',linewidth=1);ax.set_ylim(0,7.4);ax.set_xticks(discounts,[f'{v:,}' for v in discounts]);ax.set_xlabel('50포 한 박스당 판매자 부담 할인 (원)');ax.set_ylabel('광고 전 총기여이익 유지에 필요한 순주문 배수');ax.set_title('프로모션은 주문 증가보다 할인 후 이익으로 판단해야 합니다');ax.legend(loc='upper left')
fig.text(.02,.01,'현재가39,900원·주문당1박스·변동비 고정·광고비 동일 가정. 실제 원가와 수요 반응이 아니며 할인 실행안 아님.',fontsize=10)
plt.tight_layout(rect=(0,.06,1,1));plt.savefig(R/'juice_figures/11_promotion_threshold.png',dpi=160,bbox_inches='tight');plt.close()
(R/'juice_experiment_design_2026-10-27.json').write_text(json.dumps(dict(
 alpha=.05,power=.8,allocation='1:1 independent eligible users',method='two-proportion normal approximation',
 sample_size_scenarios=cases,promotion_scenarios=promo,
 sources=['https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.power_proportions_2indep.html',
 'https://www.microsoft.com/en-us/research/wp-content/uploads/2016/06/ftir-online-evaluation-final-journal.pdf'],
 limitations=['Baseline purchase rate unknown; total ad conversions are not net purchases',
 'Naver random assignment and exposure linkage are unverified',
 'Cluster or time-block tests require separate design; this sample-size formula does not apply']),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(cases))
