"""Consistent, readable plates around untouched native render pixels."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont

REGULAR='/usr/share/fonts/truetype/Roboto-Regular.ttf'
BOLD='/usr/share/fonts/truetype/Roboto-Bold.ttf'


def plate(raw,output,*,title,subtitle,footer,width=3000,height=1900):
    source=Image.open(raw).convert('RGBA')
    canvas=Image.new('RGB',(width,height),'#f5f7f9');draw=ImageDraw.Draw(canvas)
    ratio=width/3000
    font=lambda size,bold=False:ImageFont.truetype(BOLD if bold else REGULAR,round(size*ratio))
    # Fit without stretching or cropping the actual CAD/numerical image.
    top=round(235*ratio);bottom=round(130*ratio);margin=round(55*ratio)
    area=(width-2*margin,height-top-bottom)
    source.thumbnail(area,Image.Resampling.LANCZOS)
    at=(round((width-source.width)/2),top+round((area[1]-source.height)/2))
    canvas.paste(source,at,source)
    draw.text((margin,round(32*ratio)),'OPENSOURCERAIL · CAD & ENGINEERING',font=font(34,True),fill='#087e8b')
    size=70
    while draw.textlength(title,font=font(size,True))>width-2*margin and size>40:size-=2
    draw.text((margin,round(88*ratio)),title,font=font(size,True),fill='#122d40')
    draw.text((margin,round(177*ratio)),subtitle,font=font(34),fill='#465a6b')
    draw.line((margin,height-bottom,width-margin,height-bottom),fill='#cbd7df',width=max(1,round(2*ratio)))
    draw.text((margin,height-round(99*ratio)),footer,font=font(31,True),fill='#122d40')
    draw.text((margin,height-round(50*ratio)),'Research model · physical validation and manufacturing release remain open',font=font(27),fill='#607487')
    target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(target,format='WEBP',quality=94,method=6)
    return dict(size=[width,height],source_size=list(Image.open(raw).size),image_fit='contain; no crop or stretch',display_image_rect=[*at,source.width,source.height])
