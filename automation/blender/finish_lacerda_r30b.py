"""Acabamento das esquadrias e consolidação dos detalhes estáticos R30B."""
import bpy, json
from pathlib import Path
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parents[2]
col=bpy.data.collections['HERO | Lacerda | detalhes R30B']
R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z');I=R.inverted()
ivory=bpy.data.materials['LAC R30B | reboco marfim fino']

# Transparência de lâmina fina visível também no preview Eevee, sem depender de ray tracing.
m=bpy.data.materials['LAC R30B | vidro incolor transparente'];nt=m.node_tree
p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL')
t=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.16
nt.links.new(t.outputs[0],mix.inputs[1]);nt.links.new(p.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])

def bb(o):
    vs=[I@o.matrix_world@v.co for v in o.data.vertices]
    return [(min(v[i] for v in vs),max(v[i] for v in vs)) for i in range(3)]

# Chanfros superiores das aberturas da passarela, conforme foto interior catalogada.
pillars=[bb(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('PASSARELA | montante interno')]
for side in sorted(set(round(sum(b[1])/2,2) for b in pillars)):
    xs=sorted(b[0] for b in pillars if abs(sum(b[1])/2-side)<.05)
    for j,(a,b) in enumerate(zip(xs,xs[1:])):
        if b[0]-a[1]<.5:continue
        for start,sgn in [(a[1],1),(b[0],-1)]:
            # Pequeno enchimento de alvenaria, fora do volume de circulação.
            points=[(start,73.875),(start+sgn*.27,73.875),(start,73.60)]
            vs=[tuple(R@Vector((x,side+dy,z))) for dy in [-.065,.065] for x,z in points]
            me=bpy.data.meshes.new('Chanfro abertura');me.from_pydata(vs,[],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);me.update()
            o=bpy.data.objects.new('LAC R30B | Passarela | chanfro %s %s %s'%(side,j,sgn),me);col.objects.link(o);me.materials.append(ivory)
            o['boas_location_id']='elevador-lacerda';o['boas_role']='visual_detail'

# Uma malha por conjunto fixo de venezianas/frisos. Nenhum objeto funcional é unido.
groups={}
for o in list(col.objects):
    if ' | lamela ' in o.name:key=o.name.split(' | lamela ')[0]+' | veneziana completa'
    elif 'Galeria | cruzeta ' in o.name:key='LAC R30B | Galeria | frisos cruzetados'
    elif ' | chanfro ' in o.name:key='LAC R30B | Passarela | chanfros das aberturas'
    else:continue
    groups.setdefault(key,[]).append(o)
deps=bpy.context.evaluated_depsgraph_get()
for name,objects in groups.items():
    verts=[];faces=[];mats=[];indices=[]
    for o in objects:
        ev=o.evaluated_get(deps);me=ev.to_mesh();base=len(verts)
        verts.extend(tuple(o.matrix_world@v.co) for v in me.vertices)
        for poly in me.polygons:
            faces.append(tuple(base+i for i in poly.vertices));mat=me.materials[poly.material_index]
            if mat not in mats:mats.append(mat)
            indices.append(mats.index(mat))
        ev.to_mesh_clear()
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    for mat in mats:me.materials.append(mat)
    for p,idx in zip(me.polygons,indices):p.material_index=idx
    merged=bpy.data.objects.new(name,me);col.objects.link(merged)
    merged['boas_location_id']='elevador-lacerda';merged['boas_role']='visual_detail'
    for o in objects:bpy.data.objects.remove(o,do_unlink=True)

report_path=ROOT/'artifacts/lacerda/refinement_report.json'
report=json.loads(report_path.read_text(encoding='utf8'));report['added_visual_objects']=len(col.objects)
report['visual_review']='Galeria, venezianas e transparência inspecionadas; interior completo e demais vistas pendentes.'
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps(report,ensure_ascii=False))
