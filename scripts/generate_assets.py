#!/usr/bin/env python3
"""Create self-hosted monochrome GitHub profile artwork.
Run: python -m pip install Pillow && python scripts/generate_assets.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import math, html, re, os
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT/'assets'
ASSETS.mkdir(parents=True,exist_ok=True)
PHOTO = ASSETS/'portrait.jpg'
W,H = 1120,380
BG=(245,243,239); PAPER=(252,251,248); INK=(24,24,24); MUTED=(100,100,98); LINE=(215,211,205); SOFT=(231,228,221)
# Cross-platform fonts: use installed system fonts. Never require Linux paths
# or distribute proprietary fonts with the README source archive.
@lru_cache(maxsize=40)
def _load_font(style: str, size: int):
    windows_fonts = Path(os.environ.get('WINDIR', r'C:\Windows')) / 'Fonts'
    inter_fonts = Path('/usr/share/fonts/opentype/inter')
    linux_fonts = Path('/usr/share/fonts/truetype/dejavu')
    mac_fonts = Path('/System/Library/Fonts/Supplemental')
    if style == 'mono':
        candidates = [
            os.environ.get('PROFILE_README_MONO_FONT'),
            windows_fonts / 'consola.ttf',
            windows_fonts / 'cour.ttf',
            linux_fonts / 'DejaVuSansMono.ttf',
            mac_fonts / 'Menlo.ttc',
            mac_fonts / 'Courier New.ttf',
            'DejaVuSansMono.ttf',
        ]
    else:
        bold = style == 'Bold'
        candidates = [
            os.environ.get('PROFILE_README_FONT'),
            inter_fonts / f'InterDisplay-{style}.otf',
            windows_fonts / ('arialbd.ttf' if bold else 'arial.ttf'),
            windows_fonts / ('segoeuib.ttf' if bold else 'segoeui.ttf'),
            windows_fonts / ('calibrib.ttf' if bold else 'calibri.ttf'),
            mac_fonts / ('Arial Bold.ttf' if bold else 'Arial.ttf'),
            linux_fonts / ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'),
            'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',
        ]
    for item in candidates:
        if not item:
            continue
        try:
            return ImageFont.truetype(str(item), size)
        except (OSError, ValueError):
            continue
    # Pillow's bundled fallback works without additional font installations.
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Older Pillow versions
        return ImageFont.load_default()

def font(name, size):
    return _load_font(name, size)

def monofont(size):
    return _load_font('mono', size)

if PHOTO.exists():
    src = Image.open(PHOTO).convert('RGB')
    avatar=ImageOps.fit(src,(244,244),method=Image.Resampling.LANCZOS,centering=(.5,.31))
    mask=Image.new('L',(244,244));md=ImageDraw.Draw(mask);md.ellipse((0,0,243,243),fill=255)
    avatar_rgba=Image.new('RGBA',(244,244),(255,255,255,0));avatar_rgba.paste(avatar,(0,0),mask)
    avatar_rgba.save(ASSETS/'portrait-circle.png', optimize=True)
else:
    avatar_rgba=Image.open(ASSETS/'portrait-circle.png').convert('RGBA')

F_BOLD=font('Bold',110); F_NAME=font('Medium',47); F_MED=font('Medium',20)
F_SMALL=monofont(13); F_TINY=monofont(12); F_LABEL=font('Medium',17)

def base():
    image=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(image)
    d.rounded_rectangle((2,2,W-3,H-3),radius=26,outline=LINE,width=2)
    # understated graphical frame
    for i in range(28):
        for j in range(6):
            px=750+i*10;py=20+j*10
            if px<1110:d.ellipse((px,py,px+1,py+1),fill=LINE)
    # ornamental circle under the subject
    d.ellipse((824,48,1110,334),outline=LINE,width=2)
    d.ellipse((836,60,1098,322),outline=SOFT,width=2)
    d.arc((802,26,1132,356),14,115,fill=(172,168,159),width=2)
    d.arc((802,26,1132,356),190,310,fill=(172,168,159),width=2)
    d.rounded_rectangle((31,22,86,77),radius=28,fill=INK)
    bb=d.textbbox((0,0),'SS',font=font('Bold',18)); tw=bb[2]-bb[0]
    d.text((58-tw/2,40),'SS',font=font('Bold',18),fill=(255,255,255))
    d.text((103,33),'PROFILE   /   2026 EDITION',font=F_SMALL,fill=MUTED)
    d.text((1075,33),'BHUBANESWAR, INDIA',font=F_TINY,anchor='ra',fill=MUTED)
    d.line((50,96,1070,96),fill=LINE,width=2)
    # main content
    d.text((60,104),'SURAJ',font=F_BOLD,fill=INK)
    d.text((66,221),'KUMAR SUBUDHI',font=F_NAME,fill=INK)
    d.text((69,283),'PYTHON DEVELOPER  /  AI & FULL-STACK',font=F_LABEL,fill=(92,91,87))
    d.line((66,341,1068,341),fill=LINE,width=2)
    # avatar with single photo and outlines
    image.paste(avatar_rgba,(847,68),avatar_rgba)
    d.ellipse((845,66,1093,314),outline=INK,width=3)
    d.ellipse((849,70,1089,310),outline=SOFT,width=2)
    return image

phrases=['APPLIED MACHINE LEARNING', 'PRODUCTION-GRADE BACKENDS', 'THOUGHTFUL FULL-STACK APPS']
frames=[]
raw_frames=[]
num=48
for i in range(num):
    im=base(); d=ImageDraw.Draw(im)
    t=i/num
    idx=min(2,int(t*3))
    within=t*3-idx
    # short pause at completed message
    text=phrases[idx];n=max(0,min(len(text),int((within/.72)*len(text))))
    if within>.72:n=len(text)
    d.text((70,354),text[:n],font=F_TINY,fill=MUTED)
    if (i//4)%2==0:
        prefix=d.textbbox((0,0),text[:n],font=F_TINY)[2]
        d.rectangle((74+prefix,354,76+prefix,369),fill=INK)
    # progress bar tracks one full loop
    progress=int(998*(i+1)/num)
    d.line((69,371,69+progress,371),fill=INK,width=3)
    # moving marker on portrait outer circle
    a=2*math.pi*i/num
    x=969+144*math.cos(a);y=190+144*math.sin(a)
    d.ellipse((x-5,y-5,x+5,y+5),fill=INK)
    # darker secondary geometric marks in hero
    d.rectangle((755,150,757,260),fill=SOFT)
    d.ellipse((750,150,762,162),outline=MUTED,width=1)
    # palette optimize (for consistent photo color across frames)
    raw_frames.append(im)
    frames.append(im.quantize(colors=96, method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE))
frames[0].save(ASSETS/'hero.gif',save_all=True,append_images=frames[1:],duration=105,loop=0,optimize=True,disposal=2)
raw_frames[0].save(ASSETS/'hero.webp',format='WEBP',save_all=True,append_images=raw_frames[1:],duration=105,loop=0,quality=86,method=5)
base().save(ASSETS/'hero-poster.png',optimize=True)

# SVG components are self-contained; no CSS/JS from hosting site needed.
def svg(name,w,h,content):
    out=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(name)}">\n{content}\n</svg>'
    (ASSETS/name).write_text(out,encoding='utf-8')

def esc(x):return html.escape(x,quote=True)

# Four project preview cards. Embedded text is legible, even without loading remote icons.
projects=[
    ('01','AI Interview Web App','AI-POWERED INTERVIEW PREP','Role-specific questions, voice feedback,','and Gemini-powered evaluation.','NEXT.JS  /  REACT  /  GEMINI'),
    ('02','ResolverAI','CONVERSATIONAL AI','A responsive AI conversation interface','built with Gemini and React.','REACT  /  VITE  /  TAILWIND'),
    ('03','Any Video Downloader','FULL-STACK UTILITY','A web utility for supported video links,','validation, and backend logging.','REACT  /  NODE.JS  /  MONGODB'),
    ('04','Personal Portfolio','INTERACTIVE PERSONAL WEBSITE','A motion-conscious, responsive portfolio','built with Next.js and TypeScript.','NEXT.JS  /  TYPESCRIPT  /  CSS'),
]
for n,title,kicker,line1,line2,tech in projects:
    # all cards same 534 x 212
    cw,ch=534,212
    safe=re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')
    lines=[
        '<rect x="1.5" y="1.5" width="531" height="209" rx="21" fill="#f4f2ee" stroke="#d4d0c9" stroke-width="2"/>',
        '<circle cx="38" cy="36" r="15" fill="#1b1b1b"/>',
        f'<text x="38" y="41" text-anchor="middle" fill="white" font-size="12" font-weight="700" font-family="Arial, sans-serif">{n}</text>',
        f'<text x="64" y="41" fill="#77756f" font-family="monospace" font-size="10" letter-spacing="1.5">{esc(kicker)}</text>',
        f'<text x="27" y="97" fill="#171717" font-family="Arial, Helvetica, sans-serif" font-size="31" font-weight="700" letter-spacing="-1">{esc(title)}</text>',
        f'<text x="27" y="132" fill="#5a5956" font-family="Arial, sans-serif" font-size="16">{esc(line1)}</text>',
        f'<text x="27" y="153" fill="#5a5956" font-family="Arial, sans-serif" font-size="16">{esc(line2)}</text>',
        '<line x1="27" y1="174" x2="506" y2="174" stroke="#d4d0c9"/>',
        f'<text x="27" y="195" fill="#77756f" font-family="monospace" font-size="11">{esc(tech)}</text>',
        f'<path d="M477 40 L495 22 M484 22 H495 V33" stroke="#171717" stroke-width="2" fill="none" stroke-linecap="round"><animateTransform attributeName="transform" type="translate" values="0 0;3 -3;0 0" dur="4s" begin="{int(n)*0.25}s" repeatCount="indefinite"/></path>'
    ]
    svg(f'project-{n}.svg',cw,ch,'\n'.join(lines))

# Designed modular stack grid
families=[
  ('LANGUAGES', ['Python','JavaScript','Java','SQL']),
  ('FRONTEND', ['React','Next.js','TypeScript','Tailwind CSS']),
  ('BACKEND & DATA', ['Django','Node.js','Express.js','MongoDB','MySQL','Redis']),
  ('AI, CLOUD & DEVOPS', ['CatBoost','TensorFlow','NLP','Azure','Docker','Git / CI/CD']),
]
width=1100; hgt=428
l=['<rect x="1" y="1" width="1098" height="426" rx="24" fill="#f4f2ee" stroke="#d4d0c9" stroke-width="2"/>',
  '<text x="32" y="43" font-family="monospace" font-size="13" fill="#77756f" letter-spacing="1.6">MY TOOLKIT / PRACTICAL TECH</text>',
  '<line x1="32" y1="57" x2="1068" y2="57" stroke="#d4d0c9"/>']
for row,(label,vals) in enumerate(families):
    yy=82+row*86
    l.append(f'<text x="34" y="{yy+29}" font-family="monospace" font-size="13" fill="#696864">{esc(label)}</text>')
    x=285
    for skill in vals:
        sw=min(165,max(91,32+len(skill)*9))
        l.append(f'<rect x="{x}" y="{yy}" width="{sw}" height="49" rx="13" fill="#fdfcf9" stroke="#d6d2ca"/>')
        l.append(f'<text x="{x+sw/2:.1f}" y="{yy+31}" font-family="Arial, sans-serif" font-size="16" font-weight="600" text-anchor="middle" fill="#252525">{esc(skill)}</text>')
        x+=sw+11
svg('stack.svg',1100,428,'\n'.join(l))

# Centered monochrome link badges used as UI-like controls, not real CSS buttons
for short,label in [('mail','EMAIL ME'),('linkedin','LINKEDIN'),('portfolio','VISIT PORTFOLIO')]:
    widths={'mail':224,'linkedin':224,'portfolio':268}
    ww=widths[short]
    content='\n'.join([
      f'<rect x="1.5" y="1.5" width="{ww-3}" height="54" rx="27" fill="{INK and "#171717" if short=="mail" else "#f4f2ee"}" stroke="#171717" stroke-width="2"/>',
      f'<text x="{ww/2-8:.1f}" y="35" text-anchor="middle" font-size="14" font-family="Arial, sans-serif" font-weight="700" letter-spacing="1.5" fill="{"#ffffff" if short=="mail" else "#171717"}">{label}</text>',
      f'<path d="M{ww-44} 29 h13 m-6 -6 6 6 -6 6" fill="none" stroke="{"#ffffff" if short=="mail" else "#171717"}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    ])
    svg(f'btn-{short}.svg',ww,57,content)

# footer with subtle animated line in SVG; no JS
svg('footer.svg',1100,124,'\n'.join([
  '<rect x="1" y="1" width="1098" height="122" rx="21" fill="#f4f2ee" stroke="#d4d0c9" stroke-width="2"/>',
  '<text x="31" y="36" font-family="monospace" font-size="12" fill="#77756f" letter-spacing="2">THE NEXT BUILD STARTS WITH A CONVERSATION</text>',
  '<text x="31" y="90" font-family="Arial, sans-serif" font-size="42" font-weight="700" fill="#171717" letter-spacing="-1.5">Let\'s build something useful.</text>',
  '<path d="M974 64 L1057 64 M1037 46 L1057 64 L1037 82" stroke="#171717" stroke-width="3" fill="none"/>',
  '<circle cx="974" cy="64" r="5" fill="#171717"><animate attributeName="cx" values="954;1008;954" dur="4s" repeatCount="indefinite"/></circle>'
]))

# Compose responsive 2x2 and 1x4 project galleries from the original cards.
from xml.etree import ElementTree as ET
from copy import deepcopy
for mode in ('desktop','mobile'):
    desktop=(mode=='desktop')
    sw,sh=(1100,462) if desktop else (554,904)
    root=ET.Element('{http://www.w3.org/2000/svg}svg',{
        'width':str(sw),'height':str(sh),'viewBox':f'0 0 {sw} {sh}',
        'role':'img','aria-label':'Four selected project cards'
    })
    for idx in range(4):
        card=ET.parse(ASSETS/f'project-0{idx+1}.svg').getroot()
        xx,yy=((16+(idx%2)*550,10+(idx//2)*225) if desktop else (10,10+idx*222))
        sub=ET.SubElement(root,'{http://www.w3.org/2000/svg}svg',{
            'x':str(xx),'y':str(yy),'width':'534','height':'212','viewBox':'0 0 534 212'
        })
        for node in card:sub.append(deepcopy(node))
    ET.ElementTree(root).write(ASSETS/f'projects-{mode}.svg',encoding='unicode',xml_declaration=False)

# Mobile-specific, vertically stacked technology diagram for readable labels.
mob=['<rect x="1" y="1" width="598" height="886" rx="25" fill="#f4f2ee" stroke="#d4d0c9" stroke-width="2"/>',
     '<text x="28" y="43" font-family="monospace" font-size="19" fill="#77756f">MY TOOLKIT / PRACTICAL TECH</text>',
     '<line x1="28" y1="59" x2="572" y2="59" stroke="#d4d0c9"/>']
cy=88
for label, vals in families:
    mob.append(f'<text x="28" y="{cy+16}" font-family="monospace" font-size="18" letter-spacing="1" fill="#77756f">{esc(label)}</text>')
    cy+=31
    for idx, value in enumerate(vals):
        column=idx%2;row=idx//2
        xx=28+column*277;yy=cy+row*53
        mob.append(f'<rect x="{xx}" y="{yy}" width="265" height="43" rx="11" fill="#fdfcf9" stroke="#d6d2ca"/>')
        mob.append(f'<text x="{xx+132.5}" y="{yy+28}" font-family="Arial,sans-serif" font-size="20" font-weight="600" fill="#252525" text-anchor="middle">{esc(value)}</text>')
    cy+=(math.ceil(len(vals)/2))*53+28
svg('stack-mobile.svg',600,888,'\n'.join(mob))

print('Created:')
for p in sorted(ASSETS.iterdir()):print(p.name, p.stat().st_size)
