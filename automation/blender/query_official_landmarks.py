import bpy
terms=('elevador','lacerda','mercado','modelo','prefeitura','palacio','rio branco','cairu','tome')
hits=[]
for o in bpy.data.objects:
    n=o.name.lower()
    if any(t in n for t in terms):
        hits.append((o.name, tuple(round(x,3) for x in o.location), tuple(round(x,3) for x in o.dimensions)))
print(hits[:250])
