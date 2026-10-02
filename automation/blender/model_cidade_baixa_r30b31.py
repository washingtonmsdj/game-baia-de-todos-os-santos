"""Passe arquitetônico da frente inferior e Fonte de Mário Cravo, via MCP.

Footprints existentes preservados; alturas/composição da foto são candidatas.
Sem terreno, vias, tráfego, gameplay, npm ou builds.
"""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];cp=root/'world/areas/mvp-centro-lacerda/production.json';c=json.loads(cp.read_text());before=c['world_source'].copy()
if before['revision']!='R30B.30' or Path(bpy.data.filepath).resolve()!=(root/before['file']).resolve():raise RuntimeError('Abrir fonte R30B30 antes da modelagem')
scene=bpy.context.scene;bpy.context.view_layer.update()
existing=bpy.data.collections.get('ENVIRONMENT_FINAL | Cidade Baixa R31')
if existing and len(existing.all_objects):raise RuntimeError('Passe já aplicado; não duplicar')
for name in ('ENVIRONMENT_FINAL | Cidade Baixa R31','REFERENCE | fachadas anteriores R30B05'):
    empty=bpy.data.collections.get(name)
    if empty and not len(empty.all_objects):bpy.data.collections.remove(empty)
col=bpy.data.collections.new('ENVIRONMENT_FINAL | Cidade Baixa R31');scene.collection.children.link(col)
archive=bpy.data.collections.new('REFERENCE | fachadas anteriores R30B05');scene.collection.children.link(archive)
manifest=json.loads((root/'world/areas/mvp-centro-lacerda/media-manifest.json').read_text());photo=next(m['media_id'] for m in manifest['media'] if m['storage']['sha256'].startswith('783a31279c0d'));sculpt_photo=next(m['media_id'] for m in manifest['media'] if m['location_id']=='monumento-mario-cravo' and m['view']=='front')
def material(name,color,rough=.78,metal=0,glass=False,tiles=False):
    m=bpy.data.materials.new('BAIXA R31 | '+name);m.diffuse_color=(*color,1);m.use_nodes=True;ns=m.node_tree.nodes;ls=m.node_tree.links;p=next((n for n in ns if n.type=='BSDF_PRINCIPLED'),None)
    if p is None:
        p=ns.new('ShaderNodeBsdfPrincipled');out=next((n for n in ns if n.type=='OUTPUT_MATERIAL'),None) or ns.new('ShaderNodeOutputMaterial');ls.new(p.outputs[0],out.inputs['Surface'])
    p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if glass:p.inputs['Transmission Weight'].default_value=.65;p.inputs['IOR'].default_value=1.45
    else:
        noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=85 if not tiles else 12;noise.inputs['Detail'].default_value=2
        bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16 if not tiles else .34;bump.inputs['Distance'].default_value=.018 if not tiles else .05;ls.new(noise.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs['Normal'],p.inputs['Normal'])
        if tiles:
            brick=ns.new('ShaderNodeTexBrick');brick.inputs['Color1'].default_value=(.40,.11,.045,1);brick.inputs['Color2'].default_value=(.62,.24,.10,1);brick.inputs['Mortar'].default_value=(.25,.12,.06,1);brick.inputs['Scale'].default_value=3;brick.inputs['Mortar Size'].default_value=.006;ls.new(brick.outputs['Color'],p.inputs['Base Color']);ls.new(brick.outputs['Fac'],bump.inputs['Height'])
    return m
ivory=material('molduras e reboco claro',(.82,.80,.70));white=material('reboco branco',(.84,.85,.80));blue=material('reboco azul claro',(.46,.63,.70));yellow=material('reboco amarelo ocre',(.80,.66,.27));pink=material('faixas rosa antigo',(.62,.31,.35));gray=material('reboco cinza claro',(.64,.66,.63));stone=material('embasamento pedra',(.25,.28,.27));metal=material('caixilharia metal',(.26,.30,.30),.32,.65);dark=material('interiores em sombra',(.025,.035,.036));glass=material('vidro levemente esverdeado',(.16,.27,.30),.16,glass=True);roofmat=material('telha ceramica',(.50,.19,.08),tiles=True)
def mesh(name,verts,faces,mat,collection=col,parent=None,props=None,smooth=False):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);collection.objects.link(o)
    if parent:o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted()
    for k,v in (props or {}).items():o[k]=v
    if smooth:
        for p in me.polygons:p.use_smooth=True
    return o
class Boxes:
    def __init__(self):self.v=[];self.f=[]
    def add(self,center,xaxis,yaxis,zaxis,size):
        k=len(self.v)
        for a,b,d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:self.v.append(tuple(center+xaxis*a*size[0]/2+yaxis*b*size[1]/2+zaxis*d*size[2]/2))
        self.f.extend(tuple(k+i for i in f) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
up=Vector((0,0,1));R=Matrix.Rotation(bpy.data.objects['CASCA | parede lateral'].rotation_euler.z,4,'Z')
tobj=scene.objects[c['export']['road_object']];tobj.data.calc_loop_triangles();ground=BVHTree.FromPolygons([tobj.matrix_world@v.co for v in tobj.data.vertices],[list(t.vertices) for t in tobj.data.loop_triangles],all_triangles=True)
def ground_z(x,y):
    q=ground.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),350)[0]
    if q is None:raise RuntimeError('Sem terreno no acesso do edifício')
    return q.z
# Ordem de parcelas na frente existente; identidade arquitetônica ainda candidata.
specs=[(1263035779,3,9.2,ivory,'lattice',3,False),(1220650665,3,10.8,blue,'arches',3,True),(1220650754,6,22.,white,'deco',2,False),(1220650857,5,19.8,yellow,'colonial',3,True),(1220650885,5,19.6,ivory,'colonial',3,True),(574235997,6,24.,gray,'rect',3,False),(574235995,5,18.8,blue,'rect',3,True)]
ids={str(s[0]) for s in specs};archived=[]
for o in list(scene.objects):
    if o.name.startswith('ENTORNO LAC |') and any(str(o.get(k,'')) in ids for k in ('osm_way_id','source_osm_way_id','boas_osm_way_id')):
        archive.objects.link(o)
        for old in list(o.users_collection):
            if old!=archive:old.objects.unlink(o)
        o.hide_render=True;o.hide_set(True);o['boas_archive_reason']='Fachada visual R30B05 substituída pelo passe R31; objeto conservado como referência.';archived.append(o.name)
rows=[];created=[]
for oid,levels,H,paint,style,columns,pitched in specs:
    matches=[o for o in scene.objects if str(o.get('osm_way_id',''))==str(oid) and o.get('game_role')=='static_building_blockout']
    if len(matches)!=1:raise RuntimeError('Binding explícito de prédio ambíguo '+str(oid))
    body=matches[0];ps=[body.matrix_world@v.co for v in body.data.vertices];N=len(ps)//2;poly=[v.to_2d() for v in ps[:N]]
    if any((ps[i].to_2d()-ps[i+N].to_2d()).length>.002 for i in range(N)):raise RuntimeError('Prisma-fonte não corresponde à planta '+str(oid))
    if oid==574235995:poly=poly[4:]+poly[:4] # Frente explícita da parcela, não a primeira aresta lateral do prisma.
    a=Vector((*poly[0],0));b=Vector((*poly[1],0));t=(b-a).normalized();normal=Vector((-t.y,t.x,0));L=(b-a).length
    centroid=sum((Vector((*p,0)) for p in poly),Vector())/N
    if normal.dot(centroid-(a+b)/2)>0:normal=-normal
    gz=ground_z(*((a+b)/2+normal*.35).to_2d());base=gz-.20;top=base+H
    props={'osm_way_id':str(oid),'boas_location_candidate':f'edificio-baixa-osm-{oid}','boas_role':'visual_environment','classification':'ADAPT_LOCAL','reference_status':'candidate','reference_media_id':photo,'height_status':'estimativa fotográfica de pavimentos; não levantamento','boas_revision':'R30B.31'}
    def P(s,z,out=0):return a+t*s+up*z+normal*out
    opening=[];gh=3.45;rh=(H-gh-.5)/(levels-1);pitch=L/columns
    for row in range(levels):
        z=base+gh/2 if row==0 else base+gh+(row-.5)*rh
        hh=2.8 if row==0 else rh*.64;ww=min(pitch*.66,1.70 if row else pitch*.83)
        for j in range(columns):opening.append(((j+.5)*pitch,z,ww,hh,style=='arches' and row>0 or style=='colonial' and row==0,row,j))
    xs=sorted({0.,L,*[s+q*w/2 for s,z,w,h,arch,row,j in opening for q in (-1,1)]});zs=sorted({base,top,*[z+q*h/2 for s,z,w,h,arch,row,j in opening for q in (-1,1)]})
    verts=[];faces=[]
    def quad(vv):k=len(verts);verts.extend(tuple(v) for v in vv);faces.append(tuple(range(k,k+len(vv))))
    # Paredes laterais e fundo na planta original; fachada com aberturas reais.
    for j in range(1,N):
        q=Vector((*poly[j],0));r=Vector((*poly[(j+1)%N],0));quad([q+up*base,r+up*base,r+up*top,q+up*top])
    quad([Vector((*q,base)) for q in reversed(poly)]);quad([Vector((*q,top)) for q in poly])
    for x0,x1 in zip(xs,xs[1:]):
        for z0,z1 in zip(zs,zs[1:]):
            cx=(x0+x1)/2;cz=(z0+z1)/2
            if any(abs(cx-s)<w/2-.0001 and abs(cz-z)<h/2-.0001 for s,z,w,h,*_ in opening):continue
            quad([P(x0,z0),P(x1,z0),P(x1,z1),P(x0,z1)])
    inv=body.matrix_world.inverted();new=bpy.data.meshes.new(body.data.name+' | R31 aberturas');new.from_pydata([tuple(inv@Vector(v)) for v in verts],[],faces);new.materials.append(paint);new.update()
    bm=bmesh.new();bm.from_mesh(new);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(new);bm.free();body.data=new
    body['boas_facade_reference']=photo;body['boas_height_candidate_m']=H;body['boas_height_candidate_basis']='contagem/proporção visual de pavimentos; escala aproximada';body['boas_foundation_z_method']='cota de terreno existente diante da fachada, embutimento 20 cm; piso térreo horizontal';body['boas_footprint_controls']=json.dumps([list(q) for q in poly]);body['boas_revision']='R30B.31'
    frames=Boxes();trims=Boxes();sills=Boxes();lattice=Boxes();balcony=Boxes();gv=[];gf=[];rv=[];rf=[]
    def panel(vv,target_v,target_f):k=len(target_v);target_v.extend(tuple(v) for v in vv);target_f.append(tuple(range(k,k+len(vv))))
    for s,z,w,h,arch,row,j in opening:
        bottom=z-h/2;topwin=z+h/2
        if arch:
            radius=w/2;spring=topwin-radius
            inner=[(s-w/2,bottom),(s+w/2,bottom)]+[(s+radius*math.cos(k*math.pi/16),spring+radius*math.sin(k*math.pi/16)) for k in range(17)]
            # Encher somente os cantos acima do arco, preservando o vazio real.
            for k in range(16):
                x0,z0=inner[2+k];x1,z1=inner[3+k];panel([P(x0,z0),P(x1,z1),P(x1,topwin),P(x0,topwin)],rv,rf)
            outer=[(s+(x-s)*(w+.20)/w,bottom-.10+(zz-bottom)*(h+.20)/h) for x,zz in inner]
            for k in range(len(inner)):
                l=(k+1)%len(inner);panel([P(*inner[k],.055),P(*inner[l],.055),P(*outer[l],.055),P(*outer[k],.055)],rv,rf)
        else:
            inner=[(s-w/2,bottom),(s+w/2,bottom),(s+w/2,topwin),(s-w/2,topwin)]
            for x in (s-w/2-.055,s+w/2+.055):trims.add(P(x,z,.05),t,normal,up,(.11,.16,h+.20))
            for zz in (bottom-.055,topwin+.055):trims.add(P(s,zz,.055),t,normal,up,(w+.22,.16,.11))
        panel([P(x,zz,-.08) for x,zz in inner],gv,gf)
        # Ombreiras/revelos: profundidade da parede, caixilhos e peitoril separados.
        for x in (s-w/2+.025,s+w/2-.025):frames.add(P(x,z,-.025),t,normal,up,(.045,.12,h))
        frames.add(P(s,z,-.012),t,normal,up,(.04,.10,h));frames.add(P(s,z+.12 if row else z+.6,-.01),t,normal,up,(w,.10,.04))
        sills.add(P(s,bottom-.09,.12),t,normal,up,(w+.30,.34,.11))
        for k in range(len(inner)):
            l=(k+1)%len(inner);panel([P(*inner[k]),P(*inner[l]),P(*inner[l],-.22),P(*inner[k],-.22)],rv,rf)
        if style=='lattice' and row:
            for direction in (-1,1):
                for offset in [k*.30 for k in range(-math.ceil((w+h)/.30),math.ceil((w+h)/.30)+1)]:
                    pts=[]
                    for x in (-w/2,w/2):
                        yy=direction*x+offset
                        if -h/2<=yy<=h/2:pts.append((x,yy))
                    for yy in (-h/2,h/2):
                        xx=(yy-offset)/direction
                        if -w/2<=xx<=w/2:pts.append((xx,yy))
                    if len(pts)<2:continue
                    aa,bb=Vector((pts[0][0],0,pts[0][1])),Vector((pts[-1][0],0,pts[-1][1]));d=bb-aa
                    if d.length<.03:continue
                    axis=(t*d.x+up*d.z).normalized();cross=normal.cross(axis).normalized();lattice.add(P(s+(aa.x+bb.x)/2,z+(aa.z+bb.z)/2,.07),axis,normal,cross,(d.length,.08,.025))
    for floor in range(levels+1):
        zz=base if floor==0 else top if floor==levels else base+gh+(floor-1)*rh
        trims.add(P(L/2,zz,.075),t,normal,up,(L+.12,.24,.16 if floor<levels else .32))
    for x in (0.,L):trims.add(P(x,(base+top)/2,.065),t,normal,up,(.20,.18,H))
    if style=='deco':
        for x in [j*L/columns for j in range(1,columns)]:trims.add(P(x,(base+top)/2,.15),t,normal,up,(.27,.30,H+.25))
    for label,buff,mat in [('Molduras e cornijas',trims,ivory),('Caixilhos',frames,metal),('Peitoris',sills,ivory),('Cobogo diagonal',lattice,ivory)]:
        if buff.v:created.append(mesh(f'BAIXA R31 | {oid} | {label}',buff.v,buff.f,mat,parent=body,props=props).name)
    if gv:created.append(mesh(f'BAIXA R31 | {oid} | Vidros',gv,gf,glass,parent=body,props=props).name)
    if rv:created.append(mesh(f'BAIXA R31 | {oid} | Arcos e revelos',rv,rf,ivory,parent=body,props=props).name)
    if style=='lattice':
        bands=Boxes()
        for zz in (base+gh,base+gh+rh):bands.add(P(L/2,zz-.10,.115),t,normal,up,(L,.12,.72))
        created.append(mesh(f'BAIXA R31 | {oid} | Faixas rosadas',bands.v,bands.f,pink,parent=body,props=props).name)
    roofv=[tuple(Vector((*q,top+.04))) for q in poly]
    if pitched:
        roofv.append(tuple(centroid+up*(top+1.7)));rooff=[(i,(i+1)%N,N) for i in range(N)]
    else:rooff=[tuple(range(N))]
    created.append(mesh(f'BAIXA R31 | {oid} | Cobertura',roofv,rooff,roofmat if pitched else stone,parent=body,props=props).name)
    # Lajes dão profundidade aos vãos; interior continua apenas estrutural.
    slabv=[];slabf=[]
    for floor in range(1,levels):
        zz=base+gh+(floor-1)*rh;panel([Vector((*q,zz)) for q in poly],slabv,slabf)
    created.append(mesh(f'BAIXA R31 | {oid} | Lajes estruturais',slabv,slabf,dark,parent=body,props=props).name)
    rows.append({'osm_way_id':oid,'body':body.name,'footprint_controls_xy':[list(q) for q in poly],'street_front_length_m':L,'ground_source_z':gz,'candidate_height_m':H,'candidate_floors':levels,'photo_identity':'candidate','real_height_verified_m':None,'openings':len(opening),'style':style})
# Fonte: preservar o centro e o raio da bacia existente; escultura em asset próprio.
basin=scene.objects['CAIRU | bacia da fonte OSM'];corners=[basin.matrix_world@Vector(p) for p in basin.bound_box];center=Vector(((min(p.x for p in corners)+max(p.x for p in corners))/2,(min(p.y for p in corners)+max(p.y for p in corners))/2,min(p.z for p in corners)));radius=(max(p.x for p in corners)-min(p.x for p in corners))/2
sculptmat=material('fibra branca marfim da fonte',(.82,.80,.68),.38);rim=material('borda clara da bacia',(.78,.79,.74));water=material('agua azul esverdeada da fonte',(.065,.24,.30),.08,glass=True)
def lathe(name,profiles,mat,collection,parent=None,origin=Vector(),smooth=True):
    vv=[];ff=[];steps=64
    for z,cx,cy,rx,ry in profiles:
        for j in range(steps):a=2*math.pi*j/steps;vv.append(tuple(origin+Vector((cx+rx*math.cos(a),cy+ry*math.sin(a),z))))
    for i in range(len(profiles)-1):
        for j in range(steps):ff.append((i*steps+j,i*steps+(j+1)%steps,(i+1)*steps+(j+1)%steps,(i+1)*steps+j))
    ff+=[tuple(reversed(range(steps))),tuple((len(profiles)-1)*steps+j for j in range(steps))]
    return mesh(name,vv,ff,mat,collection,parent,smooth=smooth)
bp=[(0,0,0,radius,radius),(.12,0,0,radius,radius),(.40,0,0,radius-.24,radius-.24),(.40,0,0,radius-.65,radius-.65),(.12,0,0,radius-.75,radius-.75)]
fresh=lathe('BAIXA R31 | bacia da fonte — perfil',bp,rim,col,origin=center)
basin.data=fresh.data;basin.matrix_world=Matrix.Identity(4);bpy.data.objects.remove(fresh,do_unlink=True)
basin['boas_reference_media_id']=photo;basin['boas_placement_status']='Centro e raio da bacia existente preservados; identificação/fit geográfico candidato.'
floor=scene.objects['CAIRU | fundo da bacia'];floor.data.materials.clear();floor.data.materials.append(water)
asset=bpy.data.collections.new('ASSET | monumento-mario-cravo | R31');asset['boas_asset_id']='monumento-mario-cravo';asset['boas_reference_status']='modeling_candidate';asset['boas_reference_media_id']=sculpt_photo
def curved_lobe(name,profiles,offset):
    # Seções elípticas recortadas por uma superfície côncava contínua.
    # O recorte faz parte da malha fechada, sem booleanos nem cilindros sobrepostos.
    vv=[];ff=[];steps=64
    for z,rx,ry,cut in profiles:
        angle=math.asin(max(-.999,min(.999,cut)));start=math.pi-angle;end=2*math.pi+angle
        for j in range(steps):
            theta=start+(end-start)*j/(steps-1);vv.append((offset[0]+rx*math.cos(theta),offset[1]+ry*math.sin(theta),z))
    for i in range(len(profiles)-1):
        for j in range(steps):ff.append((i*steps+j,i*steps+(j+1)%steps,(i+1)*steps+(j+1)%steps,(i+1)*steps+j))
    ff.extend([tuple(reversed(range(steps))),tuple((len(profiles)-1)*steps+j for j in range(steps))])
    return mesh(name,vv,ff,sculptmat,asset,smooth=True)
for direction in (-1,1):
    lower=[]
    for j in range(81):
        z=8.7*j/80;dome=math.sqrt(max(.001,1-max(0,(z-5.5)/3.2)**2))
        cut=.62-.87*math.sin(math.pi*min(1,z/7.1)) if z<7.1 else .62
        lower.append((z,2.30*dome,2.28*dome,cut))
    o=curved_lobe('MARIO CRAVO | corpo inferior recortado '+str(direction),lower,(0,direction*2.25));o['boas_component']='corpo inferior com recorte côncavo'
    upper=[]
    controls=[(6.65,.15,.20,.99),(7.3,1.1,1.3,.99),(8.6,2.55,2.9,.98),(9.6,2.8,3.2,.70),(10.8,2.65,2.7,.05),(12.2,2.25,1.5,-.35),(14.0,2.15,.85,-.30),(16.0,2.0,.35,-.25)]
    for j in range(101):
        z=6.65+9.35*j/100
        for index,(aa,bb) in enumerate(zip(controls,controls[1:])):
            if aa[0]<=z<=bb[0]:
                u=(z-aa[0])/(bb[0]-aa[0]);pr=controls[max(0,index-1)];nx=controls[min(len(controls)-1,index+2)];values=[]
                for k in range(1,4):
                    ma=(bb[k]-pr[k])/(bb[0]-pr[0]);mb=(nx[k]-aa[k])/(nx[0]-aa[0]);values.append((2*u**3-3*u*u+1)*aa[k]+(u**3-2*u*u+u)*(bb[0]-aa[0])*ma+(-2*u**3+3*u*u)*bb[k]+(u**3-u*u)*(bb[0]-aa[0])*mb)
                upper.append((z,max(.02,values[0]),max(.02,values[1]),values[2]));break
    o=curved_lobe('MARIO CRAVO | vela superior recortada '+str(direction),upper,(direction*2.8,0));o['boas_component']='vela superior com face côncava e término achatado'
hero=bpy.data.collections.new('HERO | Monumento Mário Cravo R31');scene.collection.children.link(hero);instance=bpy.data.objects.new('MARIO CRAVO | Fonte da Rampa do Mercado',None);hero.objects.link(instance);instance.instance_type='COLLECTION';instance.instance_collection=asset;instance.location=center+Vector((0,0,.13));instance.rotation_euler.z=bpy.data.objects['CASCA | parede lateral'].rotation_euler.z
instance['boas_asset_id']='monumento-mario-cravo';instance['boas_location_candidate']='monumento-mario-cravo';instance['boas_reference_status']='modeling_candidate';instance['boas_reference_media_ids']=json.dumps([photo,sculpt_photo]);instance['boas_height_status']='16 m conforme descrição da fotografia Commons; forma/rotação candidatas, não levantamento';instance['boas_placement']='Centro da bacia existente preservado; sem deslocar ruas/praça'
assetfile=root/'blender/assets/monumento_mario_cravo/monumento_mario_cravo_v01.blend';assetfile.parent.mkdir(parents=True,exist_ok=True);bpy.data.libraries.write(str(assetfile),{asset},compress=True)
scene['boas_architectural_revision']='R30B.31 | Cidade Baixa — frente inferior e Fonte Mário Cravo'
report={'source_before':before,'reference_media_ids':[photo,sculpt_photo],'classification':'ADAPT_LOCAL','buildings':rows,'created_facade_objects':created,'archived_reference_objects':archived,'terrain_or_roads_changed':False,'footprints_xy_changed':False,'heights_status':'candidate photographic estimates; not survey','monument':{'asset_id':'monumento-mario-cravo','asset_file':assetfile.relative_to(root).as_posix(),'asset_sha256':hashlib.file_digest(assetfile.open('rb'),'sha256').hexdigest(),'basin_center_world':list(center),'basin_outer_radius_preserved_m':radius,'height_reference_m':16,'geographic_binding':'candidate_existing_basin','sculpture_status':'modeling_candidate','views_sufficient_for_approval':False},'visual_review':'pending','reopened':False,'runtime_exported':False}
dest=root/'blender/salvador_lacerda_r30b31_cidade_baixa_fachadas_cravo.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest));report['candidate_file']=dest.relative_to(root).as_posix();report['candidate_sha256']=hashlib.file_digest(dest.open('rb'),'sha256').hexdigest();(root/'docs/reports/blender/cidade_baixa_r30b31.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'saved':report['candidate_file'],'buildings':len(rows),'new_facade_objects':len(created),'archived_objects':len(archived),'monument_asset':report['monument']['asset_file'],'terrain_changed':False,'status':'modeling_candidate'},ensure_ascii=False))
