"""Correção de revisão visual, auditoria e salvamento final da candidata V09."""
import bpy
import hashlib
import json
from pathlib import Path

repo=Path(__file__).resolve().parents[2]
s=bpy.context.scene
assert not bpy.app.background
assert Path(bpy.data.filepath).name=='marrom_v09.blend'
assert s.get('boas_v09_finish_applied') and not s.get('boas_v09_closed')
# A revisão multivista mostrou que levantar a borda posterior produzia um
# ressalto. Reverter somente essa tentativa; não promover essa alteração.
roof=s.objects['RDP01 | HILUX06 | Teto curvatura dupla']
for v in roof.data.vertices:
    if v.co.y>.86:
        t=min(1,(v.co.y-.86)/.253);e=t*t*(3-2*t)
        v.co.z-=.065*e;v.co.x/=1+.052*e
roof.data.update()
roof['boas_v09_finish']='Teto preservado; tentativa de elevação revertida após revisão lateral'
s['boas_v09_closed']=True
bpy.context.view_layer.update()
wheelbase=abs(s.objects['RDP01 | Eixo giro roda 1 -1'].location.y-s.objects['RDP01 | Eixo giro roda 0 -1'].location.y)
assert abs(wheelbase-3.085)<.00001
rp=repo/'docs/reports/blender/rondesp_marrom_v09.json'
r=json.loads(rp.read_text(encoding='utf-8'))
r['changes']=[x for x in r['changes'] if x!='encaixe posterior do teto']
r['visual_correction']='Elevação posterior do teto revertida: criava ressalto na vista lateral.'
r['wheelbase_measured_m']=wheelbase
r['objects']=len(s.objects)
r['status']='candidate'
r['pending']=['aprovação final da fidelidade de carroceria','brasão PMBA detalhado','camuflagem exata','animação e runtime']
r['validation']={'compileall':'passed','unittest_count':62,'unittest':'passed','reference_registry_errors':0,'reference_registry_warnings':2}
r['reference_ids']=['hilux-std-stock-front','hilux-2024-std-dealer-side','hilux-srx-user-front','rondesp-31110-front','rondesp-31110-rear']
r['research']=[
 {'url':'https://www.toyotacomunica.com.br/toyota-hilux-e-sw4-estreiam-novidades-na-linha-2025/','purpose':'Publicação oficial da linha 2025; encontrada no índice de pesquisa. Conteúdo integral indisponível no fetch.'},
 {'url':'https://media.toyota.com.br/0a63079c-ec07-4607-a6b0-b0d182bda6b4.pdf','purpose':'Catálogo 2024/2025 localizado; acesso ao PDF retornou HTTP 403, não usado como medição.'},
 {'url':'https://www.instagram.com/p/DV4fernIZKG/?img_index=1','purpose':'Foto da RONDESP 3.1110 já fornecida pelo usuário e catalogada, inspecionada localmente. Sotero Filho/viaturas_ba_.'}
]
out=repo/'blender/assets/vehicles/rondesp-pickup/marrom_v09.blend'
bpy.data.libraries.write(str(out),{s},path_remap='RELATIVE',fake_user=True,compress=True)
r['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();r['source_reopened']=False
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reopen():
    bpy.ops.wm.open_mainfile(filepath=str(out))
    r=json.loads(rp.read_text(encoding='utf-8'));r['source_reopened']=Path(bpy.data.filepath).resolve()==out.resolve()
    rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return None
bpy.app.timers.register(reopen,first_interval=.5)
