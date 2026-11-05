"""Readable engineering plates from real 3D projections, not invented imagery."""
from pathlib import Path
import json,textwrap,re
from PIL import Image,ImageDraw,ImageFont

FONT='/usr/share/fonts/truetype/Roboto-Regular.ttf'
BOLD='/usr/share/fonts/truetype/Roboto-Bold.ttf'
NAVY='#183E4C';TEAL='#197F82';MUTED='#526B73';LIGHT='#E8EDEB'


def display_text(text):
    text=re.sub(r'(?<=[a-z])(?=\d)',' ',str(text))
    text=re.sub(r'(?<=\d)(mm|km|kg|kN|MJ|m|t)\b',r' \1',text)
    text=re.sub(r'(?<= )m ?3\b','m³',text)
    return re.sub(r'\s+/\s*',' / ',text)


def plate(assembly,render_dir,output):
    render_dir=Path(render_dir);record=json.loads((render_dir/'render.json').read_bytes())
    raw=Image.open(render_dir/'raw.png').convert('RGBA')
    image=Image.alpha_composite(Image.new('RGBA',raw.size,'#F6F8F6'),raw).convert('RGB');w,h=image.size;scale=w/3000
    draw=ImageDraw.Draw(image)
    font=lambda size,bold=False:ImageFont.truetype(BOLD if bold else FONT,max(10,round(size*scale)))
    draw.rectangle((0,0,w,round(242*scale)),fill='#F6F8F6')
    draw.text((round(72*scale),round(38*scale)),'OPENSOURCERAIL  /  ENGINEERING MODELS',font=font(29,True),fill=TEAL)
    title=assembly['title'];size=69
    while draw.textlength(title,font=font(size,True))>w-144*scale and size>42:size-=2
    draw.text((round(72*scale),round(91*scale)),title,font=font(size,True),fill=NAVY)
    subtitle=display_text(assembly.get('subtitle','Source dimensions and declared layout assumptions'))
    for i,line in enumerate(textwrap.wrap(subtitle,110)[:2]):
        draw.text((round(75*scale),round((175+38*i)*scale)),line,font=font(32),fill=MUTED)
    labels=record.get('labels',[])
    for side in ('left','right'):
        rows=[r for r in labels if r.get('side', 'left' if r['pixel'][0]<w/2 else 'right')==side]
        rows.sort(key=lambda r:r['pixel'][1])
        for i,row in enumerate(rows):
            cy=(380+(h/scale-680)*(i+.5)/max(1,len(rows)))*scale
            lines=textwrap.wrap(display_text(row['text']),27);boxw=455*scale;boxh=(38*len(lines)+42)*scale
            x=46*scale if side=='left' else w-46*scale-boxw;y=cy-boxh/2
            anchor=(max(8,min(w-8,row['pixel'][0])),max(255*scale,min(h-145*scale,row['pixel'][1])))
            edge=x+boxw if side=='left' else x
            elbow=edge+(38*scale if side=='left' else -38*scale)
            draw.line((anchor,(elbow,anchor[1]),(elbow,cy),(edge,cy)),fill=TEAL,width=max(1,round(2*scale)))
            r=5*scale;draw.ellipse((anchor[0]-r,anchor[1]-r,anchor[0]+r,anchor[1]+r),fill=TEAL)
            draw.rounded_rectangle((x,y,x+boxw,y+boxh),radius=10*scale,fill='#F7FAF8',outline='#CFDCD7',width=max(1,round(scale)))
            for j,line in enumerate(lines):draw.text((x+20*scale,y+(18+38*j)*scale),line,font=font(32,True),fill=NAVY)
    footer=h-104*scale
    draw.rectangle((0,footer,w,h),fill=NAVY)
    draw.text((70*scale,footer+20*scale),'SOURCE-BASED GEOMETRY  +  DECLARED PROPOSALS',font=font(27,True),fill='#FFFFFF')
    draw.text((70*scale,footer+58*scale),'Outline communication model  |  Physical validation and manufacturing detail remain open',font=font(24),fill='#C5DAD9')
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True);image.save(out,format='WEBP',quality=92,method=6)
    return dict(width=w,height=h,labels=len(labels),format='WebP',quality=92)
