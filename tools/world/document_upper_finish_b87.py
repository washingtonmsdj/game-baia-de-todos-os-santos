"""Registrar o resultado real da modelagem e QA B86/B87, sem promover produção."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=root/'docs/reports/blender/lacerda-finish-b87'
r=json.loads((out/'application.json').read_text(encoding='utf8'))
v=json.loads((out/'validation.json').read_text(encoding='utf8'))
assert r['sha256'] and r['reopened'] and v['reopened']
states=', '.join(f"Y {row['y']:+.1f}: {row['status']}" for row in v['junction'])
panes=sum(row['glass_panes'] for row in r['glazing'])
text=f'''# B87 — modelagem do fechamento e piso superior

## Resultado aplicado

**B87 salva e reaberta na única janela Blender**, PID {v['pid']}, porta MCP 9876, cena SALVADOR | ESBOCO OFICIAL. Fonte de autoria/validação registrada: `{r['file']}`. SHA-256: `{r['sha256']}`.

B86 preservada, SHA-256 `{r['parent_sha256']}`. B76–B85, SSOT, proxy B82 e gates históricos também preservados. Não houve exportação/promoção de produção.

## Modelagem

1. **Piso do saguão reconciliado com acabamento da ponte**: topo {r['floor_level']['before']:.6f} → {r['floor_level']['after']:.6f}, diferença {r['floor_level']['delta']*1000:.3f} mm. Topo dos dois colisores explicitamente vinculados recebeu a mesma correção. A cota relativa 0,00 da prancha 17 é a evidência independente de continuidade; o valor de acabamento foi obtido da malha existente da ponte, não da cápsula. A origem/datum global permanece candidata. Nenhum Z global ou terreno foi alterado.
2. **Duas paredes laterais do saguão reconstruídas com faixa de vidro**. Foram substituídas as três aberturas genéricas largas em cada lateral por envidraçamento contínuo com {panes} painéis, montantes e travessas. Materiais de vidro, esquadria e reboco foram reutilizados da passarela/retornos existentes. Não existe parede opaca atrás da faixa de vidro. O contorno principal continua o derivado da B86/prancha 17.
3. **Dois colisores simples de parede envidraçada**, vinculados às respectivas fontes, impedem atravessar o vidro. A geometria detalhada inteira não foi duplicada como collider. Os bindings são únicos e explícitos.
4. **Piso auxiliar NAV legado preservado como referência substituída**, fora da representação física/visual ativa. Seu collider já estava desabilitado na B80 e substituído pelo piso real da ponte; isso está comprovado no contrato e em `reconcile_upper_ground_b80.py`. Não foi removido um obstáculo real para liberar o teste. A função obsoleta ainda constava na apresentação da B86, atravessando o salão ampliado.
5. Seis peitoris vinculados às antigas três aberturas foram preservados como referência substituída. O fechamento novo inclui seus próprios encontros inferiores, evitando empilhar duas soluções visuais.

Nenhuma torre, cabine, poço, guia de fila, soleira do elevador ou desembarque inferior foi alterado nesta revisão. Não há teleporte, recorte de poço ou passagem invisível.

## Referências e precisão

- SUCOP 17, projeto 2023: contorno superior, esquadrias das circulações e níveis relativos. `source:lacerda-issue22-sucop-17`.
- Fotografias externas fornecidas pelo usuário e catalogadas, em especial `source:lacerda-exterior-photo-139fa6c8d4d1`: padrão qualitativo de faixa envidraçada contínua junto ao saguão.
- Retornos B84 e materiais/travessas da passarela: compatibilidade visual do fechamento.

**A largura dos módulos de vidro e suas seções são aproximações autorais**, reaproveitando o padrão existente de 0,68 m e travessas, não medidas derivadas da perspectiva da foto. Altura do vidro segue a passarela existente, de aproximadamente 71,225 a 73,875 no referencial local. A planta não certifica essas dimensões executadas. O recurso mantém `APPROXIMATE`, `partial`, `replacement_required: true` e `REPLACE_BEFORE_RELEASE`.

## Conferência objetiva

- {len(v['mesh_checks'])} componentes conferidos após reabertura: signatures persistidas e ausência de faces degeneradas.
- Paredes reconstruídas fechadas/manifold.
- Piso visual e dois derivados físicos na mesma altura final.
- Binding de cada novo collider único e preservando fonte.
- Hash da B86 e SSOT preservados.
- Aplicação confirmou preservação do terreno, dos 70 componentes do proxy B82 e dos objetos fora do escopo.
- Encontro ponte/saguão: {states}.

O QA local cobre 4 m, com cápsula R 0,30 / H 1,80 / skin 0,015 / step máximo candidato 0,25. Usa apoio da esfera inferior em faces/arestas finitas e CCD Lipschitz entre amostras; classifica contato/convergência insuficiente sem forçar aprovação. **Não representa controller completo, gravidade/slide no percurso inteiro, poço ou ligação até o Mercado.** `full_route_approved: false`, `engine_verified: false`.

Arquivos: `docs/reports/blender/lacerda-finish-b87/application.json`, `validation.json`, `artifacts/lacerda-live-diagnostic/b87-upper-finish.png`. Scripts: `model_upper_finish_b87.py` e `validate_upper_finish_b87.py` em `automation/blender/`.

## Gates preservados

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`; 27 testemunhas B80 `UNRESOLVED`; movimento histórico falso. Proxy B82 permanece separado e aproximado. Implantação/orientação das torres, comprimento livre completo da ponte e distribuição física dos quatro equipamentos continuam pendentes. O progresso desta revisão não deve ser apresentado como reprodução integral/certificada do Elevador Lacerda.

Lapa, Campo da Pólvora, Dique e Fonte Nova não foram alterados. Não houve npm, build, testes amplos, commit/push ou exportação de produção.
'''
(root/'docs/LACERDA_UPPER_FINISH_B87_2026-10-07.md').write_text(text,encoding='utf8')
header=f'''## 07/10/2026 — B87 ativa: saguão ampliado, vidro e piso reconciliados

B87 salva/reaberta na única janela PID {v['pid']}/MCP 9876. B86 corrigiu contorno/proporções superiores; B87 reconstruiu duas laterais envidraçadas, reconciliou topo do piso/colisores e preservou helper obsoleto como referência substituída. QA local: {states}; não aprova controller/poço/percurso completo. Torres e instalação ainda pendentes. SSOT, B76–B86, proxy B82, 27 testemunhas e bloqueio histórico preservados; sem produção. Fonte explícita authoring_source/validation_source B87. Relatório: docs/LACERDA_UPPER_FINISH_B87_2026-10-07.md.

'''
for name in ('PROJECT_STATUS.md','CODEX_HANDOFF.md','CODEX_STRUCTURE_HANDOFF.md'):
    path=root/'docs'/name;old=path.read_text(encoding='utf8')
    if not old.startswith(header):path.write_text(header+old,encoding='utf8')
provenance_path=root/'world/data-provenance.json';provenance=json.loads(provenance_path.read_text(encoding='utf8'))
for rid in ('derived:lacerda-upper-layout-b86','derived:lacerda-upper-finish-b87'):
    resource=next(x for x in provenance['resources'] if x['resource_id']==rid)
    resource['generation_status']='APPLIED_REOPENED_LOCAL_QA_ONLY'
provenance_path.write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
recovery_path=root/'docs/reports/blender/lacerda-layout-b86/session-recovery.json'
recovery=json.loads(recovery_path.read_text(encoding='utf8'))
recovery.update({'source_load_confirmed':True,'mcp_adoption_completed':True,'last_connection_result':'SUCCESS','b86_saved':True,
                 'note':'B85 recuperada/adotada antes da aplicação; B86 e B87 salvas/reabertas na única janela PID 16912.'})
recovery_path.write_text(json.dumps(recovery,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'documented':r['revision'],'local_qa':states,'full_route_approved':False},ensure_ascii=False))
