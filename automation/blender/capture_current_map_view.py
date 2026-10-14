import bpy,json,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
report={}
try:
    import gpu
    area=next(ar for ar in bpy.context.window.screen.areas if ar.type=='VIEW_3D');space=area.spaces.active;region=next(r for r in area.regions if r.type=='WINDOW')
    report['viewport']={'shading':space.shading.type,'perspective':space.region_3d.view_perspective,'local_view':bool(space.local_view),'view_location':list(space.region_3d.view_location),'view_distance':space.region_3d.view_distance}
    width,height=1000,650;off=gpu.types.GPUOffScreen(width,height)
    try:
        with bpy.context.temp_override(window=bpy.context.window,area=area,region=region):
            off.draw_view3d(bpy.context.scene,bpy.context.view_layer,space,region,space.region_3d.view_matrix,space.region_3d.window_matrix,do_color_management=True)
            with off.bind():pixels=gpu.state.active_framebuffer_get().read_color(0,0,width,height,4,0,'UBYTE')
        pixels.dimensions=width*height*4;raw=bytes(pixels)
        def chunk(tag,data):return struct.pack('!I',len(data))+tag+data+struct.pack('!I',zlib.crc32(tag+data)&0xffffffff)
        scan=b''.join(b'\0'+raw[y*width*4:(y+1)*width*4] for y in reversed(range(height)))
        png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b'')
        filename=globals().get('BOAS_CAPTURE_FILENAME','restored-viewport.png')
        assert Path(filename).name==filename and filename.endswith('.png')
        target=ROOT/'artifacts/lacerda-live-diagnostic'/filename;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(png);report['screenshot']=str(target)
    finally:off.free()
except Exception as exc:report['capture_error']=str(exc)

print(json.dumps(report))
