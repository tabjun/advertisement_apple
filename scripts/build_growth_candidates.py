"""Build an evidence-linked candidate backlog; no live campaigns or messages are sent."""
from pathlib import Path
import json,csv,re,html,base64
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'result'
read=lambda n:json.loads((R/n).read_text(encoding='utf-8-sig'))
num=lambda s:float(re.sub(r'[^0-9.-]','',str(s)) or 0)
media=defaultdict(lambda:dict(impressions=0,clicks=0,cost=0,events=0))
for row in read('ads_media_2025-11-01_2026-01-31.json')['rows']:
    group='콘텐츠' if row[3]=='콘텐츠' else ('네이버 검색' if '네이버' in row[1] else '외부 검색')
    for key,col in [('impressions',4),('clicks',5),('cost',8),('events',10)]:media[group][key]+=num(row[col])
assert [sum(v[k] for v in media.values()) for k in ['impressions','clicks','cost','events']]==[26783,112,8481,1]
for v in media.values():v['ctr']=v['clicks']/v['impressions']*100;v['cpc']=v['cost']/v['clicks']
with (R/'ads_search_term_clicks_2025-11-01_2026-01-31.csv').open(encoding='utf-8-sig') as f:terms=list(csv.DictReader(f))
confused=[x for x in terms if x['검색어'] in ['삼형제농장현서면','얼음골사과밀양주스','청도형제사과즙']]
assert sum(int(x['클릭']) for x in confused)==3 and sum(int(x['광고비(원)']) for x in confused)==220
kw={x['keyword']:x for x in csv.DictReader((R/'juice_keyword_priority_2026-10-28.csv').open(encoding='utf-8-sig'))}
assert kw['사과즙100포']['monthly_upper']==kw['사과즙50포']['monthly_upper']=='450'
S={
 'M':('과거3개월 매체별 원자료','../result/ads_media_2025-11-01_2026-01-31.json'),
 'H':('322일 광고 이력 원자료','../result/ads_history_expanded_2026-10-20.json'),
 'L':('공개 상품 규격·구매제한 기록','../result/juice_own_listing_2026-10-27.json'),
 'Q':('과거 클릭 검색어','../result/ads_search_term_clicks_2025-11-01_2026-01-31.csv'),
 'K':('10/28 키워드364개','../result/juice_keyword_priority_2026-10-28.csv'),
 'P':('판매자·제품·후기 근거','../result/juice_seller_evidence_2026-10-28.json'),
 'D':('실제 소재6검색어 진단','../result/juice_diagnostics_2026-10-28.json'),
 'T':('현재 제목 시험','../result/juice_title_trial_2026-10-28.json'),
 'N1':('쇼핑 매체·입찰 설정','https://ads.naver.com/help/faq/1508'),
 'N2':('쇼핑 제외검색어','https://ads.naver.com/help/faq/1433'),
 'N3':('ADVoost 개요','https://ads.naver.com/help/faq/1361'),
 'N4':('쇼핑스토리','https://help.sell.smartstore.naver.com/faq/content.help?faqId=4423'),
 'N5':('첫구매·재구매 고객 혜택','https://help.sell.smartstore.naver.com/faq/content.help?faqId=6107'),
 'N6':('판매분석 지표 정의','https://help.sell.smartstore.naver.com/faq/content.help?faqId=17791'),
 'N7':('마케팅 유입과 전환 범위','https://help.naver.com/service/19459/contents/21263?lang=ko&osType=COMMONOS'),
 'C1':('쿠팡 키워드·검색/비검색 입찰','https://ads.coupang.com/AdsPer.html'),
 'C2':('쿠팡 판매·무료노출 신청 안내','https://marketplace.coupang.com/mba-onepage'),
 'A1':('당근 상품·소식·단골 운영','https://bizschool.daangn.com/commerce_startguide'),
 'A2':('친구 농원 당근 업체','https://www.daangn.com/kr/local-profile/삼형제농원-y1s8f2wxd7fq/'),
}
C=[]
def add(area,title,tier,target,evidence,refs,task,gate,metric,stop):
    C.append(dict(id=f'G{len(C)+1:02}',area=area,title=title,priority=tier,target=target,evidence=evidence,source_ids=refs.split(),first_task=task,prerequisite=gate,measurement=metric,stop_or_change=stop,status='후보·미집행'))

add('측정·운영','제조·소비기한·출고 마감 통일','선행 필수','네이버 직접','실제 페이지 날짜가 서로 다르고 상세12시/공지11시 마감이 충돌. 광고 이전 구매 신뢰 문제.','P','수정 대상 필드·현값·확인자·정정값 표 작성','판매자 새 출고 라벨/실제마감 확인, 스토어 수정 권한','정보 일치 여부·출고지연·취소 사유','사실 오류는 실험을 위해 유지하지 않음')
add('측정·운영','상품별 원가·광고후 이익 계산','선행 필수','전 채널','24,900은 상품가 하한이지 원가가 아님. 판매 증가와 손익 증가를 나눠야 함.','P T','포장·배송·수수료·환불·쿠폰의 입력표와 손익식 준비','실제 비용·세금기준·재고/월출고 역량','순판매팩수·광고후 공헌이익·허용CPA','단위공헌이익이 음수인 제안은 확대하지 않음')
add('측정·운영','광고 귀속전환과 사과즙 순주문 대조','선행 필수','네이버 직접','과거 전체전환10이벤트는 주문/타상품/중복귀속 여부 미확인. 판매분석 방문수의 상품선별 조건도 있음.','H N6 N7','상품11659930652·주문일·상태·수량·채널별 집계 사전과 대조표 작성','스토어 주문/취소반품·광고보고서, 개인정보 제외','주문상품 기준 순50포상자·순판매포수·고유주문수','광고이벤트를 실주문이나 증분 주문으로 대체하지 않음')
add('측정·운영','외부 콘텐츠별 유입 경로 측정','선행 필수','네이버 직접','현재 당근이 자사스토어에 연결되지만 게시물별 순주문 기여는 미확보.','P N7','당근소식/블로그/촬영영상 링크 이름과 캠페인 표 작성','현재 통계의 사용자정의 지원·실제 유입 대조. 네이버광고는 광고보고서 사용','콘텐츠별유입·상품방문·순주문, 출처불명 별도','UTM/nt파라미터만으로 모든 앱·네이버광고 소재 추적이 된다고 단정하지 않음')
add('측정·운영','1인1개 제한과 재고·다박스 구매 점검','높음','네이버 직접','10/27 공개 상품은 최대1개 제한. 100포 묶음·단체주문과 양립 가능한지 미확인.','L K','제한의 의도와 2박스 주문 가능 여부 확인 항목 작성','판매자 재고·택배 중량·제한 사유·상품 권한','장바구니/주문수량·품절취소·순판매포수','재고보호 목적이면 임의로 제한 해제하지 않음')
add('측정·운영','맛·내용량·배송 불만의 품질 점검','높음','전 채널','쿠팡 첫페이지10후기에 내용량 지적·기대 맛 차이·배송 지연이 존재. 대표불만율은 아님.','P','로트별 충전 검수·맛 설명·발송표를 연결한 점검표와 FAQ 작성','실제 검수자료/공정/배송 기록','사유별문의·취소반품·재문의율','후기만으로 실제미달/공정오류를 확정하지 않음')

add('검색·광고','청송사과 구매 의도를 사과즙으로 연결','높음','네이버 직접','청송사과 단독·사과주스는 현소재 카테고리불가, 청송사과즙·사과즙·50포는요건충족.','D K T','청송사과 필수 포함, 상품명·태그·속성·FAQ별 사용처 지도 작성','실제 상품정보·태그사전·현재제목시험 경계 관리','적합검색어 노출·CTR·유입 후 순주문','청송사과 단독 매칭을 보장하거나 생과 카테고리로 억지변경하지 않음')
add('검색·광고','다른 산지·동명 농원 검색어 검토','보조','네이버 직접','현서면·밀양·청도 관련3검색어:3클릭220원. 정리 가치 있으나 큰 비용낭비 원인은 아님.','Q N2','정확한3검색어 제외 검토표와 최근30일 재확인 항목 작성','현재실제검색어·상품별오매칭 확인 후 정확한 범위만','관련없는클릭비·핵심검색유입 유지','청송사과/얼음골 전체를 광범위 차단하지 않음')
add('검색·광고','네이버 검색·외부검색·콘텐츠 지면 분리 검증','높음','네이버 직접','동기간CTR0.804%/0.282%/0.144%, 클릭68/36/8. 전환은 합계1건뿐.','M N1','매체구성·현재 CPC·적합검색어를 비교할 시험 설계','동일예산 내 재배분안·계정 설정 검토, 원가/손실한도','매체별 노출·CTR·CPC·동일상품 순주문','0전환만으로 지면영구중단/요일예산몰빵하지 않음')
add('검색·광고','노출 자격과 입찰 경쟁을 구분한 제한 시험','조건부','네이버 직접','소재 운영가능·일부검색어 요건충족인데 최근7일623노출1클릭. 입찰100원이나 예산 부족 원인은 미입증.','D T N1','같은지면·시간대 노출관찰과 입찰 변경일 기록표 작성','원가·허용CPA·총시험손실한도·금액 확정','추가노출당비용·적합클릭·순주문','일예산10000원이라는 이유만으로 예산을 증액하지 않음')
add('검색·광고','파워링크로 구매형 검색어와 원고 직접 제어','조건부','네이버 직접','쇼핑상품형은 자동매칭. 사과즙 구매형 검색어를 직접 선택하는 다른 광고 방식 후보.','K N2','청송사과즙/청송사과100%/농원명 구매형 그룹과 랜딩 원고 작성','해당비즈채널/심사·도달지 적합성·허용CPC·총한도','적합클릭·순주문CPA·자연유입대체 여부','쇼핑광고와 중복귀속 매출을 합산하지 않음')
add('검색·광고','ADVoost를 별도 확장 후보로 설계','조건부','네이버 직접','자동 피드·지면 최적화 공식지원. 식품 연구는 참고이며 우리매출효과는 미확인.','N3 P','사과즙만 대상인 피드·측정·제외생과·중복귀속 설계','출고/전환측정·총시험한도·마진 확정','스토어 총순판매·광고후 이익, 중복귀속 점검','현재캠페인과 동시에 여러요소 확대하지 않음')

add('상품·표현','상세 첫 화면을 산지·재배자·원재료 순으로','높음','네이버 직접','당근자사스토어연결·직접재배소개·상세사과100%표시 확보. 가격우월소구 제외 지시.','P Q','현재원고: 청송 얼음골에서 키운 사과/사과100%/사과하나/120ml50포','다음로트·표시명칭대조 후스토어 반영','상품방문→순주문·관련문의·반품','증빙없는3대/4만평/인증/당도보장 확장금지')
add('상품·표현','파우치 단품과 박스+파우치 썸네일 비교','높음','네이버 직접','현재실사진은 눕힌파우치. 포장/브랜드와50포구성을 한눈에 연결할 후보.','P T','원본사진 기반 촬영 구도2개·선명도/규격 점검표 작성','실제50포박스·이미지기준,제목시험과시기 분리','같은검색어/지면 CTR·클릭 후 순주문','문구형포스터를 대표이미지로 바로등록하지 않음')
add('상품·표현','산지→세척→착즙→포장 15초 영상','높음','네이버 직접','기계세척/저온착즙에 대한 실제질문·답변 있음. 원물100%만으로 공정궁금증 해소불가.','P','4장면 촬영표·자막·상품명·출고로트 연결 원고 작성','실제농원·공정 촬영 또는 기존사용권있는영상','영상유입·상품클릭·공정문의·순주문','스톡공장/AI공정을 실제제조현장처럼 제시하지 않음')
add('상품·표현','맛·당류·살균·보관 설명 FAQ','높음','전 채널','진한맛호평과 생사과맛기대차이 공존. 사과100%와 당류0은 다름.','P','원재료/공정/맛편차/보관/용량/출고 6문항 초안 작성','현재제품라벨·실제공정·보관조건 확인','문의해결·구매후불일치·순주문','무가당을 당류0/건강효능으로 바꾸지 않음')

add('구성·객단가','첫 구매용 소포장 10·20·30포','조건부','네이버 직접','50포첫구매부담은 가설. 30포검색30–39회, 배송비와 포장비 비중 커질 수 있음.','K P','포수별 생산/포장/배송 손익표,현재24900하한 적용범위 확인','생산·표시/출고가능성·소포장별최저판매조건 별도확정','신규순주문·30일후50포이동·광고후이익','50포24900하한을 임의로 포수비례해 새가격 확정하지 않음')
add('구성·객단가','50포×2박스 100포 묶음','조건부','네이버 직접','100포검색450회,50포도450회. 구성수요 후보이지 동일고객/매출예측 아님.','K P','2박스12L 구성·택배중량·포장·손익표 작성','1인1개제한·재고·배송비·새상품/옵션 적합성','순판매포수·주문당이익·포장파손','판매포수만 늘고 이익/반품 악화하면 축소')
add('구성·객단가','배송포함과 별도배송 제안 비교','조건부','네이버 직접','24900+배송비·29900포함은 사용자제안,실판매가보류. 원가미확인.','P','총결제액24900+S 비교표·상세가격표시 원고 작성','실배송비/지역추가비/원가·사용자최종가격결정','동일규격 순주문·공헌이익·배송비관련문의','가격보류준수,판매가하한아래쿠폰금지')
add('구성·객단가','부모님·가족 선물용 구성','탐색','네이버 직접','실제쿠팡후기에 가족음용/부모님선물 언급. 선물키워드검색은적고대표수요미검증.','P K','실제손잡이박스·포장보호·발송요청 안내1장 작성','선물포장원가/실현가능서비스·출고일','선물용문의→순주문·파손/환불·이익','무료포장·명절도착·어린이안전 보장하지 않음')
add('고객·재구매','50포 소비기간과 재구매 시점 분석','접근 후','네이버 직접','50포1인하루1포면50일,2포면25일은 계산가정. 실제반복구매간격은 미확보.','P N5','신규고객 코호트별30/60/90일 재구매표 정의','익명고객키·동일상품주문·취소반품·성숙기간','고객별 순재구매율·구매간격·이익','25/50일가정을실제발송스케줄로자동설정하지 않음')
add('고객·재구매','생과 구매자에게 사과즙 교차 제안','접근 후','네이버 직접','농원생과판매와당근후기는존재하지만즙선호·대체여부미확인.','P N5','동일스토어 생과구매→즙구매 코호트표와상품연결원고 작성','상품별주문·동의범위·실제재고','생과고객즙첫구매·기존생과매출대체·총이익','쿠팡구매자연락처를추출해네이버광고메시지로전용하지 않음')
add('고객·재구매','네이버 알림 동의 고객 소식·혜택','접근 후','네이버 직접','공개관심고객47명은 발송동의/도달가능47명과 다름. 공식고객별혜택지원.','P N5','동의고객용 출시소식1개·혜택없이상품사실중심원고 작성','동의여부·발송권한/비용·출고가능','도달·클릭·고유순주문·수신거부·이익','동의없는발송/플랫폼간연락처전용 안함')
add('고객·재구매','당근 기존 단골에게 상품 소식 정비','높음','네이버 유입 후보+당근 매출','당근단골986명·업체후기325개와상품링크존재. 신규유료광고 전 기존자산 후보.','P A1 A2','청송사과필수·로트/구성/출고확인 후게시할소식1개 작성','당근운영권한·링크/상품첨부 가능범위·실재고','소식조회·상품클릭·채널별순주문','986명을실제도달수/사과즙구매자로간주하지 않음')

add('콘텐츠·협력','쇼핑스토리로 농원과 제조 과정 설명','높음','네이버 직접','공식쇼핑스토리는상품연결가능. 당근/쿠팡의공정질문과일치.','P N4','청송사과가사과하나가되기까지 이미지/원고 초안 작성','스토어접근·실제공정자료·제조표기','스토리→상품유입·순주문·관련문의','스토리 노출만으로검색순위상승을약속하지 않음')
add('콘텐츠·협력','질문형 검색 콘텐츠 3편','높음','네이버 유입 후보','사과즙효능검색1190회는구매량아님. 건강주장대신원재료/착즙/맛·보관질문공략.','K P','청송사과즙원재료읽기/청송얼음골농원소개/50포구성알기 3편개요','실제자료·게시채널권한·외부링크정책','콘텐츠검색유입·상품방문·순주문','체험담으로효능·진위확인안된인증을만들지 않음')
add('콘텐츠·협력','짧은 상품 설명 영상 후 라이브 검토','탐색','네이버 직접','상품영상이있고판매자가답할공정질문도있으나라이브시청수요/자격미확인.','P N4','짧은영상대본과소규모질의응답 진행표 작성','숏클립/라이브 현재등록자격·권한·촬영·재고 확인','영상/라이브상품클릭·순주문·제작비차감이익','방송만하면유입이생긴다고예산선집행하지 않음')
add('콘텐츠·협력','공개 조건의 체험·콘텐츠 협업','탐색','네이버 유입 후보','현재제품설명과실물증빙이판매신뢰자산. 협업매출효과나적합크리에이터는미확인.','P','가격이아닌농원/제품기반협업브리프·비용표·성과링크 설계','콘텐츠사용권/표시조건·매체정책·비용한도·상품제공 가능성','링크별상품유입·순주문·협업비포함이익','별점/긍정후기강요·숨은광고·중복귀속금지')

add('다른 채널·새 수요','쿠팡 키워드·비검색 광고 분리 후보','조건부','쿠팡 매출·네이버와 별도','실제동일상품판매중. 공식수동광고는키워드입찰/제외/검색비검색제어가능.','P C1','청송사과즙구매형그룹·검색/비검색분리·기존노출중복 확인표','쿠팡판매자권한·기존광고/정산·원가/한도','쿠팡순주문·광고비포함공헌이익','쿠팡판매를네이버매출증가로보고하지 않음')
add('다른 채널·새 수요','쿠팡 무료노출 프로모션 자격 점검','접근 후','쿠팡 매출·네이버와 별도','공식안내에무료노출신청이있으나일부판매자/구좌/상품조건제한.','P C2','윙에서신청가능여부·할인/재고조건·기존상품매칭 확인표','쿠팡접근·참여조건·정산/마진 검토','추가비용/가격조건포함순주문·이익','무료노출을무비용/노출보장이라고해석하지 않음')
add('다른 채널·새 수요','당근 소식 광고·지역별 반응 후보','조건부','당근 매출·네이버 유입 별도측정','현재상품/단골/소식존재. 공식당근은소식·상품·광고운영경로지원. 지역별구매분포는미확보.','P A1','기존구매배송지역집계후후보지역/소재/랜딩분리 설계','집계데이터·당근광고권한/자격·비용한도','지역별문의·상품클릭·순주문CPA','단골소재지/사용자개인정보로무단타기팅하지 않음')
add('다른 채널·새 수요','소규모 사업장·단체용 50포 공급','탐색','신규 단체 매출','파우치/50포박스가실물구성. 단체수요·납품가능가격/마진은미검증 사업가설.','P','복지간식/사무실공용음료용1장제안서·필요포수·배송/증빙 조건표','공급량·사업자거래/정산·마진·상담대상확정','유효문의→견적→유료순주문·주문당이익','단체주문가능성만으로리드명단에무단발송하지 않음')
add('다른 채널·새 수요','청송 방문객·오프라인 판매 연결','탐색','오프라인 매출·네이버 유입 후보','당근은농원방문구매안내·주왕산면소재지공개. 방문/관광객즙수요는미확인.','P A2','방문판매가능시간/현장재고/상품안내·자사스토어링크 원고 작성','실제방문운영·파트너허락·포장·판매조건','현장유료판매·허용된링크유입·순주문','농원주소존재만으로관광객유동량/제휴를만들지 않음')
add('다른 채널·새 수요','맛 체험 후 온라인 재구매 경로','탐색','오프라인→네이버 후보','맛기대차이후기와한포구성. 시음이구매를늘린다는결과는없음.','P','실제제품시음조건·보관·샘플원가·재구매링크 설계','운영장소허락/위생·제공제품·총비용 확인','시음비포함순유료주문·후속구매','배포수/만족응답을유료판매로대체하지 않음')
add('측정·운영','광고·판매 파일의 반복 집계 자동화','접근 후','전 채널 측정','322일광고자료와최근스냅샷·키워드/매체파일이분리. 데이터없음/0구분필요.','M Q N6 N7','일별상품/채널집계스키마·공개정보/주문집계 연결·변경로그 준비','지원API/엑셀·권한/보존기간 확인,개인정보열제외','누락일·합계대조·갱신시각·순주문/광고비','API키발급만으로주문·광고전체접근가능하다가정하지 않음')
add('다른 채널·새 수요','100%·NFC·추천형 검색의 추가 수요 검토','탐색','네이버 직접','사과즙100%130회/NFC사과즙90회/사과즙추천170회. 현상품100%표시있고NFC는기존공개주장이지만공정검증필요.','K P D','수요어별 사실/증빙/광고매칭/상세활용 표 작성','NFC공정·당해원재료·매칭진단·사실표현적합성','관련검색유입·순주문·CPA','유기농/영유아/제로슈거 등없는속성으로확장하지 않음')
assert len(C)==36 and len({x['id'] for x in C})==36

payload={'as_of':'2026-10-28','candidate_count':len(C),'candidates':C,'sources':{k:{'title':v[0],'url':v[1]} for k,v in S.items()},'reanalysis':{'media_period':'2025-11-01~2026-01-31','media':dict(media),'cross_region_terms':confused,'cross_region_clicks':3,'cross_region_cost':220,'cross_region_cost_share_of_clicked_query_cost_pct':220/7678*100,'mobile_click_share_pct':104/112*100,'bulk100_monthly_searches':450,'pack50_monthly_searches':450},'limits':['후보36개는36개실험완료/효과입증아님','고객기반·주문·이익미확인','실행권한/총지출한도미확정인외부변경없음','청송사과필수·가격우월성소구제외·현재제목시험유지']}
(R/'juice_growth_candidates_2026-10-28.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
with (R/'juice_growth_candidates_2026-10-28.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=list(C[0]);w=csv.DictWriter(f,fields);w.writeheader();w.writerows({**x,'source_ids':' '.join(x['source_ids'])} for x in C)

def refs(ids):
    out=[]
    for k in ids:
        label,url=S[k]
        if url.startswith('../result/'):url='https://github.com/tabjun/advertisement_apple/blob/main/result/'+url.split('/')[-1]
        out.append(f'<a href="{html.escape(url)}">{html.escape(label)}</a>')
    return ' · '.join(out)

media_rows=''.join(f'<tr><td>{k}</td><td>{int(v["impressions"]):,}</td><td>{int(v["clicks"])}</td><td>{v["ctr"]:.3f}%</td><td>{int(v["cost"]):,}원</td><td>{int(v["events"])}</td></tr>' for k,v in media.items())
sections=[]
for area in dict.fromkeys(x['area'] for x in C):
    items=[]
    for x in C:
        if x['area']!=area:continue
        items.append(f'''<details class="growth-item" data-area="{area}" data-priority="{x['priority']}"><summary>{x['id']} · {x['title']} <span class="note">[{x['priority']}]</span></summary><p><b>도달할 매출:</b> {x['target']}</p><p><b>근거와 가설:</b> {x['evidence']}</p><p><b>첫 실행 태스크:</b> {x['first_task']}</p><p><b>적용 조건:</b> {x['prerequisite']}</p><p><b>확인할 효과:</b> {x['measurement']}</p><p><b>수정·중단 기준:</b> {x['stop_or_change']}</p><p class="note">{refs(x['source_ids'])}</p></details>''')
    sections.append(f'<h3 class="growth-group" data-area="{area}">{area}</h3>'+''.join(items))

image_path=next((R/'juice_figures').glob('02_*.png'))
img='data:image/png;base64,'+base64.b64encode(image_path.read_bytes()).decode()
section=f'''<section id="growth-candidates"><style>#growth-candidates .growth-item{{border-bottom:1px solid #ddd;padding:12px 0}}#growth-candidates summary{{cursor:pointer;font-weight:700}}#growth-candidates .growth-item p{{margin:7px 0}}#growth-candidates .filters{{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}}#growth-candidates input,#growth-candidates select{{padding:12px;font:inherit;border:1px solid #aab8a8;border-radius:8px;background:white;color:#203c30}}#growth-candidates .flow b{{font-size:16px}}#growth-candidates [hidden]{{display:none!important}}</style>
<div class="eyebrow">2026.10.28 확대 분석 · 기존 제목 시험과 병행할 성장 후보</div><h2>청송사과즙 판매를 늘릴 36개 후보와, 먼저 할 일을 정리했습니다</h2>
<ul><li><b>지금 할 일:</b> 상품 표시·출고 정보 정정 준비, 실제 공정 FAQ와 촬영 원고, 매체 분리·검색어 정리 설계, 당근 단골용 소식 초안을 병행합니다.</li><li><b>데이터가 뒷받침하는 확장:</b> 과거3개월 네이버검색68클릭/CTR0.804%,외부검색36/0.282%,콘텐츠8/0.144%. 매체별 검증 후보이며 전환1건으로 승패를 정하지 않습니다.</li><li><b>새 구성·고객 후보:</b> 100포검색450회는50포와 같았습니다. 100포묶음·생과고객교차구매·단골재방문은 검토할 이유가 있고, 소포장·단체공급은 손익과 실제 수요를 먼저 확인할 사업가설입니다.</li></ul>
<div class="flow"><div><b>찾게 한다</b><br>SEO·검색/매체·콘텐츠</div><div><b>믿고 고르게 한다</b><br>원재료·사진·공정·출고</div><div><b>다시·더 사게 한다</b><br>묶음·재구매·교차구매</div><div><b>다른 수요를 만난다</b><br>당근·쿠팡·단체·현장</div></div>
<h3>광고 문구 외에 무엇을 먼저 검증할 것인가</h3><img alt="과거 동일기간 매체별 노출 클릭 비용 비교" src="{img}" style="width:100%"><table><tr><th>매체 묶음</th><th>노출</th><th>클릭</th><th>CTR</th><th>비용</th><th>전환 이벤트</th></tr>{media_rows}</table>
<p>2025-11-01–2026-01-31 같은 광고그룹 기간입니다. 네이버 검색은 더 높은 클릭 반응을 보였으나 타깃·지면 위치 차이가 남습니다. 외부검색과 콘텐츠를 즉시 끄는 결론은 아닙니다. 동일조건에서 적합 유입·순주문·광고후 이익을 비교할 이유입니다.</p>
<p>다른 산지/동명업체로 보이는 현서면·밀양·청도 검색어3개는 합계3클릭220원으로, 클릭검색어 비용7,678원의2.9%입니다. 검색어 정리는 보조 개선이며 이 작은 비용만 없애면 판매가 늘어난다고 설명하지 않습니다. 반면 모바일 클릭은104/112=92.9%여서 상품 식별·원재료·출고 설명의 모바일 검수는 우선할 이유가 있습니다.</p>
<h3>후보를 클릭하면 근거·실행 조건·판단 지표가 펼쳐집니다</h3><p>‘높음’은 측정된 예상 매출 순위가 아니라 확인된 구매 장벽과 준비 가능성을 기준으로 정한 작업 우선순위입니다. 후보 목록 작성은 집행 완료가 아닙니다. 공식 기능이 존재해도 현재 계정의 자격·권한·사용 가능 여부는 별도 확인합니다.</p>
<div class="filters"><input id="growth-search" aria-label="후보 검색" placeholder="예: 100포, 재구매, 당근, 매체"><select id="growth-area" aria-label="영역 선택"><option value="">모든 영역</option>{''.join(f'<option>{x}</option>' for x in dict.fromkeys(x['area'] for x in C))}</select><select id="growth-priority" aria-label="준비 우선순위"><option value="">모든 우선순위</option>{''.join(f'<option>{x}</option>' for x in dict.fromkeys(x['priority'] for x in C))}</select><span id="growth-count" role="status">36개 후보</span></div>{''.join(sections)}
<h3>지금 바로 준비해 둔 실행 패키지</h3>
<table><tr><th>패키지</th><th>복사·검토할 초안</th><th>적용 전 필요한 확인</th></tr><tr><td>당근 기존단골 소식</td><td>청송사과를 직접 키우는 삼형제농원입니다. 얼음골 사과하나 사과즙,사과100%·120ml50포 구성을 실제 사진과 원재료표로 소개합니다. 출고일은 확정한 뒤 안내드리겠습니다.</td><td>게시권한·출고일·최종로트·링크/상품첨부범위. 이번에 발송/게시하지 않음.</td></tr><tr><td>공정영상 촬영</td><td>0–3초 청송얼음골농원/사과 →3–7초 실제세척 →7–11초 실제착즙/포장 →11–15초 사과하나·120ml50포. 현장자료만 사용.</td><td>공정촬영/사용권·제조명칭·자막사실대조</td></tr><tr><td>상세 FAQ</td><td>어디서재배하나요? 원재료는무엇인가요? 어떤세척/착즙을하나요? 실제한포용량은? 맛이달라질수있나요? 언제출고되나요?</td><td>새로트라벨·실제공정/보관/검수·출고시각</td></tr><tr><td>100포 구성</td><td>50포2박스=100포·총12L. 포수/박스수/배송포장·추가배송비·손익을 동일표에서 비교.</td><td>1인1개제한·재고·원가·포장/택배중량</td></tr><tr><td>단체공급 제안</td><td>청송사과100% 사과하나120ml파우치. 필요포수·행사일·배송지수·예산·증빙서류를 받아 공급가능성과총액을 확인하는1장 제안서.</td><td>실제문의/공급량·가격·납기·정산. 업체에 연락하지 않음.</td></tr></table>
<h3>주말에 스토어 연결 후 바로 할 분석</h3><p>상품·일자·유입경로·규격·결제/취소/반품과 익명고객키를 받아 <b>첫구매/재구매·생과→즙 교차구매·수량별 이익·채널별 순판매</b>를 대조합니다. 광고의 직접/간접 이벤트와 스토어 순주문을 분리합니다. 판매분석의 개별상품 방문수는 조회기간 내 판매가 발생한 상품에 한해 제공되는 조건이 있어, 표시 안 된 상품을 방문0으로 채우면 안 됩니다. 외부링크는 현재통계로 유입을 시험 확인하고 네이버 광고 소재 성과는 광고보고서에서 봅니다.</p>
<p class="note">판매분석/귀속 정의: {refs(['N6','N7'])}. 공식 기능은 방법의 존재를 뒷받침하며 판매 증가를 입증하지 않습니다. 이번 작업은 분석·원고·후보 명세이며 광고/상품/가격/예산·고객발송·외부제휴 변경은 없습니다.</p></section>
<script>(()=>{{const root=document.getElementById('growth-candidates');if(!root)return;const q=root.querySelector('#growth-search'),a=root.querySelector('#growth-area'),p=root.querySelector('#growth-priority');const run=()=>{{let n=0;root.querySelectorAll('.growth-item').forEach(el=>{{const ok=(!a.value||el.dataset.area===a.value)&&(!p.value||el.dataset.priority===p.value)&&el.textContent.toLowerCase().includes(q.value.toLowerCase());el.hidden=!ok;if(ok)n++;}});root.querySelectorAll('.growth-group').forEach(h=>{{h.hidden=![...root.querySelectorAll('.growth-item')].some(el=>el.dataset.area===h.dataset.area&&!el.hidden);}});root.querySelector('#growth-count').textContent=n+' / 36개 후보';}};[q,a,p].forEach(el=>el.addEventListener('input',run));}})();</script>'''
(ROOT/'scripts/growth_candidates_section.html').write_text(section,encoding='utf-8')
md=['## 10/28 판매 성장 후보36개: 근거와 첫 실행 태스크','', '현재 제목 시험의 실측을 기다리는 동안 진행할 다른 방법을 정리했습니다. 후보 수는 실행 완료/판매 효과 수가 아닙니다. 청송사과 필수·가격 우월성 소구 제외·현재 가격 보류를 유지합니다.','', '[필터로 후보 찾기: 클라이언트 보고서](juice_client_visual_2026-10-27.html) · [후보 전체 CSV](juice_growth_candidates_2026-10-28.csv) · [근거·계산 JSON](juice_growth_candidates_2026-10-28.json)','', '과거 동기간 네이버검색CTR0.804%(68클릭), 외부검색0.282%(36), 콘텐츠0.144%(8), 전환 합계1건. 매체 분리 검증 후보이며 효과 승자 미확정. 다른산지3검색어 광고비220원은 검색어비용7,678원의2.9%라 작은 정리만으로 판매 문제가 해결된다고 주장하지 않습니다. 100포검색450회=50포450회는 구성 검토 근거이며 신규 매출 추정이 아닙니다.','', '| ID | 방법 | 우선순위 | 근거 | 첫 태스크 / 조건 | 측정 |','|---|---|---|---|---|---|']
for x in C:md.append(f"| {x['id']} | {x['title']} | {x['priority']} | {x['evidence']} | {x['first_task']} / {x['prerequisite']} | {x['measurement']} |")
md+=['','판매분석의 개별상품 방문수는 조회기간 내 판매상품만 제공될 수 있어 미표시를0으로 채우지 않습니다. 광고전환·상품별순주문·타채널매출·증분효과는 구분합니다. 단골/통합리뷰를 합산한 구매자수·매출예측·ROI 점수는 만들지 않았습니다.','']
(ROOT/'scripts/growth_candidates_section.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps({'candidates':len(C),'by_area':dict(Counter(x['area'] for x in C)),'by_priority':dict(Counter(x['priority'] for x in C)),'cross_region_cost':220},ensure_ascii=False))
