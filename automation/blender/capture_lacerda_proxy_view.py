"""Captura GPU da câmera do controller na sessão existente, sem nova cena."""
import bpy, gpu, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
operator=bpy.app.driver_namespace['boas_proxy_operator']
area=operator.area; space=operator.space
region=next(r for r in area.regions if r.type=='WINDOW')
off=gpu.types.GPUOffScreen(1000,650)
try:
    with bpy.context.temp_override(window=operator.window,area=area,region=region):
        operator.view()
        off.draw_view3d(bpy.context.scene,bpy.context.view_layer,space,region,
                       space.region_3d.view_matrix,space.region_3d.window_matrix,
                       do_color_management=True)
        with off.bind():
            pixels=gpu.state.active_framebuffer_get().read_color(0,0,1000,650,4,0,'FLOAT')
        image=bpy.data.images.new('B82 captura temporária',width=1000,height=650)
        pixels.dimensions=1000*650*4;image.pixels.foreach_set(pixels)
        target=ROOT/'artifacts/lacerda-gameplay-proxy/controller-gpu.png'
        image.filepath_raw=str(target);image.file_format='PNG';image.save()
        bpy.data.images.remove(image)
        print(json.dumps({'image':str(target),'active':not operator.finished,'mode':operator.controller.mode,'position':operator.controller.player}))
finally:off.free()
