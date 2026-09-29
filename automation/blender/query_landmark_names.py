import bpy
terms=('ELEVADOR','LACERDA','MERCADO','PREFEITURA','PALACIO','PALÁCIO','CAMARA','CÂMARA')
for term in terms:
    rows=[o.name for o in bpy.data.objects if term in o.name.upper()]
    print(term, len(rows), rows[:80])
