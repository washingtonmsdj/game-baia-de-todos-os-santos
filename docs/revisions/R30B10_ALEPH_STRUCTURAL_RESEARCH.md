# R30B10 — Pesquisa estrutural do Elevador Lacerda

Pesquisa visual concluída em 29/09/2026–30/09/2026 com o Aleph pinado em `Belluxx/Aleph@d24c61507481a91a0dd6afac4f97626a4e5ea780`. Esta revisão é um handoff para a próxima implementação no Blender; não modifica o `.blend`, o terreno ou o runtime.

## Evidência principal

- A fotografia fornecida pelo usuário (`codex-clipboard-c8532ea7-e128-4e6d-a582-e50a9105ad70.png`) confirma a peça que faltava: um apoio vertical largo no lado oposto à torre com venezianas. Ele funciona visualmente como um pilar/fundação independente, com corpo em forma de parede, base descendo para a encosta e encontro superior com a passarela.
- A vista Aleph de `Ladeira da Montanha` em `-12.97445211799565, -38.51327607728878`, panorama `mG65in9kOUJd821rYJscVQ`, mostra a torre, o intradorso da passarela, o vão sobre a via e a relação do conjunto com o grande muro de contenção. A vista direcional está catalogada como `elevador-lacerda-oblique_right-4ba71f16af8d`.
- A vista Aleph inferior `elevador-lacerda-detail-6e9796b71968` registra a marquise/entrada, o intradorso com luminárias circulares, a torre e o muro de contenção próximos ao acesso da Cidade Baixa.
- As vistas Commons já catalogadas continuam sendo o controle para fachadas, galerias, torre e acessos. Street View/Aleph permanece referência temporária e restrita.

## Elementos permanentes a reproduzir

1. **Apoio oposto à torre:** volume largo e vertical, independente da torre principal, com leitura de pilar/fundação; não reduzir a uma coluna fina. A geometria deve descer até a encosta e fechar o encontro com a extremidade esquerda da passarela.
2. **Torre principal:** fuste estreito e alto, nervuras verticais, grupos repetidos de venezianas e coroamento/antena. O alinhamento deve ser vertical e separado do apoio oposto.
3. **Passarela elevada:** galeria superior envidraçada com módulos repetidos, molduras e ritmo regular; faixa externa inferior com guarda-corpo/friso vazado; viga/intradorso inferior profundo e contínuo atravessando o vão.
4. **Encontros e acessos:** marquises e volumes de entrada da Cidade Baixa e da Cidade Alta, mantendo os vãos e a continuidade estrutural antes de adicionar decoração.
5. **Entorno imediato:** muro de contenção de pedra, encosta, piso/calçada, praça superior e praça inferior. A relação espacial entre passarela, apoio, torre e ladeira é mais importante que props isolados.

## Elementos que devem ser excluídos nesta fase

Pessoas, ônibus, caminhões, carros, barracas, vendedores, lixo, tapumes, máquinas de obra, faixas temporárias, iluminação natalina e cabos aéreos vistos nas capturas. No ponto de ônibus, manter apenas abrigo, postes/sinalização e implantação permanente; os demais objetos ficam para uma camada posterior.

## Decisões de modelagem para o Astra

- Criar o apoio oposto como objeto estrutural próprio, com material e pivô independentes, ligado semanticamente à passarela e ao terreno, sem fundi-lo à torre.
- Modelar primeiro silhueta, vãos, espessura do intradorso e encontros dos apoios; depois galeria, venezianas, molduras e materiais.
- Manter torre, apoio oposto, passarela, galeria envidraçada, marquises, acessos e elementos de entorno em coleções/objetos separados para LOD, colisão e futuras correções.
- Vidros devem ser transparentes e separados das molduras; o apoio e o intradorso devem permanecer opacos.
- As dimensões métricas exatas do apoio oposto não foram medidas nas referências. Registrar como `NEEDS_REVIEW`/`ADAPT_LOCAL` e ajustar pela escala georreferenciada e pelo terreno existente; não inventar uma cota apenas para fechar a imagem.

## Proveniência e limites

As imagens Aleph/Google Street View estão registradas no manifesto como `source_type=aleph_reference`, `usage_class=TEMPORARIA` e `license_status=restricted`. Elas servem para inspeção e comparação visual, não para textura, fotogrametria ou asset distribuível. A foto anexada pelo usuário é orientação visual direta, sem promoção a mídia aprovada. A referência estrutural está suficientemente consolidada para iniciar a implementação no Astra.
