# R30B.03 — exterior e acessos

Arquivo: `blender/salvador_lacerda_r30b03_exterior_acessos.blend`. R30B.02 preservada. Fonte ativa do runtime inalterada.

Prioridade solicitada: fachadas da Cidade Alta/Baixa, praça, laterais e acessos; suspender microdetalhes internos.

- Cidade Baixa: redução do bloco de platibanda acima da marquise, perfis da marquise e profundidade dos três portais. Passagens existentes mantidas abertas.
- Cidade Alta: coroamento escalonado e seis aberturas nas laterais do saguão, preservando pilares, vigas, piso e peitoril. Adaptação à malha atual (`ADAPT_LOCAL`), não levantamento métrico.
- Doze janelas laterais com recortes reais atrás dos caixilhos.
- Corrigidas normais dos sólidos de corte; reaplicados também os seis vãos frontais da R30B.02. A revisão anterior continha recortes que não tinham produzido abertura efetiva.
- Câmeras de revisão: `REV LAC | Praca Cidade Alta`, `REV LAC | Acesso Cidade Baixa`, `REV LAC | Lateral conjunto`.

Referências registradas: Commons 20250721125819 (entrada baixa, 2025), Webysther 20150907164641 (fachada alta e praça, 2015), além das fotos de 2025 já catalogadas. A foto 20250721125020 é contexto da baía, não evidência de acesso: não usar seu rótulo inicial `access` para aprovação de cobertura.

O patamar antigo em Z≈11 está na coleção 13 já oculta. Não foi deslocado nem reativado; o piso inferior corrente está em Z≈7,406. Não foi feita correção geográfica, DEM, percurso global ou runtime.

Inspeção visual das duas fachadas e aberturas laterais; arquivo salvo/reaberto. Capturas em `artifacts/lacerda/r30b03_*`. Fidelidade ainda parcial; não declarar os acessos completos ou o Hero aprovado. Próxima revisão deve conferir o encontro efetivo com praça/calçada na cena completa, sem criar ligação fictícia.

Scripts: `refine_lacerda_r30b03_exterior.py` e `repair_lacerda_r30b03_openings.py` em `automation/blender/`.
