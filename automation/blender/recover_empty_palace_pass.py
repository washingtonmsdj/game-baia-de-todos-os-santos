"""Remove somente datablocks vazios do passe que falhou antes de gerar objetos."""
import bpy
c=bpy.data.collections.get('HERO | Palácio Rio Branco | fotografia R34')
assert c and not c.all_objects,'Recuperação só permite coleção vazia'
bpy.data.collections.remove(c)
for m in list(bpy.data.materials):
    if m.name.startswith('RIO R34 |') and m.users==0:bpy.data.materials.remove(m)
print('Passe vazio limpo; geometria B33 não foi alterada.')
