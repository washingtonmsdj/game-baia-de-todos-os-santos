"""Refinar recorte inferior e normais da fonte na biblioteca, pelo MCP visível."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];path=root/'docs/reports/blender/cidade_baixa_r30b31.json';report=json.loads(path.read_text(encoding='utf8'));scene=bpy.context.scene
instance=scene.objects['MARIO CRAVO | Fonte da Rampa do Mercado'];original=instance.instance_collection;library=original.library;assetfile=root/report['monument']['asset_file'];name=original.name
with bpy.data.libraries.load(str(assetfile),link=False) as (available,wanted):wanted.collections=[name]
working=wanted.collections[0];working.name=name
for o in working.objects:
    me=o.data.copy();o.data=me;steps=64;rings=len(me.vertices)//steps
    if 'corpo inferior' in o.name:
        direction=-1 if ' -1' in o.name else 1
        for i in range(rings):
            z=8.7*i/(rings-1);dome=math.sqrt(max(.001,1-max(0,(z-5.5)/3.2)**2));rx=2.30*dome;ry=2.28*dome;cut=-.35+1.34*(min(1,z/5.5)**2);angle=math.asin(min(.999,cut))
            for j in range(steps):
                theta=math.pi-angle+(math.pi+2*angle)*j/(steps-1);me.vertices[i*steps+j].co=(rx*math.cos(theta),direction*2.25+ry*math.sin(theta),z)
        o['boas_component']='corpo inferior: recorte ascendente arqueado e cúpula superior'
    # Separar a normal da face recortada da carcaça curva, mantendo malha fechada.
    for edge in me.edges:
        aa,bb=edge.vertices
        if abs(aa-bb)==steps and aa%steps in (0,steps-1):edge.use_edge_sharp=True
    for face in me.polygons:face.use_smooth=len(face.vertices)==4
    me.update()
if working.name!=name:raise RuntimeError('Nome da coleção do asset não foi preservado')
bpy.data.libraries.write(str(assetfile),{working},compress=True)
for o in list(working.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.data.collections.remove(working);library.reload()
bpy.ops.wm.save_as_mainfile(filepath=str(root/report['candidate_file']))
report['monument']['asset_sha256']=hashlib.file_digest(assetfile.open('rb'),'sha256').hexdigest();report['monument']['refinement']='recorte inferior ascendente e separação de normais no encontro entre superfície curva e face recortada';report['candidate_sha256']=hashlib.file_digest((root/report['candidate_file']).open('rb'),'sha256').hexdigest();path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'asset_refined':report['monument']['asset_file'],'relative_link_preserved':True,'saved':report['candidate_file']}))
