"""Construção localizada de fachadas em plantas existentes; usada pelo passe e reparos."""
import bpy,bmesh,json,math
from mathutils import Vector
up=Vector((0,0,1))
class Boxes:
    def __init__(self):self.v=[];self.f=[]
    def add(self,c,x,y,z,size):
        k=len(self.v)
        for a,b,d in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:self.v.append(tuple(c+x*a*size[0]/2+y*b*size[1]/2+z*d*size[2]/2))
        self.f.extend(tuple(k+i for i in f) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])

def model_frontages(scene,specs,palette,mesh,signature,media):
    rows=[]
    trim,green,glass,rose,tile,gray=[palette[k] for k in ("trim","green","glass","rose","tile","gray")]
    for oid,levels,H,bays,paint,framesmat,style in specs:
        matches=[o for o in scene.objects if str(o.get('osm_way_id',''))==str(oid) and o.get('game_role')=='static_building_blockout']
        assert len(matches)==1,str(oid);body=matches[0];original_signature=signature(body)
        ps=[body.matrix_world@v.co for v in body.data.vertices];N=len(ps)//2
        assert len(ps)==N*2 and all((ps[i]-ps[i+N]).to_2d().length<.002 for i in range(N))
        poly=[p.to_2d() for p in ps[:N]];front_edge={1220650503:2}.get(oid,0);poly=poly[front_edge:]+poly[:front_edge];a=Vector((*poly[0],0));b=Vector((*poly[1],0));t=(b-a).normalized();L=(b-a).length
        centroid=sum((Vector((*p,0)) for p in poly),Vector())/N;normal=Vector((-t.y,t.x,0))
        if normal.dot(centroid-(a+b)/2)>0:normal=-normal
        zbase=min(p.z for p in ps[:N]);assert max(p.z for p in ps[:N])-zbase<.002
        top=zbase+H;gh=3.25;rh=(H-gh-.45)/(levels-1);pitch=L/bays
        props={'osm_way_id':str(oid),'boas_role':'visual_environment','reference_media_id':media,'reference_status':'candidate','classification':'ADAPT_LOCAL','boas_revision':'R30B.33','photo_binding_status':'candidate','height_verified_m':None,'height_basis':'Proporção/contagem visível de pavimentos; não medição','boas_location_candidate':f'edificio-baixa-osm-{oid}'}
        # Blender custom properties não aceitam None; o valor desconhecido fica no relatório.
        props.pop('height_verified_m')
        def P(s,z,out=0):return a+t*s+up*z+normal*out
        openings=[]
        for row in range(levels):
            z=zbase+gh*.48 if row==0 else zbase+gh+(row-.5)*rh
            h=2.62 if row==0 else rh*.62;w=pitch*(.70 if row==0 else .56)
            for j in range(bays):openings.append(((j+.5)*pitch,z,w,h,row,j))
        xs=sorted({0.,L,*[s+q*w/2 for s,z,w,h,row,j in openings for q in (-1,1)]})
        zs=sorted({zbase,top,*[z+q*h/2 for s,z,w,h,row,j in openings for q in (-1,1)]})
        vv=[];ff=[]
        def quad(points,v=vv,f=ff):k=len(v);v.extend(tuple(p) for p in points);f.append(tuple(range(k,k+len(points))))
        for i in range(1,N):
            p=Vector((*poly[i],0));q=Vector((*poly[(i+1)%N],0));quad([p+up*zbase,q+up*zbase,q+up*top,p+up*top])
        quad([Vector((*p,zbase)) for p in reversed(poly)]);quad([Vector((*p,top)) for p in poly])
        for x0,x1 in zip(xs,xs[1:]):
            for z0,z1 in zip(zs,zs[1:]):
                cx=(x0+x1)/2;cz=(z0+z1)/2
                if any(abs(cx-s)<w/2-1e-5 and abs(cz-z)<h/2-1e-5 for s,z,w,h,*_ in openings):continue
                quad([P(x0,z0),P(x1,z0),P(x1,z1),P(x0,z1)])
        for s,z,w,h,row,j in openings:
            corners=[(s-w/2,z-h/2),(s+w/2,z-h/2),(s+w/2,z+h/2),(s-w/2,z+h/2)]
            for p,q in zip(corners,corners[1:]+corners[:1]):quad([P(*p),P(*q),P(*q,-.22),P(*p,-.22)])
        inv=body.matrix_world.inverted();me=bpy.data.meshes.new(body.data.name+' | R33 fachada recortada');me.from_pydata([tuple(inv@Vector(p)) for p in vv],[],ff);me.materials.append(paint);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();body.data=me
        body['boas_revision']='R30B.33';body['reference_media_id']=media;body['boas_height_candidate_m']=H;body['boas_photo_binding_status']='candidate';body['boas_footprint_controls']=json.dumps([list(p) for p in poly])
        frames=Boxes();mould=Boxes();sills=Boxes();shutters=Boxes();gv=[];gf=[]
        for s,z,w,h,row,j in openings:
            for x in (s-w/2-.04,s+w/2+.04):frames.add(P(x,z,-.015),t,normal,up,(.08,.16,h+.16))
            for zz in (z-h/2-.04,z+h/2+.04):frames.add(P(s,zz,-.01),t,normal,up,(w+.16,.17,.08))
            frames.add(P(s,z,-.025),t,normal,up,(.055,.13,h));frames.add(P(s,z+.12,-.025),t,normal,up,(w,.13,.05))
            quad([P(s-w/2,z-h/2,-.13),P(s+w/2,z-h/2,-.13),P(s+w/2,z+h/2,-.13),P(s-w/2,z+h/2,-.13)],gv,gf)
            if row:
                sills.add(P(s,z-h/2-.09,.10),t,normal,up,(w+.28,.31,.11))
                if style!='gray_vertical_ribs':
                    for x in (s-w/2-.075,s+w/2+.075):mould.add(P(x,z,.05),t,normal,up,(.13,.14,h+.22))
                    for zz in (z-h/2-.065,z+h/2+.065):mould.add(P(s,zz,.05),t,normal,up,(w+.28,.14,.13))
            if style=='white_green_rose_awning' and row==1:
                # Folhas verdes visíveis na fachada: sem inventar interiores.
                for x in (s-w*.24,s+w*.24):shutters.add(P(x,z,-.06),t,normal,up,(w*.44,.035,h*.9))
        for zz in [zbase+gh,top-.32,top+.03]:mould.add(P(L/2,zz,.10),t,normal,up,(L,.32,.16 if zz<top else .23))
        if style=='gray_vertical_ribs':
            for j in range(bays+1):
                x=j*pitch;mould.add(P(x,zbase+(H+gh)/2,.14),t,normal,up,(.22,.28,H-gh+.42))
            for j in range(bays+1):mould.add(P(j*pitch,top+.26,.14),t,normal,up,(.22,.28,.46))
        for label,buf,m in [('Caixilhos',frames,framesmat),('Cornijas e frisos',mould,trim if style!='gray_vertical_ribs' else gray),('Peitoris',sills,trim),('Folhas verdes',shutters,green)]:
            if buf.v:mesh(f'BAIXA R33 | {oid} | {label}',buf.v,buf.f,m,props,body)
        mesh(f'BAIXA R33 | {oid} | Vidros',gv,gf,glass,props,body)
        if style=='white_green_rose_awning':
            # Toldo inclinado e bandô observáveis; projeção e cor candidatas.
            av=[];af=[]
            for out,z in [(0,zbase+3.15),(2.05,zbase+2.42),(2.05,zbase+2.10)]:
                av.extend([tuple(P(.12,z,out)),tuple(P(L-.12,z,out))])
            af.extend([(0,1,3,2),(2,3,5,4)])
            awning=mesh(f'BAIXA R33 | {oid} | Toldo rosado',av,af,rose,props,body)
            awning['projection_verified_m']='null';awning['projection_candidate_m']=2.05
            # Telhado de duas águas dentro da planta, parcialmente visto na foto.
            rv=[];rf=[]
            for side in (-1,1):
                half=[]
                for p,q in zip(poly,poly[1:]+poly[:1]):
                    dp=(Vector((*p,0))-a).dot(t)-L/2;dq=(Vector((*q,0))-a).dot(t)-L/2
                    if side*dp>=-1e-6:half.append(Vector((*p,0)))
                    if dp*dq<0:half.append(Vector((*p,0))+(Vector((*q,0))-Vector((*p,0)))*(-dp/(dq-dp)))
                quad([p+up*(top+.04+1.1*max(0,1-abs((p-a).dot(t)-L/2)/(L/2))) for p in half],rv,rf)
            roof_faces=len(rf)
            for p,q in zip(poly,poly[1:]+poly[:1]):
                p=Vector((*p,0));q=Vector((*q,0));sp=(p-a).dot(t);sq=(q-a).dot(t)
                hp=1.1*max(0,1-abs(sp-L/2)/(L/2));hq=1.1*max(0,1-abs(sq-L/2)/(L/2))
                if max(hp,hq)<.0001 and (sp-L/2)*(sq-L/2)>=0:continue
                boundary=[p+up*(top+.04+hp)]
                if (sp-L/2)*(sq-L/2)<0:boundary.append(p+(q-p)*((L/2-sp)/(sq-sp))+up*(top+1.14))
                boundary.append(q+up*(top+.04+hq))
                quad([p+up*(top+.04),q+up*(top+.04)]+list(reversed(boundary)),rv,rf)
            roof=mesh(f'BAIXA R33 | {oid} | Telhado cerâmico visível',rv,rf,tile,props,body);roof.data.materials.append(paint)
            for face in list(roof.data.polygons)[roof_faces:]:face.material_index=1
        rows.append({'osm_way_id':oid,'body':body.name,'footprint_controls_xy':[list(p) for p in poly],'source_signature':original_signature,'modeled_signature':signature(body),'candidate_height_m':H,'height_verified_m':None,'candidate_floors':levels,'facade_bays_candidate':bays,'style':style,'photo_binding_status':'candidate','reference_media_id':media,'footprint_xy_changed':False,'foundation_z_changed':False,'unseen_sides':'Volumes existentes preservados, sem novas janelas inventadas.'})
    return rows
