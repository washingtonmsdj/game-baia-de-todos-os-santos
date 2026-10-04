"""Conferência após reabertura e playback observável da câmera interna."""
import bpy,json,hashlib,os,time,numpy as np
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
rp=r/'docs/reports/blender/rondesp_driver_review_b39.json';report=json.loads(rp.read_text(encoding='utf8'))
assert Path(bpy.data.filepath).resolve()==(r/report['source_after']['file']).resolve()
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==report['source_after']['sha256']
assert hashlib.sha256((r/report['source_before']['file']).read_bytes()).hexdigest()==report['source_before']['sha256']
assert hashlib.sha256((r/report['vehicle']['file']).read_bytes()).hexdigest()==report['vehicle']['sha256']
c=json.loads((r/'world/areas/mvp-centro-lacerda/production.json').read_text(encoding='utf8'))
proxy=s.objects[c['export']['terrain_proxy']];me=proxy.data;me.calc_loop_triangles()
a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a);xyz=a.reshape(-1,3).astype(np.float64)
a=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',a);tri=a.reshape(-1,3)
areas=np.linalg.norm(np.cross(xyz[tri[:,1]]-xyz[tri[:,0]],xyz[tri[:,2]]-xyz[tri[:,0]]),axis=1)*.5
finite=bool(np.isfinite(xyz).all());degenerate=int(np.count_nonzero(areas<1e-9))
assert finite and degenerate==0,'Colisor com geometria degenerada'
assert s.camera.name=='QA | RONDESP | camera motorista'
actor=s.objects['QA | RONDESP | veiculo na pista'];assert s.camera.parent==actor
report['source_reopened']=True;report['source_sha256_after_reopen']=report['source_after']['sha256']
report['proxy_mesh_validation']={'vertices':len(me.vertices),'polygons':len(me.polygons),'finite':finite,'degenerate_triangles':degenerate}
report['library_paths']=[lib.filepath for lib in bpy.data.libraries]
report['turn_audit']='docs/reports/blender/rondesp_turn_audit.json'
report['driver_view_review']='reviewed: Montanha, Conceição, Chile, Carlos Gomes, Castro Rabelo, Lafayete Coutinho, via sem nome e Ruy Barbosa; visibilidade interna confirmada, cidade ainda candidata.'
report['pending']=['Não há aprovação AAA ou de todos os circuitos','54 curvas com raio e 16 com apoio em revisão; critérios candidatos','Nós sem binding ou pista e apoios/colisor pendentes','Varredura volumétrica de obstáculos e curva contínua','Física, tráfego e performance em runtime; sentidos inversos completos']
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# A temporary timer demonstrates real frame updates, without saving or new scene edits.
start=s.frame_start;end=s.frame_end;began=time.monotonic();samples=[]
def observe():
    elapsed=time.monotonic()-began;frame=min(end,start+round(elapsed*24));s.frame_set(frame)
    samples.append({'frame':frame,'location':list(actor.matrix_world.translation)})
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':area.tag_redraw()
    if elapsed<12 and frame<end:return .5
    moved=any(a['location']!=samples[0]['location'] for a in samples[1:])
    report['visible_driver_playback']={'samples':len(samples),'movement_observed':moved,'wall_seconds':elapsed,'frames_observed':[p['frame'] for p in samples],'dynamic_physics':False}
    rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    s.frame_set(start)
    return None
bpy.app.timers.register(observe,first_interval=.5)
print(json.dumps({'reopened':True,'proxy_mesh_validation':report['proxy_mesh_validation'],'visible_playback_started':True,'pid':os.getpid()}))