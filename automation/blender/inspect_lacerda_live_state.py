"""Diagnóstico read-only da B82 e captura GPU da vista atual, sem salvar cena."""
import bpy,json,runpy,math,os,struct,zlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/reports/blender/lacerda-live-diagnostic';OUT.mkdir(parents=True,exist_ok=True)
sig=runpy.run_path(str(ROOT/'automation/blender/component_fingerprint.py'))['signature']
before=json.loads((ROOT/'docs/reports/blender/lacerda-gameplay-proxy/protected_original_components.json').read_text(encoding='utf8'))
changed=[];missing=[]
for name,value in before.items():
    ob=bpy.data.objects.get(name)
    if ob is None:missing.append(name);continue
    try:actual=sig(ob)
    except RuntimeError:actual={'type':ob.type,'basis':[list(r) for r in ob.matrix_basis],'data':ob.data.name if ob.data else None}
    if actual!=value:changed.append({'object':name,'changed_fields':[k for k in set(actual)|set(value) if actual.get(k)!=value.get(k)]})
cfg=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))
col=bpy.data.collections.get('GAMEPLAY_PROXY | Lacerda B82');ids={o.get('boas_proxy_id'):o for o in col.objects} if col else {}
a=cfg['local_frame']['angle'];c,s=math.cos(a),math.sin(a);origin=cfg['local_frame']['origin_xy'];errors=[]
for row in cfg['obstacles']:
    ob=ids.get(row['id'])
    if ob is None:errors.append({'id':row['id'],'missing':True});continue
    p=row['center'];expected=Vector((origin[0]+c*p[0]-s*p[1],origin[1]+s*p[0]+c*p[1],p[2]))
    delta=(ob.matrix_world.translation-expected).length;size=max(abs(ob.dimensions[i]-row['size'][i]) for i in range(3))
    if delta>1e-4 or size>1e-4:errors.append({'object':ob.name,'position_error':delta,'size_error':size})
op=bpy.app.driver_namespace.get('boas_proxy_operator');state=None
if op:
    try:state={'finished':op.finished,'mode':op.controller.mode,'car_z':op.controller.car_z,'station':op.controller.station,'openness':op.controller.openness,'player':op.controller.player,'keys':sorted(op.keys)}
    except (ReferenceError,AttributeError) as exc:state={'error':str(exc)}
rows=[]
for ob in bpy.context.scene.objects:
    if ob.get('boas_proxy_dynamic') or ob.name in {'SUPERIOR | piso saguão','INFERIOR | piso do saguão','CALIBRADO | passarela piso 28.71 x 6.00m'}:
        rows.append({'object':ob.name,'location':list(ob.matrix_world.translation),'visible':ob.visible_get(),'hidden':ob.hide_get(),'role':ob.get('boas_proxy_dynamic')})
report={'file':bpy.data.filepath,'scene':bpy.context.scene.name,'pid':os.getpid(),'dirty':bpy.data.is_dirty,'frame':bpy.context.scene.frame_current,'historical_changed':changed,'historical_missing':missing,'static_proxy_errors':errors,'proxy_count':len(ids),'controller':state,'objects':rows,'scene_changed_by_diagnostic':False}
try:
    import gpu
    area=next(ar for ar in bpy.context.window.screen.areas if ar.type=='VIEW_3D');space=area.spaces.active;region=next(r for r in area.regions if r.type=='WINDOW')
    report['viewport']={'shading':space.shading.type,'perspective':space.region_3d.view_perspective,'local_view':bool(space.local_view),'view_location':list(space.region_3d.view_location),'view_distance':space.region_3d.view_distance}
    width,height=1000,650;off=gpu.types.GPUOffScreen(width,height)
    try:
        with bpy.context.temp_override(window=bpy.context.window,area=area,region=region):
            off.draw_view3d(bpy.context.scene,bpy.context.view_layer,space,region,space.region_3d.view_matrix,space.region_3d.window_matrix,do_color_management=True)
            with off.bind():pixels=gpu.state.active_framebuffer_get().read_color(0,0,width,height,4,0,'UBYTE')
        pixels.dimensions=width*height*4;raw=bytes(pixels)
        def chunk(tag,data):return struct.pack('!I',len(data))+tag+data+struct.pack('!I',zlib.crc32(tag+data)&0xffffffff)
        scan=b''.join(b'\0'+raw[y*width*4:(y+1)*width*4] for y in reversed(range(height)))
        png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b'')
        target=ROOT/'artifacts/lacerda-live-diagnostic/current-viewport.png';target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(png);report['screenshot']=str(target)
    finally:off.free()
except Exception as exc:report['capture_error']=str(exc)
(OUT/'current.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
