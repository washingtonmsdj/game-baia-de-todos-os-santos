from pathlib import Path
p=Path(__file__).with_name('verify_coastal_transition_b59.py')
code=p.read_text(encoding='utf8').replace('salvador_lacerda_r30b59_encosta_transicao_continua.blend','salvador_lacerda_r30b60_plataformas_costeiras.blend').replace('B59 | GAMEPLAY TERRAIN HQ | encosta contínua','B60 | GAMEPLAY TERRAIN HQ | plataformas costeiras').replace('B59 | COLLISION | terreno encosta contínua','B60 | COLLISION | plataformas costeiras').replace('B59 | ROAD VISUAL |','B60 | ROAD VISUAL |').replace('coastal-transition-b59-check-v1','coastal-transition-b60-check-v1').replace('coastal_transition_r30b59_check.json','coastal_transition_r30b60_check.json')
exec(compile(code,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
