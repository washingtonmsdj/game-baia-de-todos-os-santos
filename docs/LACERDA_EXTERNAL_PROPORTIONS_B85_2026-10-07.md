# B85 — apoio da encosta e diagnóstico do conjunto superior

## Revisão aplicada

Fonte de authoring: `blender/salvador_lacerda_r30b85_apoio_encosta_proporcoes.blend`, SHA-256 `c1d5e4b8aad618e0ebcdca77accf700febf49c0b8d4861809d9034c20453a7c8`. B84 preservada: `f5aa780febb22fdba739842046960a539bccba487ccd19199f473513c8fc006e`. Salva e reaberta na mesma janela, PID 11304, porta 9876, cena `SALVADOR | ESBOCO OFICIAL`.

Alteração de seis malhas: corpo do apoio da encosta, capitel, ressalto transversal, caixilhos, vidros e pilastras associadas. Corpo passou de 6,940002 para 11,400001 unidades no eixo transversal local, preservando X/Z e transforms. A largura adotada vem do contorno lateral da parede superior existente, **não de levantamento métrico**. É `ADAPT_LOCAL`, `APPROXIMATE`, `replacement_required: true`, recurso `REPLACE_BEFORE_RELEASE`. Fotografias dão suporte qualitativo à maior largura do conjunto; não certificam 11,40 m.

A torre da Cidade Baixa permaneceu no mesmo local, sem alteração. Não houve mudança em terreno, SSOT, comprimento da ponte, piso do saguão ou cabines. A cena ainda não reproduz corretamente as proporções completas solicitadas. **Não declarar o saguão corrigido ou dimensões reais certificadas.**

## Conferência documental do saguão e das duas torres

Pranchas SUCOP 2023 já catalogadas: 17 (Cidade Alta), 12 (Cidade Baixa), 23 (cortes). Foram renderizadas e inspecionadas visualmente; as cotas AutoCAD não estão todas presentes na extração de texto. Imagens de desenvolvimento em `artifacts/lacerda-proportions/`; PDFs brutos permanecem fora do Git comum em `world-reference/mvp-centro-lacerda/research-20261006-issue22/`.

| Planta | Elemento explicitamente identificado | Área impressa |
|---|---|---:|
| 17 | Salão superior | 117,50 m² |
| 17 | Circulação de saída | 86,61 m² |
| 17 | Circulação de entrada | 61,93 m² |
| 17 | Entrada / saída | 15,17 / 20,10 m² |
| 17 | Acesso à torre pela passarela | 214,74 m² |
| 12 | Saguão inferior | 265,56 m² |
| 12 | Circulação do túnel | 90,99 m² |

**117,50 m² não é a área do conjunto superior completo.** Não obter largura/profundidade de um retângulo dividindo essa área por uma dimensão escolhida. A planta mostra circulação ao redor da região da torre e dependências distintas do salão. O saguão atual simplificado não representa esse contorno completo.

A prancha 12 mostra ligação inferior por túnel entre o saguão frontal e a torre junto à encosta. A prancha 17 mostra a ligação superior por passarela entre dois conjuntos de torre, com plantas de formas/orientações diferentes. Portanto, a reconstrução deve tratar **ambas as conexões e os quatro equipamentos**, conforme requisito confirmado do projeto; não duplicar duas cabines no mesmo volume como substituto da organização arquitetônica. Símbolos de portas/acesso nas pranchas não fornecem, sozinhos, W/D/H ou contagem de cabines instaladas por peça da cena.

São cotas documentais úteis na planta superior: cadeias 5,20 / 1,99 / 2,20, circulação transversal 2,47 / 2,40 e trechos frontais 3,13 / 3,07 / 3,17. Precisam ser associados aos respectivos planos de parede, não usados como dimensões globais do saguão. O carimbo de escala não substitui essas cotas. Projeto de restauração não é as-built da instalação de elevadores.

## Divergência que permanece

O piso genérico superior atual mede aproximadamente 11,00 × 18,60 unidades locais; a passarela livre mede aproximadamente 55,538544 no eixo longitudinal. O nome legado “28.71 x 6.00m” não corresponde à extensão da malha. A referência histórica de vão 28,71 m não autoriza recortar 26,83 unidades e atribuí-las ao saguão: endpoints, contornos e implantação devem ser reconciliados.

Registro arquitetônico XY permanece não aceito conforme `docs/research/LACERDA_B80_CONTROLLED_REGISTRATION_2026-10-06.md`. Não existe transformação arquitetônica aprovada apoiada em três controles físicos independentes. Fixar a torre da Cidade Baixa preserva uma âncora, mas não determina sozinho a posição do conjunto superior, orientação/escala e conexão à praça. Fotografias em perspectiva não resolvem essa transformação métrica.

Não foi redimensionado o saguão nesta revisão. O próximo ajuste deve distinguir salão, circulações, bloco superior e torre da encosta, confrontar o contorno documental com os apoios reais da cena e preservar a implantação geográfica. Nenhuma B86 foi criada apenas para registrar essa investigação.

## Validação e limites

`application.json` registra antes/depois das seis meshes; 6.292 objetos restantes preservados na comparação de estado e os 70 objetos proxy B82 mantidos. `validation.json` confirmou persistência após reabertura, nenhuma face degenerada nas seis meshes e nenhuma nova penetração local dessas meshes contra 1.947 amostras superiores / 3.206 inferiores das rotas candidatas. **Esse teste não aprova o trajeto inteiro, poço, cabine ou arquitetura real.**

Proveniência das duas fotos fornecidas pelo usuário em `photo_evidence.json` e registros centrais. Autor, licença e data de captura desconhecidos; `DEV_REFERENCE_ONLY`, sem promoção para produção. Fontes SUCOP continuam catalogadas como referências de desenvolvimento. SSOT preservado.

`LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`; 27 testemunhas históricas `UNRESOLVED`; movimento histórico desabilitado. GAMEPLAY_PROXY B82 separado e aproximado, sem promoção. B76–B84 preservadas. Lapa, Campo da Pólvora, Dique e Fonte Nova não foram alterados. Nenhum npm, build, suíte geral, commit, push ou exportação de produção.
