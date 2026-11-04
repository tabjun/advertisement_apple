"""Local-only 15s motion-video assembly. Run: py -3.12 scripts/make_juice_video.py"""
from pathlib import Path
import sys, json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.venv-report'))
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np
import imageio.v2 as imageio
RESULT=ROOT/'result'; WORK=ROOT/'.codex-build/video101'; WORK.mkdir(parents=True,exist_ok=True)
W,H,FPS=1080,1920,30
BOLD=r'C:\Windows\Fonts\malgunbd.ttf'; REG=r'C:\Windows\Fonts\malgun.ttf'
R=Image.Resampling; CHECKS={}

def scene(index,suffix,fallback):
    p=RESULT/f'juice_scene_{index:02d}_{suffix}.png'
    if not p.is_file():p=RESULT/fallback
    print('source:',p.name,flush=True)
    return Image.open(p).convert('RGB'),p.name

S1,P1=scene(1,'bag','juice_original_product_2026-10-28.webp')
S2,P2=scene(2,'pouch','juice_pouch_label_roll_2026-11-04.jpg')
S3,P3=scene(3,'pour','juice_original_product_2026-10-28.webp')
S4,P4=scene(4,'box','juice_original_product_2026-10-28.webp')
S5,P5=scene(5,'family','juice_original_product_2026-10-28.webp')
SCENES=[
 (3,S1,P1,'출근 가방에 쏙','납작한 파우치, 한 포씩'),
 (3,S2,P2,'청송사과즙 120ml 한 포','국내산 청송군 사과 100%'),
 (3,S3,P3,'개봉해 바로, 또는 컵에 따라','120ml 파우치'),
 (3,S4,P4,'50포 한 박스 · 삼형제농원','영업일 낮 12시 전 주문 당일 발송'),
 (1.5,S5,P5,'','')]
assert sum(s[0] for s in SCENES)+1.5==15

def photo(source,t,square):
    width,height=source.size; zoom=1+0.035*t
    cw,ch=int(width/zoom),int(height/zoom); x,y=(width-cw)//2,(height-ch)//2
    source=source.crop((x,y,x+cw,y+ch))
    if not square:return ImageOps.fit(source,(W,H),method=R.BILINEAR)
    # Preserve the full portrait photo instead of cutting off labels/cups in a square crop.
    im=Image.new('RGB',(W,W),(250,247,242))
    inset=ImageOps.contain(source,(W-40,885),method=R.BILINEAR)
    im.paste(inset,((W-inset.width)//2,15)); return im

def font_fit(draw,text,maxwidth,size,path):
    while size>24:
        font=ImageFont.truetype(path,size)
        if draw.textlength(text,font=font)<=maxwidth:return font
        size-=1
    raise ValueError('Caption does not fit: '+text)

def caption(im,text,sub,alpha=1):
    if not text:return im
    width,height=im.size; square=width==height
    overlay=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(overlay)
    top=height-(190 if square else 320)
    d.rectangle((0,top,width,height),fill=(0,0,0,int(140*alpha)))
    main=font_fit(d,text,width-100,64 if square else 78,BOLD)
    small=font_fit(d,sub,width-100,32 if square else 42,REG)
    bounds=[]
    for value,font,y in [(text,main,height-(155 if square else 260)),(sub,small,height-(65 if square else 120))]:
        x=(width-d.textlength(value,font=font))/2; box=d.textbbox((x,y),value,font=font)
        assert box[0]>=40 and box[2]<=width-40 and box[3]<=height-15,(value,box)
        d.text((x,y),value,font=font,fill=(255,255,255,int(255*alpha))); bounds.append(list(box))
    CHECKS[f'{width}x{height}:{text}']={'main':text,'sub':sub,'bounds':bounds,'inside_frame':True}
    return Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB')

def endcard(square):
    width,height=(W,W) if square else (W,H)
    im=Image.new('RGB',(width,height),(250,247,242)); d=ImageDraw.Draw(im)
    pouch=ImageOps.contain(S2,(640,555 if square else 1010),method=R.LANCZOS)
    im.paste(pouch,((width-pouch.width)//2,25 if square else 80))
    lines=[('청송사과즙',90 if square else 112,630 if square else 1150,'#202020'),
           ('120ml × 50포',60 if square else 74,760 if square else 1320,'#404040'),
           ('29,900원 · 무료배송',62 if square else 78,860 if square else 1460,'#b23a2a'),
           ('삼형제농원',44 if square else 52,970 if square else 1620,'#555555')]
    for text,size,y,color in lines:
        font=font_fit(d,text,width-100,size,BOLD); x=(width-d.textlength(text,font=font))/2
        box=d.textbbox((x,y),text,font=font)
        assert box[0]>=40 and box[2]<=width-40 and box[3]<height-15
        d.text((x,y),text,font=font,fill=color)
        CHECKS[f'end:{width}x{height}:{text}']={'main':text,'bounds':[list(box)],'inside_frame':True}
    return im

def main():
    paths={n:RESULT/f'juice_video_15s_{n}_2026-11-04.mp4' for n in ['9x16','1x1']}
    temp={n:WORK/p.name for n,p in paths.items()}
    writers={n:imageio.get_writer(str(p),fps=FPS,codec='libx264',quality=8,pixelformat='yuv420p',
                 macro_block_size=None,ffmpeg_params=['-movflags','+faststart']) for n,p in temp.items()}
    last={}; count=0; crossfade=int(.25*FPS)
    try:
        for index,(seconds,source,filename,text,sub) in enumerate(SCENES):
            total=int(seconds*FPS); print(f'encoding scene {index+1}: {total} frames',flush=True)
            for k in range(total):
                for name,square in [('9x16',False),('1x1',True)]:
                    fr=caption(photo(source,k/max(1,total-1),square),text,sub,min(1,k/(.25*FPS)))
                    if index and k<crossfade:fr=Image.blend(last[name],fr,k/crossfade)
                    writers[name].append_data(np.asarray(fr))
                    if k==total-1:last[name]=fr
                count+=1
        cards={'9x16':endcard(False),'1x1':endcard(True)}
        for k in range(int(1.5*FPS)):
            for name in writers:
                writers[name].append_data(np.asarray(Image.blend(last[name],cards[name],min(1,k/crossfade))))
            count+=1
    finally:
        for writer in writers.values():writer.close()
    assert count==450
    for name in paths:temp[name].replace(paths[name])
    times=[1.5,4.5,7.5,10.5,12.75,14.6]
    sheet=Image.new('RGB',(1620,850),'white'); d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(BOLD,20)
    d.text((12,8),'9:16 · 인코딩 영상에서 추출',font=font,fill='#202020')
    d.text((12,540),'1:1 · 전체 장면 유지, 자막 별도 배치',font=font,fill='#202020')
    qa={'request':101,'type':'AI stills with local pan/zoom/crossfade, not generated-motion footage',
        'fps':FPS,'expected_frames':450,'duration_seconds':15.0,'audio':'none',
        'sources':[s[2] for s in SCENES],'caption_bounds':CHECKS,'outputs':{},
        'note':'Local creative preview only. Label main words visually checked; original-print pixel identity not guaranteed.'}
    for name in paths:
        reader=imageio.get_reader(str(paths[name]))
        try:
            meta=reader.get_meta_data(); actual=reader.count_frames()
            assert actual==450,(name,actual)
            assert tuple(meta['size'])==((1080,1920) if name=='9x16' else (1080,1080))
            assert abs(meta['duration']-15)<.05
            for i,t in enumerate(times):
                fr=Image.fromarray(reader.get_data(int(t*FPS)))
                size=(270,480) if name=='9x16' else (270,270)
                sheet.paste(fr.resize(size,R.LANCZOS),(i*270,48 if name=='9x16' else 580))
                d.text((i*270+10,28 if name=='9x16' else 560),f'{t:.2f}s',font=font,fill='#404040')
            qa['outputs'][name]={'file':str(paths[name].relative_to(ROOT)).replace('\\','/'),
              'dimensions':list(meta['size']),'duration':meta['duration'],'decoded_frames':actual,'bytes':paths[name].stat().st_size}
        finally:reader.close()
    sheet.save(RESULT/'juice_video_15s_contact_2026-11-04.png')
    (RESULT/'juice_video_qa_2026-11-04.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Complete: 450 frames, 15 seconds, portrait/square, caption bounds passed.',flush=True)

if __name__=='__main__':main()
