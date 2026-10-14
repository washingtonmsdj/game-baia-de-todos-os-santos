# Lacerda — limites dos vestíbulos superiores B97 — 07/10/2026

B97 modelada, salva e reaberta na única janela Blender PID16912/MCP9876. Fonte: `blender/salvador_lacerda_r30b97_limites_vestibulos_superiores.blend`. SHA-256 `0454f0cec2d8d65b4f127f635d59a217f4b62bae83d43d5e9769b541581543b5`. B76–B96 intactas.

## Modelagem e evidência

Dois limites em L acrescentados às bordas dos vestíbulos `SAÍDA 20,10m²` e `ENTRADA 15,17m²` da prancha SUCOP17. O contorno relativo usa os mesmos controles B88, sem novo SSOT, mudança de escala/origem ou ajuste do terreno. As aberturas a leste continuam intencionalmente livres. O inventário espacial B96 não encontrou proteção nessas bordas; o guarda existente perto da torre nova não corresponde a estes vestíbulos.

A nota documental “DEMOLIR FECHAMENTO EM ALVENARIA — MANTER GUARDA-CORPO” comprova a intenção do projeto2023. **Não comprova execução atual, seção, altura ou material do guarda-corpo.** Os dois volumes são massing de proteção, com seção adotada de 0,18m e altura candidata de 1,10m: `status=GAMEPLAY_PROXY`, `accuracy=APPROXIMATE`, `replacement_required=true`. Não apresentar essas medidas como levantamento real ou guarda certificado. Material sólido serve à leitura de massa; tipologia final ainda depende de evidência. A implantação absoluta permanece candidata.

As novas peças reutilizam a coleção superior existente e possuem proveniência centralizada, vínculo ao piso-fonte e `boas_collision_enabled=false`. Não substituem/dobram o GAMEPLAY_PROXY B82 nem habilitam navegação histórica. Nenhuma arquitetura existente foi removida, ocultada, deformada ou reparentada.

## Conferência

- Duas meshes fechadas, sem faces degeneradas, arestas não manifold ou winding incoerente.
- 603 componentes anteriores preservados por assinatura de geometria, transform e materiais. 6315 objetos existentes preservados no escopo de dados/transform/visibilidade/parent durante a aplicação.
- 108 amostras do disco de apoio raio0,30 + skin0,015 sobre o piso real, mais 12 conferências de afastamento das guardas. Nenhuma tampa nova cruza os acessos orientais.
- Dois primeiros pontos de sondagem ficaram perto demais da guarda e foram rejeitados. Novas amostras foram posicionadas no interior livre dos vestíbulos; guarda/raio/skin não mudaram. Distâncias registradas em `rejected_initial_samples`. Isso não constitui autorização de rota ou ajuste de arquitetura para passar teste.
- É **QA local de apoio/limite**, não sweep volumétrico completo da cena, controller, CCD da cabine ou aprovação do percurso Tomé–Mercado. Não foi repetido teste de poço/cabine.
- Fonte reaberta/hash conferido; vistas reais `artifacts/lacerda-live-diagnostic/b97-saida.png`, `b97-entrada.png`, `b97-map.png`. A janela termina com mapa completo e terreno visível, sem edição pendente.

## Estado preservado

`LACERDA_VERTICAL=BLOCKED_EXTERNAL_EVIDENCE`; `movement_enabled=false`; `27 testemunhas B80=UNRESOLVED/PRESERVED`; `GAMEPLAY_PROXY B82=PRESERVED`; `replacement_required=true`; `EXPANDED_MAP=GREYBOX`; `production_ready=false`. Nenhuma exportação/produção, fachada nova ou alteração de Lapa/Dique/Fonte Nova.

Próximo trecho: reconciliar os pilares e aberturas da frente superior com a linha oblíqua e os acessos da prancha17. O inventário registra a frente candidata antiga em cinco vãos: não tomar sua disposição como comprovação das portas reais, nem deslocar a cidade para acomodá-la. Guardas e suas seções continuam candidatas até evidência independente.
