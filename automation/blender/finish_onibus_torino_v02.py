import bpy, math
from pathlib import Path
scene=bpy.context.scene
assert 'Integra 31065' in scene.name
scene.name='ONIBUS | Torino 31065 v02'
def fy(x,z):
    return -6.04+.24*(abs(x)/1.25)**4+max(0,z-1.35)*.125+max(0,.7-z)*.14
for o in list(scene.objects):
    if o.name.startswith(('BUS02 | Grade motor fundo','BUS02 | Aleta motor')) and o.location.x<0:
        bpy.data.objects.remove(o,do_unlink=True)
        continue
    if o.type=='FONT' and o.location.y < -5.8:
        o.location.y=fy(o.location.x,o.location.z)-.085
    if o.name.startswith('BUS02 | Entrada ar frontal'):
        o.location.y=-6.07
    if o.type=='CURVE' and o.name.startswith(('BUS02 | Braco limpador','BUS02 | Palheta')):
        for sp in o.data.splines:
            for p in sp.points:p.co.y=fy(p.co.x,p.co.z)-.11
scene.frame_set(1)
scene['asset_notes']='Revisão Torino 31065 conforme concept do usuário. Três portas transferidas para -X, teto curvo, amarelo/branco, interior em esboço e plataforma conceitual. Medidas aproximadas, não medidas. Sem testes/builds. Integração em engine pendente.'
out=Path(bpy.data.filepath).parent/'assets'/'onibus_torino_31065_v02.blend'
bpy.data.libraries.write(str(out),{scene},fake_user=True,compress=True)
scene.render.resolution_x=1400
scene.render.resolution_y=900
scene.render.resolution_percentage=100
scene.render.filepath=str(out.with_suffix('.png'))
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        region=next(r for r in area.regions if r.type=='WINDOW')
        with bpy.context.temp_override(area=area,region=region):
            bpy.ops.render.opengl(write_still=True,view_context=True)
        break
print(str(out))
