"""Build local seller-review page; photos stay unmodified. Render PNGs with Pillow typesetting/compositing."""
from pathlib import Path
import shutil,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.venv-report'))
OUT=ROOT/'result/juice_seller_pack_2026-11-15'
OUT.mkdir(parents=True,exist_ok=True)
GEN=Path('C:/Users/jun99/.codex/generated_images/01a14f2d-2edc-7972-9435-1d415e442040')
sources={
 'product.png':ROOT/'result/juice_scene_02_pouch.png',
 'sip.png':GEN/'exec-5561631f-be68-4287-bb8e-377953b69d7d.png',
 'howto_icons.png':GEN/'exec-30d34412-f378-4ecc-8bf5-0e9bbfe7df9f.png',
 'box.png':ROOT/'result/juice_scene_04_box.png',
}
for name,source in sources.items():
 assert source.is_file(),source
 shutil.copy2(source,OUT/name)

HTML='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>청송사과즙 · 판매자 검토 시안</title>
<style>
*{box-sizing:border-box}body{margin:0;background:white;color:#24352c;font-family:'Malgun Gothic',sans-serif}main{width:860px;margin:auto}h1,h2,p{margin:0}h1{font-size:64px;line-height:1.25;letter-spacing:-3px;font-weight:800}h2{font-size:44px;line-height:1.3;letter-spacing:-1.6px}p{font-size:26px;line-height:1.6;color:#59645c}.eyebrow{font-size:18px;letter-spacing:3px;color:#6b7a6e;margin-bottom:18px}.small{font-size:17px;line-height:1.7;color:#798079}.card{padding:54px 50px;overflow:hidden;border-bottom:1px solid #e8ede7}.hero{height:1220px;text-align:center;padding-top:40px}.review{font-size:15px;color:#7c827c;margin-bottom:24px}.hero img{display:block;height:575px;width:720px;object-fit:contain;margin:10px auto 6px}.spec{font-size:27px;color:#41513f;letter-spacing:.3px}.price{font-size:57px;font-weight:800;color:#ab4637;margin-top:14px;letter-spacing:-1px}.price span{font-size:29px;color:#334b34;margin-left:20px;font-weight:600}.origin{font-size:21px;margin-top:10px}.sip{height:1250px}.sip h2{margin-bottom:24px}.sip img{width:760px;height:860px;object-fit:cover;object-position:center 39%;border-radius:8px;display:block}.sip .small{text-align:right;margin-top:10px}.howto{height:720px;text-align:center;padding-top:62px}.howto h2{margin-bottom:22px}.howto img{width:760px;height:270px;object-fit:contain;display:block;margin:0 auto}.labels{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.labels strong{font-size:26px}.labels p{font-size:20px;margin-top:7px}.howto>.small{margin-top:25px}.process{height:1000px;padding-top:60px}.process>p{margin-top:18px}.steps{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:35px}.step{border:1px solid #dce6d8;border-radius:18px;padding:25px 28px;min-height:205px}.num{font-size:19px;color:#a0ad95}.step h3{font-size:31px;margin:8px 0 10px}.step p{font-size:23px}.process .small{margin-top:25px}.box{height:1220px;text-align:center;padding-top:55px}.box .stats{display:flex;justify-content:center;gap:45px;margin:23px 0}.stats b{font-size:42px}.stats span{font-size:22px;color:#71806e}.box img{width:760px;height:665px;object-fit:cover;object-position:center 49%;display:block;border-radius:8px;margin-top:25px}.box .small{margin-top:14px}.certificate{padding:58px 50px 50px;min-height:480px}.certificate .eyebrow{letter-spacing:1px}.certslot{border:1px dashed #b8c7b5;border-radius:12px;margin-top:26px;padding:32px;text-align:center;background:#fafcf8}.certslot strong{font-size:25px}.certslot p{font-size:20px;margin-top:10px}.certificate>.small{margin-top:20px}.ending{text-align:center;padding:50px 50px 58px;background:#fafbf8}.ending h2{font-size:42px}.ending .price{font-size:49px;margin-bottom:20px}.ending p{font-size:20px}.ending .small{font-size:16px;margin-top:26px}.asset-only .card{border:0}body.asset-only main{margin:0}.asset-only .review{visibility:hidden}
</style></head><body><main>
<section class="card hero" id="card-01"><div class="review">판매자 검토용 시안 · 상품정보·인증서 확인 전</div><div class="eyebrow">삼형제농원</div><h1>청송사과즙<br>한 포로 가볍게.</h1><img src="product.png" alt="청송사과즙 파우치 연출 이미지"><div class="spec">120ml × 50포</div><div class="price">29,900원<span>무료배송</span></div><p class="origin">국내산 청송군 사과 100%</p><p class="small" style="margin-top:8px">제품 연출 이미지</p></section>
<section class="card sip" id="card-02"><div class="eyebrow">뜯고, 마시고.</div><h2>뜯어서,<br>바로 한 모금.</h2><img src="sip.png" alt="파우치 모서리로 한 모금 마시는 AI 모델"><p class="small">AI 모델 연출 이미지</p></section>
<section class="card howto" id="card-03"><div class="eyebrow">취향대로 간편하게</div><h2>이렇게 드세요</h2><img src="howto_icons.png" alt="뜯은 파우치, 주스 컵, 냉장고의 귀여운 안내 그림"><div class="labels"><div><strong>뜯어서 한 모금</strong><p>가볍게 꺼내 마셔요</p></div><div><strong>컵에 따라</strong><p>식탁 위에서도 간편하게</p></div><div><strong>차갑게</strong><p>시원하게 즐기고 싶을 때</p></div></div><p class="small">보관방법은 완제품 표시를 확인하고, 개봉 후에는 바로 드세요.</p></section>
<section class="card process" id="card-04"><div class="eyebrow">만드는 과정</div><h2>씻고, 짜고,<br>한 포씩 담습니다.</h2><p>사과즙이 파우치에 담기기까지,<br>네 단계로 쉽게 살펴보세요.</p><div class="steps"><div class="step"><div class="num">01</div><h3>사과 세척</h3><p>사과를 깨끗하게 씻어요.</p></div><div class="step"><div class="num">02</div><h3>착즙</h3><p>씻은 사과에서 즙을 짜요.</p></div><div class="step"><div class="num">03</div><h3>파우치 충전</h3><p>한 포씩 담고 밀봉해요.</p></div><div class="step"><div class="num">04</div><h3>박스 포장</h3><p>50포 구성으로 담아요.</p></div></div><p class="small">공정 이해를 돕는 설명도입니다. 실제 제조 현장 사진은 별도 확인 후 반영합니다.<br>세부 공정·조건은 제조원 자료 확인 후 확정합니다.</p></section>
<section class="card box" id="card-05"><div class="eyebrow">한 박스 구성</div><h2>한 포는 간편하게,<br>한 박스는 넉넉하게.</h2><div class="stats"><div><b>120<span>ml</span></b><p>한 포</p></div><div><b>50<span>포</span></b><p>한 박스</p></div><div><b>6<span>L</span></b><p>총 용량</p></div></div><img src="box.png" alt="손잡이 박스와 파우치 구성 연출"><p class="small">AI 연출 이미지 · 실제 박스 디자인과 포장 모습은 실사진으로 교체합니다.</p></section>
<section class="certificate"><div class="eyebrow">인증 · 확인 자료</div><h2>인증서도<br>함께 확인하세요.</h2><div class="certslot"><strong>공식 인증서가 들어갈 자리</strong><p>인증명 · 사업장명 · 인증번호 · 유효기간</p></div><p class="small">공식 인증서 보유는 판매자 전달 사항입니다. 인증명과 적용 범위는 자료 확인 중입니다.<br>HACCP 인증 여부는 아직 확정하지 않았으며, 확인 전 인증 마크를 표기하지 않습니다.</p></section>
<footer class="ending"><h2>청송사과즙 120ml × 50포</h2><div class="price">29,900원<span>무료배송</span></div><p>삼형제농원</p><p class="small">제조일·소비기한·보관법은 현재 출고 제품의 표시사항으로 확인 후 반영합니다.<br>제주·도서 추가 배송비와 출고 마감은 최종 상품정보에서 확인합니다.</p></footer>
</main><script>const chosen=new URLSearchParams(location.search).get('card');if(chosen){document.body.classList.add('asset-only');document.querySelectorAll('main > *').forEach(el=>{if(el.id!=='card-'+chosen)el.remove()});}</script></body></html>'''
HTML=HTML.replace('<footer class="ending">','''<section style="padding:50px"><div class="eyebrow">제품정보 · 주문 안내</div><h2>주문 전에 확인하세요.</h2><table style="width:100%;border-collapse:collapse;font-size:23px;margin-top:30px;line-height:1.7">
<tr><td style="padding:15px;border-bottom:1px solid #e2e9de">내용량</td><td>120ml × 50포 · 총 6L</td></tr>
<tr><td style="padding:15px;border-bottom:1px solid #e2e9de">원재료 표기</td><td>국내산 청송군 사과 100%</td></tr>
<tr><td style="padding:15px;border-bottom:1px solid #e2e9de">식품유형</td><td>과·채주스</td></tr>
<tr><td style="padding:15px;border-bottom:1px solid #e2e9de">제조원 기록</td><td>청송사과식품 · 최신 라벨 확인 예정</td></tr>
<tr><td style="padding:15px;border-bottom:1px solid #e2e9de">제조일·소비기한</td><td>현재 출고 파우치 각인 확인 후 기재</td></tr>
<tr><td style="padding:15px;border-bottom:1px solid #e2e9de">보관방법</td><td>완제품 표시 확인 · 개봉 후 바로 음용</td></tr>
</table><p style="margin-top:35px;font-size:23px">영업일 낮 12시 전 주문 당일 발송 · 주문당 최대 3박스</p><p style="font-size:20px;color:#798079">기존 운영 결정 기준이며, 현재 실제 출고 일정 확인 후 확정합니다.<br>제주·도서 추가 배송비와 파손·불량 교환/환불 조건은 판매자 확인 후 반영합니다.</p></section><footer class="ending">''')
(OUT/'index.html').write_text(HTML,encoding='utf-8')
manifest={'requests':[108,109,110],'price_krw':29900,'shipping':'무료배송','live_applied':False,
 'certificate':{'seller_reports_official_certificate':True,'name_verified':False,'haccp_verified':False,'badge_included':False},
 'assets':{n:str(s.relative_to(ROOT)) if s.is_relative_to(ROOT) else s.name for n,s in sources.items()},
 'outputs':['full_page.png','01_product.png','02_sip.png','03_how_to.png','04_process.png','05_box.png'],
 'notes':['포장 사진과 모델은 AI 연출. 실제 고객·제조현장 아님.','공정은 설명도이며 실제 공장사진은 미확보.','인증서와 현재출고표시사항 확인 전 판매자 검토용.','원본장면 생성해상도를 보존하며 HTML에서 배치, 라벨 픽셀 동일성 미보장.']}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def render_images():
 from PIL import Image,ImageDraw,ImageFont,ImageOps
 W=860
 ink='#24352c';muted='#667264';red='#aa4637';line='#e2e9de'
 bold='C:/Windows/Fonts/malgunbd.ttf';regular='C:/Windows/Fonts/malgun.ttf'
 def font(size,strong=False):return ImageFont.truetype(bold if strong else regular,size)
 def text(im,value,y,size=26,color=ink,strong=False,x=50,center=False):
  d=ImageDraw.Draw(im);f=font(size,strong)
  for row in value.split('\n'):
   xx=(W-d.textlength(row,font=f))/2 if center else x
   box=d.textbbox((xx,y),row,font=f)
   assert box[0]>=25 and box[2]<=W-25 and box[3]<im.height-15,(row,box,im.size)
   d.text((xx,y),row,font=f,fill=color)
   y+=round(size*1.5)
  return y
 def photo(im,name,box,contain=False,position=(.5,.5)):
  source=Image.open(OUT/name).convert('RGBA');x,y,w,h=box
  if contain:
   source=ImageOps.contain(source,(w,h),method=Image.Resampling.LANCZOS)
   x+=(w-source.width)//2;y+=(h-source.height)//2
  else:source=ImageOps.fit(source,(w,h),method=Image.Resampling.LANCZOS,centering=position)
  im.paste(source,(x,y),source)
 def canvas(h):return Image.new('RGB',(W,h),'white')
 cards=[]
 im=canvas(1220)
 text(im,'판매자 검토용 시안 · 인증서 자료 확인 전',30,16,color=muted,center=True)
 text(im,'삼형제농원',80,20,color=muted,center=True)
 text(im,'청송사과즙\n한 포로 가볍게.',135,62,strong=True,center=True)
 photo(im,'product.png',(70,340,720,595),contain=True)
 text(im,'120ml × 50포',950,29,center=True)
 text(im,'29,900원',1002,57,color=red,strong=True,center=True)
 text(im,'무료배송',1082,28,strong=True,center=True)
 text(im,'국내산 청송군 사과 100%',1132,23,center=True)
 text(im,'제품 연출 이미지',1180,16,color=muted,center=True)
 cards.append(('01_product.png',im))
 im=canvas(1200)
 text(im,'뜯고, 마시고.',48,20,color=muted)
 text(im,'뜯어서,\n바로 한 모금.',96,46,strong=True)
 photo(im,'sip.png',(50,265,760,855),position=(.5,.38))
 text(im,'AI 모델 연출 이미지',1144,17,color=muted)
 cards.append(('02_sip.png',im))
 im=canvas(650)
 text(im,'취향대로 간편하게',45,20,color=muted,center=True)
 text(im,'이렇게 드세요',92,45,strong=True,center=True)
 photo(im,'howto_icons.png',(50,190,760,270),contain=True)
 d=ImageDraw.Draw(im)
 for cx,title,sub in [(177,'뜯어서 한 모금','꺼내서 바로'),(430,'컵에 따라','식탁 위에서도'),(683,'차갑게','시원하게 즐겨요')]:
  for value,yy,sz,strong in [(title,470,25,True),(sub,518,20,False)]:
   f=font(sz,strong);tw=d.textlength(value,font=f);assert 10<cx-tw/2 and cx+tw/2<850
   d.text((cx-tw/2,yy),value,font=f,fill=ink if strong else muted)
 text(im,'보관방법은 완제품 표시를 확인하고, 개봉 후에는 바로 드세요.',588,18,color=muted,center=True)
 cards.append(('03_how_to.png',im))
 im=canvas(1000)
 text(im,'만드는 과정',48,20,color=muted)
 text(im,'씻고, 짜고,\n한 포씩 담습니다.',95,46,strong=True)
 text(im,'사과즙이 파우치에 담기기까지, 네 단계로 살펴보세요.',260,24,color=muted)
 d=ImageDraw.Draw(im)
 steps=[('01','사과 세척','사과를 깨끗하게 씻어요.'),('02','착즙','씻은 사과에서 즙을 짜요.'),('03','파우치 충전','한 포씩 담고 밀봉해요.'),('04','박스 포장','50포 구성으로 담아요.')]
 for i,(n,title,sub) in enumerate(steps):
  x=50+(i%2)*390;y=345+(i//2)*235
  d.rounded_rectangle((x,y,x+370,y+215),radius=18,outline=line,width=2)
  text(im,n,y+22,20,color=muted,x=x+25)
  text(im,title,y+65,31,strong=True,x=x+25)
  text(im,sub,y+125,22,x=x+25)
 text(im,'공정 이해를 돕는 설명도입니다. 실제 제조 현장 사진은 별도 확인합니다.',867,18,color=muted)
 text(im,'세부 공정과 조건은 제조원 자료 확인 후 확정합니다.',907,18,color=muted)
 cards.append(('04_process.png',im))
 im=canvas(1220)
 text(im,'한 박스 구성',48,20,color=muted,center=True)
 text(im,'한 포는 간편하게,\n한 박스는 넉넉하게.',94,43,strong=True,center=True)
 text(im,'120ml  ×  50포  =  총 6L',255,36,strong=True,center=True)
 photo(im,'box.png',(50,345,760,760),position=(.5,.30))
 text(im,'AI 연출 이미지 · 실제 박스와 포장은 실사진으로 교체합니다.',1136,18,color=muted,center=True)
 cards.append(('05_box.png',im))
 for name,im in cards:im.save(OUT/name)
 cert=canvas(510);text(cert,'인증 · 확인 자료',40,20,color=muted)
 text(cert,'인증서도 함께 확인하세요.',85,42,strong=True)
 d=ImageDraw.Draw(cert);d.rounded_rectangle((50,185,810,335),radius=14,outline='#bccbb8',width=2,fill='#fafcf8')
 text(cert,'공식 인증서가 들어갈 자리',214,28,strong=True,center=True)
 text(cert,'인증명 · 사업장명 · 인증번호 · 유효기간',272,22,center=True)
 text(cert,'공식 인증서 보유는 판매자 전달 사항이며, 자료 확인 후 반영합니다.',370,18,color=muted)
 text(cert,'HACCP 여부는 아직 미확인으로, 인증 마크는 넣지 않았습니다.',409,18,color=muted)
 end=canvas(330);text(end,'청송사과즙 120ml × 50포',38,36,strong=True,center=True)
 text(end,'29,900원 · 무료배송',100,44,color=red,strong=True,center=True)
 text(end,'삼형제농원',175,25,center=True)
 text(end,'제조일·소비기한·배송 안내는 현재 출고 제품 정보 확인 후 반영합니다.',242,17,color=muted,center=True)
 details=canvas(970)
 text(details,'제품정보 · 주문 안내',42,20,color=muted)
 text(details,'주문 전에 확인하세요.',88,42,strong=True)
 d=ImageDraw.Draw(details)
 info=[('내용량','120ml × 50포 · 총 6L'),('원재료 표기','국내산 청송군 사과 100%'),('식품유형','과·채주스'),('제조원 기록','청송사과식품 · 최신 라벨 확인 예정'),('제조일·소비기한','현재 출고 파우치 각인 확인 후 기재'),('보관방법','완제품 표시 확인 · 개봉 후 바로 음용')]
 for i,(k,v) in enumerate(info):
  yy=190+i*85;d.line((50,yy+65,810,yy+65),fill=line,width=1)
  text(details,k,yy,22,color=muted,x=50);text(details,v,yy,22,x=280)
 text(details,'영업일 낮 12시 전 주문 당일 발송',745,25,strong=True)
 text(details,'주문당 최대 3박스',794,25,strong=True)
 text(details,'출고 일정·제주/도서 추가 배송비·교환/환불 조건은 판매자 확인 후 확정합니다.',864,17,color=muted)
 text(details,'표시사항은 현재 출고 제품의 완제품 라벨을 받은 뒤 최종 반영합니다.',905,17,color=muted)
 full=canvas(sum(im.height for _,im in cards)+cert.height+details.height+end.height)
 y=0
 for im in [im for _,im in cards]+[cert,details,end]:
  full.paste(im,(0,y));y+=im.height
 full.save(OUT/'full_page.png')
 # One sheet keeps every section visible without making the product cards unreadable.
 contact=Image.new('RGB',(1440,650),'white');draw=ImageDraw.Draw(contact)
 for i,(name,im) in enumerate(cards):
  thumb=ImageOps.contain(im,(270,565),method=Image.Resampling.LANCZOS)
  contact.paste(thumb,(i*288+(288-thumb.width)//2,55))
  draw.text((i*288+16,14),name,font=font(18),fill=ink)
 contact.save(OUT/'contact_sheet.png')
 preview=ImageOps.contain(full,(430,3500),method=Image.Resampling.LANCZOS);preview.save(OUT/'full_page_preview.png')
 manifest['render']='Pillow typesetting/compositing from unchanged source photos; browser page content checked, browser PNG export timed out'
 manifest['image_sizes']={name:list(im.size) for name,im in cards}|{'full_page.png':list(full.size)}
 (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Saved full_page.png and five separate image cards.')

if __name__=='__main__':
 render_images()
 print(OUT)
