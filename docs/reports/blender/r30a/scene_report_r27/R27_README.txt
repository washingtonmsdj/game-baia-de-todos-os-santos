SALVADOR / ELEVADOR LACERDA MVP — R27

Objetivo desta revisao:
- preservar a geometria arquitetonica existente;
- adicionar marcadores de QA para o percurso jogavel;
- adicionar camera de dossie/revisao;
- criar um rig de luz opcional, desligado para render por seguranca;
- registrar pendencias sem renomear em massa os milhares de objetos existentes.

Contagens observadas antes da revisao:
{
  "objects": 4657,
  "meshes": 4137,
  "materials": 135,
  "collections": 32,
  "curves": 412,
  "lights": 1,
  "cameras": 54
}

Pendencias conhecidas:
- Entrada superior: footprint/implantacao ainda deve ser confirmado por levantamento.
- Ladeira: perfil funcional registrado como 2-14%; nao tratar como levantamento viario definitivo.
- Praca Castro Alves e Ladeira da Conceicao: trechos viarios omitidos por artefato de escarpa do DEM.
- Cota da saida inferior e terreno local continuam aproximacoes do MVP.
- Fachadas e mobiliario: referencias fotograficas externas, sem certificacao dimensional completa.

Uso:
1. A colecao '30 MVP | QA E GUIAS R27' contem apenas marcadores e camera de revisao.
2. A colecao '31 LUZ | PREVIEW R27' contem luzes opcionais; hide_render=True por padrao.
3. Nao foi feita renomeacao automatica dos objetos .001/.002 para evitar quebrar referencias.
4. Antes de exportar para engine, executar consolidacao/instanciamento em uma revisao dedicada.
