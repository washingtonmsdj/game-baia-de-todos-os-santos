from pathlib import Path
p=Path(__file__).with_name('verify_coastal_transition_b59.py')
code=p.read_text(encoding='utf8').replace('salvador_lacerda_r30b59_encosta_transicao_continua.blend','salvador_lacerda_r30b61_pavimento_integrado.blend').replace('B59 | GAMEPLAY TERRAIN HQ | encosta contínua','B61 | GAMEPLAY TERRAIN HQ | pavimento integrado').replace('B59 | COLLISION | terreno encosta contínua','B61 | COLLISION | terreno e pavimento integrado').replace('B59 | ROAD VISUAL |','B61 | ROAD VISUAL |').replace('coastal-transition-b59-check-v1','coastal-transition-b61-check-v1').replace('coastal_transition_r30b59_check.json','coastal_transition_r30b61_check.json')
exec(compile(code,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
