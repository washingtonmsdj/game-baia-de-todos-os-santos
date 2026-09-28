import bpy
from collections import defaultdict
from mathutils import Vector

SURFACE = 'BAÍA DE TODOS-OS-SANTOS | superfície e recorte costeiro'
COLLECTION = '36 VISUAL | OCEANO R30A8'


def ensure_collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def coastline_chains(obj):
    mesh = obj.data
    usage = defaultdict(int)
    for poly in mesh.polygons:
        for a, b in zip(poly.vertices, poly.vertices[1:] + poly.vertices[:1]):
            usage[tuple(sorted((a, b)))] += 1
    edges = [e for e, count in usage.items() if count == 1]
    world = [obj.matrix_world @ v.co for v in mesh.vertices]
    xs = [p.x for p in world]; ys = [p.y for p in world]
    xmin, xmax = min(xs), max(xs); ymin, ymax = min(ys), max(ys)
    tol = 1.5

    def artificial(i):
        p = world[i]
        return abs(p.x-xmin) < tol or abs(p.y-ymin) < tol or abs(p.y-ymax) < tol

    coast_edges = [(a,b) for a,b in edges if not (artificial(a) and artificial(b))]
    adj = defaultdict(list)
    for a,b in coast_edges:
        adj[a].append(b); adj[b].append(a)
    unused = {tuple(sorted(e)) for e in coast_edges}
    chains=[]
    while unused:
        a,b = next(iter(unused))
        start = a if len(adj[a]) != 2 else (b if len(adj[b]) != 2 else a)
        chain=[start]; prev=None; cur=start
        while True:
            candidates=[]
            for nxt in adj[cur]:
                key=tuple(sorted((cur,nxt)))
                if key in unused and nxt != prev:
                    candidates.append(nxt)
            if not candidates: break
            nxt=candidates[0]
            unused.discard(tuple(sorted((cur,nxt))))
            chain.append(nxt); prev,cur=cur,nxt
            if cur == start: break
        if len(chain) >= 2:
            chains.append([world[i].copy() for i in chain])
    return chains


def build_curve(name, chains, material, bevel, z):
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old, do_unlink=True)
    data=bpy.data.curves.new(name+' | DATA','CURVE')
    data.dimensions='3D'; data.resolution_u=4; data.bevel_depth=bevel; data.bevel_resolution=3
    for chain in chains:
        spline=data.splines.new('POLY')
        spline.points.add(len(chain)-1)
        for point,co in zip(spline.points,chain):
            point.co=(co.x,co.y,z,1.0)
    if material: data.materials.append(material)
    obj=bpy.data.objects.new(name,data)
    ensure_collection(COLLECTION).objects.link(obj)
    obj['boas_revision']='R30A.8'; obj['boas_source']='water_surface_boundary'; obj['boas_visual_only']=True
    return obj

surface=bpy.data.objects[SURFACE]
chains=coastline_chains(surface)
near=build_curve('R30A8 | FOAM | linha costeira',chains,bpy.data.materials.get('R30A8 | Espuma costeira'),0.22,0.395)
soft=build_curve('R30A8 | FOAM | halo costeiro',chains,bpy.data.materials.get('R30A8 | Espuma costeira suave'),0.55,0.385)
print({'chains':len(chains),'near':near.name,'soft':soft.name})
bpy.ops.wm.save_mainfile()
