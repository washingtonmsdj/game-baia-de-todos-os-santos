"""Registro de modelagem candidata dos vestíbulos, sem promoção para produção."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];out=root/'docs/reports/blender/lacerda-vestibules-b97'
r=json.loads((out/'application.json').read_text());q=json.loads((out/'validation.json').read_text());p=json.loads((out/'presentation.json').read_text())
assert r['reopened'] and q['reopened'] and p['file']==r['file'] and not p['local_view'] and p['terrain_visible'] and not p['unsaved_changes']
with (root/r['file']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256']
assert hashlib.sha256((root/'world/geographic-reference.json').read_bytes()).hexdigest()==r['ssot_sha256']
doc=root/'docs/LACERDA_UPPER_VESTIBULES_B97_2026-10-07.md'
doc.write_text(f'''# Lacerda — limites dos vestíbulos superiores B97 — 07/10/2026

B97 modelada, salva e reaberta na única janela Blender PID{r['pid']}/MCP9876. Fonte: `{r['file']}`. SHA-256 `{r['sha256']}`. B76–B96 intactas.

## Modelagem e evidência

Dois limites em L acrescentados às bordas dos vestíbulos `SAÍDA 20,10m²` e `ENTRADA 15,17m²` da prancha SUCOP17. O contorno relativo usa os mesmos controles B88, sem novo SSOT, mudança de escala/origem ou ajuste do terreno. As aberturas a leste continuam intencionalmente livres. O inventário espacial B96 não encontrou proteção nessas bordas; o guarda existente perto da torre nova não corresponde a estes vestíbulos.

A nota documental “DEMOLIR FECHAMENTO EM ALVENARIA — MANTER GUARDA-CORPO” comprova a intenção do projeto2023. **Não comprova execução atual, seção, altura ou material do guarda-corpo.** Os dois volumes são massing de proteção, com seção adotada de 0,18m e altura candidata de 1,10m: `status=GAMEPLAY_PROXY`, `accuracy=APPROXIMATE`, `replacement_required=true`. Não apresentar essas medidas como levantamento real ou guarda certificado. Material sólido serve à leitura de massa; tipologia final ainda depende de evidência. A implantação absoluta permanece candidata.

As novas peças reutilizam a coleção superior existente e possuem proveniência centralizada, vínculo ao piso-fonte e `boas_collision_enabled=false`. Não substituem/dobram o GAMEPLAY_PROXY B82 nem habilitam navegação histórica. Nenhuma arquitetura existente foi removida, ocultada, deformada ou reparentada.

## Conferência

- Duas meshes fechadas, sem faces degeneradas, arestas não manifold ou winding incoerente.
- {q['preserved_architecture_components']} componentes anteriores preservados por assinatura de geometria, transform e materiais. {r['protected_object_count']} objetos existentes preservados no escopo de dados/transform/visibilidade/parent durante a aplicação.
- {len(q['support_checks'])} amostras do disco de apoio raio0,30 + skin0,015 sobre o piso real, mais {len(q['local_guard_clearance'])} conferências de afastamento das guardas. Nenhuma tampa nova cruza os acessos orientais.
- Dois primeiros pontos de sondagem ficaram perto demais da guarda e foram rejeitados. Novas amostras foram posicionadas no interior livre dos vestíbulos; guarda/raio/skin não mudaram. Distâncias registradas em `rejected_initial_samples`. Isso não constitui autorização de rota ou ajuste de arquitetura para passar teste.
- É **QA local de apoio/limite**, não sweep volumétrico completo da cena, controller, CCD da cabine ou aprovação do percurso Tomé–Mercado. Não foi repetido teste de poço/cabine.
- Fonte reaberta/hash conferido; vistas reais `artifacts/lacerda-live-diagnostic/b97-saida.png`, `b97-entrada.png`, `b97-map.png`. A janela termina com mapa completo e terreno visível, sem edição pendente.

## Estado preservado

`LACERDA_VERTICAL=BLOCKED_EXTERNAL_EVIDENCE`; `movement_enabled=false`; `27 testemunhas B80=UNRESOLVED/PRESERVED`; `GAMEPLAY_PROXY B82=PRESERVED`; `replacement_required=true`; `EXPANDED_MAP=GREYBOX`; `production_ready=false`. Nenhuma exportação/produção, fachada nova ou alteração de Lapa/Dique/Fonte Nova.

Próximo trecho: reconciliar os pilares e aberturas da frente superior com a linha oblíqua e os acessos da prancha17. O inventário registra a frente candidata antiga em cinco vãos: não tomar sua disposição como comprovação das portas reais, nem deslocar a cidade para acomodá-la. Guardas e suas seções continuam candidatas até evidência independente.
''',encoding='utf8')
path=root/'world/data-provenance.json';prov=json.loads(path.read_text());resource={'resource_id':'derived:lacerda-upper-vestibules-b97','provider':'Bay of All Saints / modelagem candidata derivada SUCOP','dataset':'Limites relativos dos vestíbulos superiores da prancha17','capture_date':'2026-10-07','bounds':None,'raw_files':[],'derived_files':[r['file'],doc.relative_to(root).as_posix(),(out/'application.json').relative_to(root).as_posix(),(out/'validation.json').relative_to(root).as_posix()],'usage_class':'PENDENTE_VERIFICACAO','release_status':'REPLACE_BEFORE_RELEASE','purpose':'Modelagem das bordas com aberturas preservadas; seção aproximada explicitamente separada de dados documentais','dependencies':['derived:lacerda-upper-body-b96','source:lacerda-issue22-sucop-17'],'kind':'geometry','status':'GAMEPLAY_PROXY','accuracy':'APPROXIMATE','replacement_required':True}
assert all(v in {x['resource_id'] for x in prov['resources']} for v in resource['dependencies'])
old=next((v for v in prov['resources'] if v['resource_id']==resource['resource_id']),None)
if old:old.update(resource)
else:prov['resources'].append(resource)
path.write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
summary='''## 07/10/2026 — B97 ativa: bordas dos vestíbulos superiores

B97 salva/reaberta na mesma janela MCP9876. Dois volumes de guarda nos limites ENTRADA/SAÍDA da planta17; acessos orientais livres, nenhum componente anterior modificado. Contorno relativo documental, seção0,18/altura1,10 aproximadas, GAMEPLAY_PROXY/replacement_required: não as-built. QA das duas meshes,108 apoios locais e603 assinaturas preservadas; sem aprovação de controller. B76–B96, SSOT, B82 e gates históricos intactos; produção bloqueada. Relatório: docs/LACERDA_UPPER_VESTIBULES_B97_2026-10-07.md. Próximo: frente superior/pilares/aberturas conforme linha oblíqua documental; não expansão ou fachada fina.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
 path=root/'docs'/name;s=path.read_text(encoding='utf8')
 if not s.startswith(summary):path.write_text(summary+s,encoding='utf8')
print(json.dumps({'revision':'B97','report':doc.relative_to(root).as_posix(),'production_ready':False}))
