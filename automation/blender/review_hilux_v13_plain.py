"""Vista neutra para separar sombra da forma real da chapa."""
import bpy
from pathlib import Path
r=Path(__file__).resolve().parents[2];s=bpy.context.scene
sh=s.display.shading
original_shadows=sh.show_shadows
exec(compile((r/'automation/blender/review_hilux_body_v13.py').read_text(encoding='utf-8').replace('sh.show_shadows = True','sh.show_shadows = False'),str(r/'automation/blender/review_hilux_body_v13.py'),'exec'))
sh.show_shadows=original_shadows
for name in ['cacamba','encontro-cabine','frente']:
    p=r/f'artifacts/vehicles/rondesp/v13-carroceria-{name}.png';p.replace(p.with_name(p.stem+'-neutra.png'))
