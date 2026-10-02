"""Retopologia localizada da borda da praça para expor a contenção arqueada.

As fotos mostram alvenaria vertical imediatamente abaixo do guarda-corpo.
A interpolação suave B30 mantinha solo na frente dessa alvenaria por 12 m.
Corrige apenas as duas bandas existentes, mantendo a praça e vias no lugar.
"""
import bpy,bmesh,json,hashlib,runpy,shutil,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];scene=bpy.context.scene
path=root/'docs/reports/blender/palacio_rio_branco_r30b34.json';r=json.loads(path.read_text(encoding='utf8'))
assert not r.get('retaining_profile_refinement'),'Correção já aplicada'
signature=runpy.run_path(str(root/'automation/blender/component_fingerprint.py'))['signature']
names=['MVP | terreno corrigido | colisão estática','R30A5 | COLLISION | terrain proxy']
old={n:signature(scene.objects[n]) for n in names};source=scene.objects[names[0]];source.data.calc_loop_triangles()
tris=list(source.data.loop_triangles)
original_triangle_materials=[source.data.polygons[t.polygon_index].material_index for t in tris]
bvh=BVHTree.FromPolygons([source.matrix_world@v.co for v in source.data.vertices],[list(t.vertices) for t in tris],all_triangles=True)
allowed={i for i,m in enumerate(source.data.materials) if any(k in m.name.lower() for k in ('terreno','conten','encosta')) and not any(k in m.name.lower() for k in ('asfalto','pedonal','percurso','passeio','calçada','calcada','chile'))}
segments=r['galleries']['segments'];rows=[];up=Vector((0,0,1))
backup=root/'artifacts/palacio-rio-branco/r30b34_before_retaining_profile.blend';assert not backup.exists();shutil.copy2(Path(bpy.data.filepath),backup)
def ground_allowed(w):
    h=bvh.ray_cast(Vector((w.x,w.y,140)),Vector((0,0,-1)),220)
    return h[0] is not None and original_triangle_materials[h[2]] in allowed
def ease(v):v=max(0,min(1,v));return v*v*(3-2*v)
for name in names:
    o=scene.objects[name];o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data);M=o.matrix_world.copy();I=M.inverted()
    def permitted(f):
        if o==source:return f.material_index in allowed
        return ground_allowed(M@f.calc_center_median())
    roadlocked={v for f in bm.faces if not permitted(f) for v in f.verts}
    splits=0;moved=0;max_delta=0;local_segments=[]
    for s in segments:
        p,u,n=Vector(s['origin_world']),Vector(s['along_world']),Vector(s['outward_world']);L=s['length_from_existing_controls_m']
        def within(f):
            pts=[M@v.co-p for v in f.verts];xs=[v.dot(u) for v in pts];ys=[v.dot(n) for v in pts]
            return max(xs)>-1 and min(xs)<L+1 and max(ys)>-1.5 and min(ys)<20.5 and max((M@v.co).z for v in f.verts)>s['origin_world'][2]-.5
        # Acrescenta controle da ruptura da borda, sem cortar o mapa inteiro.
        for normal,value in [(u,x) for x in (0,.8,L-.8,L)]+[(n,y) for y in (-1.2,0,.35,1.,8.,16.,20.)]:
            faces=[f for f in bm.faces if permitted(f) and within(f)]
            if not faces:continue
            geom=set(faces)
            for f in faces:geom.update(f.edges);geom.update(f.verts)
            result=bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.00001,plane_co=I@(p+normal*value),plane_no=M.to_3x3().transposed()@normal,clear_inner=False,clear_outer=False)
            splits+=len(result['geom_cut'])
        roadlocked.update(v for f in bm.faces if not permitted(f) for v in f.verts)
        changed=0
        for v in bm.verts:
            if v in roadlocked:continue
            w=M@v.co;d=w-p;x=d.dot(u);y=d.dot(n)
            if not(0<=x<=L and -1.2<=y<=20 and w.z>s['origin_world'][2]-.8):continue
            if not ground_allowed(w):continue
            # Pé da alvenaria observada, .12 m abaixo do piso dos nichos.
            target=min(w.z,p.z-.12-.08*max(0,y))
            influence=ease(min(x/.8,(L-x)/.8))
            influence*=ease((y+1.2)/1.2) if y<0 else 1-ease((y-8)/12)
            newz=w.z+(target-w.z)*influence
            if abs(newz-w.z)<.00001:continue
            max_delta=max(max_delta,abs(newz-w.z));w.z=newz;v.co=I@w;moved+=1;changed+=1
        local_segments.append({'name':s['name'],'moved_vertices':changed})
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    o['r34_profile_reason']='Ruptura local de contenção vertical documentada nas fotos; elimina solo na frente das galerias, preservando XY, praça e materiais de circulação.'
    o['r34_profile_classification']='ADAPT_LOCAL';o['r34_profile_status']='candidate_photo_geometry; medidas de base/profundidade não levantadas'
    rows.append({'object':name,'before':old[name],'after':signature(o),'moved_vertices':moved,'max_z_delta_m':max_delta,'bisect_elements':splits,'segments':local_segments})
assert all(signature(scene.objects[n])==sig for n,sig in r['protected_signatures'].items() if n not in names),'Mudança fora do escopo'
r['retaining_profile_refinement']={'classification':'ADAPT_LOCAL','evidence':'Fotos do usuário 1,3 e9 mostram face vertical imediatamente abaixo do guarda-corpo; seções gallery_ground.json documentam transição suave do terreno anterior ocultando os arcos.','controls':'Mesmo traçado dos capeamentos e cota superior herdados; nenhum deslocamento XY do palácio, praça, galerias ou vias.','geometry':rows,'walkable_and_road_materials_excluded':True,'global_dem_changed':False,'global_z_scale_changed':False,'top_plaza_changed':False,'collision':'Mesma correção localizada no proxy simplificado; nenhum collider detalhado da arquitetura. Revalidação de gameplay pendente, sem exportar runtime.','measurements_status':'Altura de nichos e base são candidatas pela foto; ajuste local de ruptura e transição, não medição topográfica.','backup':backup.relative_to(root).as_posix(),'visual_review':'pending'}
r['changes'].append('Ruptura localizada do barranco junto às galerias; retopologia visual/proxy coordenada, sem alterar XY ou vias.');r['limitations'].append('Novo encontro de contenção/solo requer futura validação de gameplay antes de promoção; nenhuma alteração foi exportada ao jogo.')
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
r['source_after']['sha256']=hashlib.file_digest(Path(bpy.data.filepath).open('rb'),'sha256').hexdigest();path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'profile':[(x['object'],x['moved_vertices'],x['max_z_delta_m']) for x in rows],'source_after':r['source_after']},ensure_ascii=False))
