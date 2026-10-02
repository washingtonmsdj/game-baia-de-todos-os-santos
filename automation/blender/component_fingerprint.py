"""Comparação determinística de componentes, sem alterar geometria visível."""
import bpy,hashlib,json
from array import array

def world_matrix(o):
    if o.constraints:raise RuntimeError('Comparação exige revisar constraints de '+o.name)
    return world_matrix(o.parent)@o.matrix_parent_inverse@o.matrix_basis if o.parent else o.matrix_basis.copy()

def signature(o):
    h=hashlib.sha256()
    if o.type=='MESH':
        for container,attribute,size,kind in ((o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'loop_start',1,'i'),(o.data.polygons,'loop_total',1,'i'),(o.data.polygons,'material_index',1,'i')):
            buffer=array(kind,[0])* (len(container)*size);container.foreach_get(attribute,buffer);h.update(buffer.tobytes())
    elif o.type=='FONT':h.update(json.dumps([o.data.body,o.data.size,o.data.extrude,o.data.bevel_depth],ensure_ascii=False).encode())
    elif o.type=='CURVE':
        for spline in o.data.splines:
            h.update(str(spline.type).encode())
            for point in spline.bezier_points:h.update(str((tuple(point.co),tuple(point.handle_left),tuple(point.handle_right))).encode())
            for point in spline.points:h.update(str(tuple(point.co)).encode())
    mats=[]
    for m in getattr(o.data,'materials',[]):
        if m is None:mats.append(None);continue
        p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
        mats.append({'diffuse':list(m.diffuse_color),'base':list(p.inputs['Base Color'].default_value) if p else None,'roughness':p.inputs['Roughness'].default_value if p else m.roughness,'metallic':p.inputs['Metallic'].default_value if p else m.metallic})
    matrix=[list(row) for row in world_matrix(o)]
    return {'geometry_sha256':h.hexdigest(),'transform':matrix,'materials':mats,'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else None,'polygons':len(o.data.polygons) if o.type=='MESH' else None}

def inspect_file(file,names):
    before=set(bpy.data.objects);before_meshes=set(bpy.data.meshes);before_curves=set(bpy.data.curves);before_materials=set(bpy.data.materials)
    try:
        with bpy.data.libraries.load(str(file),link=False) as (available,requested):
            missing=set(names)-set(available.objects)
            if missing:raise RuntimeError('Componentes ausentes na fonte: '+str(sorted(missing)))
            requested.objects=list(names)
        return {name:signature(o) for name,o in zip(names,requested.objects)}
    finally:
        for o in set(bpy.data.objects)-before:
            if not o.users_scene:bpy.data.objects.remove(o,do_unlink=True)
        for table,known in ((bpy.data.meshes,before_meshes),(bpy.data.curves,before_curves),(bpy.data.materials,before_materials)):
            for data in set(table)-known:
                if data.users==0:table.remove(data)
