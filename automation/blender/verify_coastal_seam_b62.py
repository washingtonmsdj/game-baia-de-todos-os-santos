from pathlib import Path
p=Path(__file__).with_name('verify_coastal_transition_b59.py')
code=p.read_text(encoding='utf8').replace('salvador_lacerda_r30b59_encosta_transicao_continua.blend','salvador_lacerda_r30b62_pavimento_costura_limpa.blend').replace('B59 | GAMEPLAY TERRAIN HQ | encosta contínua','B62 | GAMEPLAY TERRAIN HQ | pavimento e costura limpa').replace('B59 | COLLISION | terreno encosta contínua','B62 | COLLISION | pavimento e costura limpa').replace('B59 | ROAD VISUAL |','B62 | ROAD VISUAL |').replace('coastal-transition-b59-check-v1','coastal-transition-b62-check-v1').replace('coastal_transition_r30b59_check.json','coastal_transition_r30b62_check.json')
exec(compile(code,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
