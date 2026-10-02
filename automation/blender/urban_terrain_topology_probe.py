"""Confere duplicação vertical e modificadores da malha de terreno."""
import bpy,json,collections
names=['MVP | terreno corrigido | colisão estática','SLICE | road | superfície particionada','SLICE | walkable | superfície particionada','SLICE | guias da malha particionada'];out=[]
for name in names:
    o=bpy.data.objects[name];heights=collections.defaultdict(list)
    for v in o.data.vertices:heights[(round(v.co.x,4),round(v.co.y,4))].append(v.co.z)
    differences=sorted([(max(z)-min(z),xy,min(z),max(z)) for xy,z in heights.items() if len(z)>1],reverse=True)
    out.append({'name':name,'modifiers':[(m.name,m.type) for m in o.modifiers],'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'height_range':[min(v.co.z for v in o.data.vertices),max(v.co.z for v in o.data.vertices)],'largest_vertical_duplicates':differences[:5]})
print(json.dumps(out))
