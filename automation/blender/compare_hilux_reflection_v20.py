import bpy,runpy
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene;o=s.objects['HILUX | CARROCERIA PRINCIPAL']
assert not bpy.app.background and Path(bpy.data.filepath).name=='hilux_chapa_v20.blend'
m=o.modifiers['V20 | Normais da chapa por area e angulo'];a,b=m.show_viewport,m.show_render
src=(r/'automation/blender/review_hilux_chapa_v20.py').read_text(encoding='utf8')
src=src.replace("('traseira',(3.5,6,3.65),(0,.72,1.50),2.6,'STUDIO','paint.sl'),",'').replace("('frente',(7,-8,3.7),(0,-.9,1.16),4.3,'STUDIO','paint.sl'),",'')
src=src.replace('v20-{name}.png','v20-sem-ponderacao-{name}.png')
try:
 m.show_viewport=False;m.show_render=False
 exec(compile(src,str(r/'automation/blender/review_hilux_chapa_v20.py'),'exec'),globals())
finally:m.show_viewport=a;m.show_render=b
