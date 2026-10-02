"""Registra comparação localizada após reabertura; não aprova a cidade inteira."""
import bpy,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
runpy.run_path(str(root/'automation/blender/conferir_tower_galleries_r35.py'))
path=root/'docs/reports/blender/torre_galerias_r30b35.json';r=json.loads(path.read_text(encoding='utf8'))
r['context_structure_refinement']['visual_review']='reviewed_modeling_candidate'
r['palace_facade_refinement']['visual_review']='reviewed_modeling_candidate'
r['visual_comparison']={'status':'partial_not_approved','views':['artifacts/palacio-rio-branco/r30b35_frente.png','artifacts/palacio-rio-branco/r30b35_apoio.png','artifacts/palacio-rio-branco/r30b35_conjunto.png','artifacts/palacio-rio-branco/r30b35_panorama_completo.png'],'changes_confirmed':['Apoio alinhado à parede/laje e perfil posterior escalonado; sobreposição antiga arquivada.','Galerias com interiores desocupados de terreno/proxy, confirmados em 39 amostras por malha.','Portal com colunas sobre pedestais; cornija/dentículos não atravessam o arco central.','Planta/cota do palácio e malha da praça preservadas.'],'remaining_gaps':['Jardins, terraços e colunata abaixo do palácio ainda não reproduzidos.','Esculturas, ornatos figurativos e fachada posterior não têm detalhe legível suficiente para atestar fidelidade.','Entorno contém esboços; não considerar a cidade ou o relevo inteiro concluídos.','Materiais procedurais exigem bake/perfil interoperável antes de exportar; runtime não atualizado.'],'dimensions_status':'candidate; nenhuma dimensão fotográfica apresentada como levantada','runtime_validated':False}
path.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Mostra a frente/ala na mesma janela; apenas enquadramento, sem alterar a cena.
r34=json.loads((root/'docs/reports/blender/palacio_rio_branco_r30b34.json').read_text(encoding='utf8'));T=Matrix(r34['palace']['frame_world'])
target=T@Vector((0,-6,12));eye=T@Vector((-38,47,27))
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        space=area.spaces.active;space.clip_end=3000;space.region_3d.view_location=target;space.region_3d.view_distance=(eye-target).length;space.region_3d.view_rotation=(target-eye).to_track_quat('-Z','Y');space.region_3d.view_perspective='PERSP'
print(json.dumps({'reopened':True,'protected':len(r['protected_signatures']),'gallery_samples_source':39,'gallery_samples_proxy':r['localized_scene_review']['proxy_clear_room_samples'],'status':'modeling_candidate'},ensure_ascii=False))
