"""Extrai vetores documentais; coordenadas PDF não são medidas reais ou SSOT."""
import json,argparse
from pathlib import Path
import pdfplumber

root=Path(__file__).resolve().parents[2]
out=root/'artifacts/lacerda-proportions'
parser=argparse.ArgumentParser();parser.add_argument('--sheets',type=int,nargs='+',default=[12,17]);args=parser.parse_args()
for sheet in args.sheets:
    source=root/f'world-reference/mvp-centro-lacerda/research-20261006-issue22/sucop-architectural-{sheet}.pdf'
    with pdfplumber.open(source) as pdf:
        page=pdf.pages[0]
        rows=[]
        for kind,items in [('curve',page.curves),('line',page.lines),('rect',page.rects)]:
            for i,item in enumerate(items):
                pts=item.get('pts') or [(item['x0'],item['top']),(item['x1'],item['bottom'])]
                rows.append({'kind':kind,'index':i,'bbox':[item['x0'],item['top'],item['x1'],item['bottom']],
                    'points':pts,'stroke':item.get('stroking_color'),'fill_color':item.get('non_stroking_color'),
                    'fill':item.get('fill'),'linewidth':item.get('linewidth')})
        (out/f'sheet{sheet}-vectors.json').write_text(json.dumps({'size':[page.width,page.height],'items':rows}),encoding='utf8')
        selected=[r for r in rows if r['kind']=='curve' and r['fill'] and r['bbox'][2]-r['bbox'][0]>45 and r['bbox'][3]-r['bbox'][1]>45]
        print(json.dumps({'sheet':sheet,'size':[page.width,page.height],'filled_contours':[{k:r[k] for k in ('index','bbox','fill_color')} for r in selected]},ensure_ascii=False))
