# Lacerda — revisão do conjunto documental, 07/10/2026

## Estado efetivo

**Correção integral ainda não concluída. Nenhuma alteração adicional de cena nesta investigação.** B85 permanece aberta e preservada. A B85 ampliou somente seis malhas do apoio; não redimensionou saguão/passarela nem corrigiu a distribuição das cabines. Não apresentar essa revisão como reprodução dimensional da planta.

A orientação mais recente do usuário permite rever também a implantação da torre da Cidade Baixa. A exigência anterior de mantê-la fixa deixou de ser restrição para trabalhos futuros. A decisão é reconstruir corretamente a relação arquitetônica antes de reconciliar sua implantação no mapa. Isso não autoriza alterar silenciosamente o SSOT ou apresentar coordenadas candidatas como geografia comprovada.

## O que a inspeção confirmou

- Planta superior SUCOP 17: o salão de 117,50 m² é somente parte do conjunto. Há circulações de entrada e saída de 61,93 e 86,61 m², além de outros recintos e acessos. Não obter largura/comprimento de todo o conjunto a partir da área do salão.
- Planta inferior SUCOP 12: saguão de 265,56 m² ligado à outra torre por circulação de túnel de 90,99 m². A ligação inferior precisa integrar a reconstrução; não basta corrigir a passarela superior.
- As direções das torres e da ligação superior não coincidem integralmente na planta. Comparação vetorial preliminar entre um segmento do contorno da torre (curva 1682) e um segmento longitudinal do acesso (curva 1780) resulta em 9,642358°. É um diagnóstico documental, **não a rotação final a aplicar a toda a torre**, porque os planos correspondentes da cena ainda precisam ser identificados.
- A cadeia de cotas superiores é **5,20 / 1,99 / 2,20 m**. A leitura anterior de 2,00 foi corrigida após renderização ampliada. Os traços das linhas de dimensão possuem interrupções/terminações: seu comprimento bruto não deve substituir a distância entre linhas de chamada.
- A ponte atual mede aproximadamente 55,54 unidades no eixo local apesar do nome legado conter 28,71. O piso genérico superior mede aproximadamente 11,00 × 18,60. Não existe correspondência aceita que transforme essas duas caixas no conjunto completo da prancha.

## Quatro elevadores: geometria legada versus protótipo

O inventário ao vivo localizou pisos nomeados `CABINE 1` a `CABINE 4`. Todos ocupam aproximadamente X −64,039 a −61,589 no referencial de medição existente. Seus centros Y estão distribuídos lado a lado; cabines 1/2 em Z ≈11,07 e 3/4 em Z ≈70,07. Portanto, a posição desses quatro candidatos representa uma única região de torre, não demonstra dois pares distribuídos entre as duas torres documentais.

Separadamente, o script `model_lacerda_gameplay_proxy_b82.py` constrói **uma** cabine funcional B82, com um piso e um conjunto de estados/portas. Quatro folhas ou dois desembarques não equivalem a quatro equipamentos. A existência dos nomes históricos também não certifica quatro instalações corretas.

Não foram criadas cabines adicionais nem deslocados esses objetos nesta investigação. Um inventário por palavras não é suficiente para provar ausência total de uma geometria de túnel sem nome; a correspondência física desse percurso continua pendente.

## Dados e limites

Dados auditáveis:

- `docs/reports/blender/lacerda-proportions-b85/four_elevators_inventory.json` — inspeção read-only, PID 11304;
- `four_elevators_summary.json` no mesmo diretório — posições legadas e distinção do proxy;
- `plan_review_20261007.json` — pontos vetoriais, áreas, cotas e hashes das quatro novas fotos;
- `artifacts/lacerda-proportions/sheet12-vectors.json` e `sheet17-vectors.json` — derivados dos PDFs, sem promoção para produção.

As quatro novas imagens foram catalogadas como `DEV_REFERENCE_ONLY`; autoria/licença/captura desconhecidas. Texto sobreposto nas fotografias não foi adotado como evidência histórica ou dimensional. Pranchas, fotos e geometria de gameplay continuam distinguíveis.

Não temos **todas** as dimensões executadas. Há cotas arquitetônicas suficientes para estudar/reconstruir partes, mas faltam a associação completa dos contornos e níveis ao modelo e dimensões atuais da instalação. O registro das plantas no SSOT permanece não aceito. Esse estado não deve ser apresentado como falta de autorização do usuário: é trabalho de correspondência geométrica ainda não fechado.

Próxima alteração deve resolver o conjunto em planta: contorno do saguão superior, ambas as torres e sua orientação, passarela, saguão inferior e túnel. Preservar a transformação derivada e os controles; verificar depois implantação, apoio no terreno, conexões e colisões. Não abreviar o problema esticando o saguão pelo excesso de comprimento da ponte ou girando apenas a casca sem suas dependências.

Histórico preservado: B76–B85, SSOT, 27 testemunhas `UNRESOLVED`, `LACERDA_VERTICAL = BLOCKED_EXTERNAL_EVIDENCE`, movimento histórico desabilitado, proxy B82 aproximado. Nenhuma exportação de produção, mudança territorial, B86 ou nova alegação de gameplay aprovado.
