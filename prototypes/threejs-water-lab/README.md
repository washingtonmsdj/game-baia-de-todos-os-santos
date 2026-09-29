# Three.js Foundation Lab

Protótipo runtime de **Bay of All Saints** para validar terreno, água, tráfego, navegação básica e integração de assets antes da engine final.

## Rodar

```bash
npm install
npm run dev
```

Validação estrutural + build:

```bash
npm run check
```

## Ônibus Integra Salvador

O laboratório possui staging do asset `vehicle-integra-salvador-01`.

Contrato da fonte:
- arquivo: `yellow city bus 3d model.glb`;
- SHA-256: `F3D5DEE69DCAB15379817A9AE13E562DF8023FD7AF38E8B6A0CDB4742AB650A2`;
- 67 geometrias;
- 992.121 vértices;
- 1.954.141 triângulos;
- dimensões de staging: 12,0 × 2,55 × 3,25 m.
O GLB pesado é **fonte de autoria**, não asset runtime final. Sem o binário local, o protótipo usa um proxy leve automaticamente.

Para disponibilizar o GLB real localmente:

```bash
npm run stage:bus
```

O stager procura `BOAS_INTEGRA_BUS_GLB` ou `artifacts/incoming/`, valida tamanho + SHA-256 e copia para `public/assets/vehicles/integra-salvador/`. Esse `.glb` é ignorado pelo Git.

No runtime:
- `B`: mostra/oculta o ônibus;
- HUD informa `PROXY` ou `GLB AUTORIA`;
- staging atual usa o eixo do grafo R30A.7, ainda sem lane binding final;
- `runtimeReady` permanece `false` até LOD, rig de rodas, collider e materiais runtime.

## Smoke test

Com Chrome em CDP e o Vite ativo:

```bash
TARGET_URL=http://127.0.0.1:5187/ npm run smoke
```

O smoke valida fundação, tráfego, água/mergulho, barco e contrato do ônibus, incluindo o toggle de visibilidade.
