# Three.js Foundation Lab

Protótipo runtime de **Bay of All Saints** para validar terreno, água, tráfego, navegação básica e integração de assets antes da engine final.

## Cidade oficial

O runtime carrega a camada visual completa da revisão oficial `salvador_lacerda_mvp_terreno_entrada_livre_chatgpt_v1_r30a11_pedestrian_nav.blend` em `public/assets/city/salvador_lacerda_mvp_r30a11_full.glb`. O asset inclui terreno visual, vias, waterfront, edifícios, Elevador Lacerda, Mercado Modelo e Prefeitura/Palácio Rio Branco nas coordenadas do projeto. A fundação JSON permanece como suporte de altura, colisão e navegação do jogador.

## Rodar

```bash
npm install
npm run dev
```

Validação estrutural + build:

```bash
npm run check
```

## Ônibus Torino 31065 / Integra Salvador

O laboratório possui staging do asset `vehicle-torino-salvador-31065`, exportado da revisão Blender v03 do ônibus modelado para o concept fornecido.

Contrato da fonte:
- arquivo: `onibus_torino_31065_v03.glb`;
- SHA-256: `F3F9BE5E2B6DF944677348EAD51F4A96D4607933F594DCFFF60BA45A752A7EB7`;
- 480 geometrias;
- dimensões de staging: 12,0 × 2,55 × 3,25 m.
O GLB pesado é **fonte de autoria**, não asset runtime final. Sem o binário local, o protótipo usa um proxy leve automaticamente.

Para disponibilizar o GLB real localmente:

```bash
npm run stage:bus
```

O stager procura `BOAS_INTEGRA_BUS_GLB` ou `artifacts/incoming/`, valida tamanho + SHA-256 e copia para `public/assets/vehicles/integra-salvador/`. Esse `.glb` é ignorado pelo Git.

No runtime:
- `B`: mostra/oculta o ônibus;
- todos os veículos do tráfego usam o mesmo Torino 31065, instanciado com a escala real de 12,0 × 2,55 × 3,25 m;
- HUD informa `PROXY` ou `GLB AUTORIA`;
- staging atual usa o eixo do grafo R30A.7, ainda sem lane binding final;
- `runtimeReady` permanece `false` até LOD, rig de rodas, collider e materiais runtime.

## Smoke test

Com Chrome em CDP e o Vite ativo:

```bash
TARGET_URL=http://127.0.0.1:5187/ npm run smoke
```

O smoke valida fundação, tráfego, água/mergulho, barco e contrato do ônibus, incluindo o toggle de visibilidade.
