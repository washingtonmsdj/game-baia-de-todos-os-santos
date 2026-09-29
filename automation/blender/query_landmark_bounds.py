import bpy
terms=('ELEVADOR','LACERDA','MERCADO','PREFEITURA','PALACIO','PALÁCIO','CAMARA','CÂMARA')
for term in terms:
    rows=[]
    for o in bpy.data.objects:
        n=o.name.upper()
        if term in n and o.type in {'MESH','CURVE'}:
            c=o.matrix_world.translation
            rows.append((o.name,tuple(round(v,1) for v in c),tuple(round(v,1) for v in o.dimensions),o.users_collection[0].name if o.users_collection else ''))
    print(term, len(rows), rows[:20])
