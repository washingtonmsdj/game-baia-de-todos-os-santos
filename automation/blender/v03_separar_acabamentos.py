import bpy
from pathlib import Path
s=bpy.context.scene
def base(x,z,end):
    t=.20*(abs(x)/1.25)**4
    return -6.05+t+.13*max(0,z-1.30) if end<0 else 6.045-t-.045*max(0,z-2.25)
for o in s.objects:
    if not o.name.startswith('BUS03 | '):continue
    if any(t in o.name for t in ['carenagem continua','retorno lateral','uniao teto']):continue
    if o.type=='MESH':
        for v in o.data.vertices:
            end=1 if v.co.y>0 else -1;b=base(v.co.x,v.co.z,end);v.co.y=b+(v.co.y-b)*3
    elif o.type=='CURVE':
        for sp in o.data.splines:
            for p in sp.points:
                end=1 if p.co.y>0 else -1;b=base(p.co.x,p.co.z,end);p.co.y=b+(p.co.y-b)*3
    elif o.type=='FONT':
        end=1 if o.location.y>0 else -1;b=base(o.location.x,o.location.z,end);o.location.y=b+(o.location.y-b)*3
bpy.data.libraries.write(str(Path(bpy.data.filepath).parent/'assets'/'onibus_torino_31065_v03.blend'),{s},fake_user=True,compress=True)
