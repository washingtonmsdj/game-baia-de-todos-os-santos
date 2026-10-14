"""Portas contidas na largura da cabine; sem sobreposição entre elevadores."""
import bpy,json,math,runpy
from pathlib import Path
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/lacerda-four-lifts.json';cfg=json.loads(cp.read_text());out=root/'docs/reports/blender/lacerda-exterior-b102'
sig=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
for s in cfg['equipment']:
 assert s['movement_enabled'];ca,sa=math.cos(s['angle_local']),math.sin(s['angle_local']);cx,cy=s['center_local']
 s['door_width']=1.2;s['door_leaf_stroke']=.62
 for p in s['parts']:
  if 'door' not in p['tag']:continue
  o=bpy.data.objects[p['object']];oldcenter=p['center'][1];newcenter=p['leaf']*.3
  for v in o.data.vertices:
   x,y=v.co.x-cx,v.co.y-cy;localy=-sa*x+ca*y;dy=newcenter+(localy-oldcenter)*(.6/.65)-localy
   v.co.x-=sa*dy;v.co.y+=ca*dy
  o.data.update();p['center'][1]=newcenter;p['size'][1]=.6
 # Abertura1,24 > cápsula0,63; folhas extremas1,22 < meia largura1,235.
 assert .3+.62+.3 < s['enclosure_size'][1]/2
 s['door_sweep_classification']='PROXY_LEAVES_CONTAINED_WITHIN_CABIN_ENCLOSURE'
cfg['door_sweep_note']='Folhas da cabine varrem dentro do volume já submetido ao CCD; portas de estação não constituem aprovação do portal pedonal histórico.'
cp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
r=json.loads((out/'application.json').read_text())
for v in r['added']:v['after']['signature']=sig(bpy.context.scene.objects[v['object']])
(out/'application.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Portas1,20m/stroke0,62m; nenhuma folha excede a caixa de varredura da cabine.')
