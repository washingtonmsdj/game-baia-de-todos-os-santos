"""Personagem controlável ao vivo: F3 → BOAS Jogar Lacerda (proxy)."""
import bpy, blf, math, json, sys, time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/world'))
from lacerda_gameplay_proxy import ProxyController
CONFIG=json.loads((ROOT/'world/areas/mvp-centro-lacerda/lacerda-gameplay-proxy.json').read_text(encoding='utf8'))


def world(p):
    a=CONFIG['local_frame']['angle'];c,s=math.cos(a),math.sin(a);o=CONFIG['local_frame']['origin_xy']
    return Vector((o[0]+c*p[0]-s*p[1],o[1]+s*p[0]+c*p[1],p[2]))


def sync(controller):
    scene=bpy.data.scenes[CONFIG['scene_name']]
    for ob in scene.objects:
        tag=ob.get('boas_proxy_dynamic')
        if not tag:continue
        p=json.loads(ob['boas_proxy_local_center'])
        if tag=='player':ob.location=world(controller.player);continue
        if tag.startswith('cabin_'):p[2]+=controller.car_z
        if 'door' in tag:
            landing=ob.get('boas_proxy_landing')
            side=ob.get('boas_proxy_side',1)
            active=(controller.station==landing if landing else (controller.station==('upper' if side==1 else 'lower')))
            p[1]+=ob.get('boas_proxy_leaf',1)*.83*(controller.openness if active else 0.)
        ob.location=world(p)


def hud(operator):
    blf.size(0,17);blf.color(0,1.,1.,1.,1.)
    lines=['BAY OF ALL SAINTS · LACERDA · GAMEPLAY PROXY',
           'WASD / ↑↓ mover · ←→ olhar · botão direito + mouse olhar · E chamar/viajar · Esc sair',
           f'{operator.controller.mode} · {operator.controller.message}',
           'Aproximação temporária. Fidelidade histórica continua pendente.']
    for i,line in enumerate(lines):blf.position(0,20,operator.area.height-45-i*25,0);blf.draw(0,line)


class BOAS_OT_proxy_play(bpy.types.Operator):
    bl_idname='boas.proxy_play';bl_label='BOAS Jogar Lacerda (proxy)';bl_description='Personagem com colisão e elevador intertravado; não certifica arquitetura'

    @classmethod
    def poll(cls,context):return context.scene.name==CONFIG['scene_name'] and context.area is not None and context.area.type=='VIEW_3D'

    def invoke(self,context,event):
        active=bpy.app.driver_namespace.get('boas_proxy_operator')
        if active:
            try:active.finish()
            except ReferenceError:bpy.app.driver_namespace.pop('boas_proxy_operator',None)
        self.area=context.area;self.space=context.space_data;self.window=context.window
        self.controller=ProxyController(CONFIG);self.keys=set();self.yaw=math.pi;self.pitch=0.;self.mouse=None
        self.timer=context.window_manager.event_timer_add(1/60,window=context.window)
        self.handler=bpy.types.SpaceView3D.draw_handler_add(hud,(self,),'WINDOW','POST_PIXEL')
        self.previous_overlay=self.space.overlay.show_overlays;self.space.overlay.show_overlays=False
        self.previous_shading=self.space.shading.type;self.space.shading.type='SOLID';self.space.shading.color_type='MATERIAL'
        self.finished=False;self.last=time.monotonic()
        context.window_manager.modal_handler_add(self);bpy.app.driver_namespace['boas_proxy_operator']=self
        bpy.data.objects['B82 | personagem proxy'].hide_set(True,view_layer=context.view_layer)
        sync(self.controller);self.view();return {'RUNNING_MODAL'}

    def view(self):
        a=CONFIG['local_frame']['angle']+self.yaw
        direction=Vector((math.cos(a)*math.cos(self.pitch),math.sin(a)*math.cos(self.pitch),math.sin(self.pitch)))
        eye=world(self.controller.player)+Vector((0,0,1.63))
        region=self.space.region_3d;region.view_perspective='PERSP';region.view_rotation=direction.to_track_quat('-Z','Y')
        region.view_distance=1.;region.view_location=eye+direction
        self.area.tag_redraw()

    def modal(self,context,event):
        if self.finished:return {'FINISHED'}
        if event.type=='ESC' and event.value=='PRESS':self.finish();return {'FINISHED'}
        if event.type in {'W','A','S','D','UP_ARROW','DOWN_ARROW','LEFT_ARROW','RIGHT_ARROW','LEFT_SHIFT','RIGHT_SHIFT'}:
            if event.value=='PRESS':self.keys.add(event.type)
            elif event.value=='RELEASE':self.keys.discard(event.type)
            return {'RUNNING_MODAL'}
        if event.type=='E' and event.value=='PRESS':self.controller.request();return {'RUNNING_MODAL'}
        if event.type=='RIGHTMOUSE':self.mouse=(event.mouse_x,event.mouse_y) if event.value=='PRESS' else None;return {'RUNNING_MODAL'}
        if event.type=='MOUSEMOVE' and self.mouse:
            self.yaw-=(event.mouse_x-self.mouse[0])*.004;self.pitch=max(-1.,min(1.,self.pitch+(event.mouse_y-self.mouse[1])*.004));self.mouse=(event.mouse_x,event.mouse_y);self.view();return {'RUNNING_MODAL'}
        if event.type=='TIMER':
            now=time.monotonic();dt=min(.10,now-self.last);self.last=now
            for _ in range(max(1,math.ceil(dt/(1/60)))):
                step=dt/max(1,math.ceil(dt/(1/60)))
                self.yaw+=step*1.6*(('LEFT_ARROW' in self.keys)-('RIGHT_ARROW' in self.keys))
                forward=int(bool({'W','UP_ARROW'}&self.keys))-int(bool({'S','DOWN_ARROW'}&self.keys))
                sideways=int('D' in self.keys)-int('A' in self.keys)
                length=max(1.,math.hypot(forward,sideways));speed=4. if {'LEFT_SHIFT','RIGHT_SHIFT'}&self.keys else 2.5
                dx=(forward*math.cos(self.yaw)+sideways*math.sin(self.yaw))*speed*step/length
                dy=(forward*math.sin(self.yaw)-sideways*math.cos(self.yaw))*speed*step/length
                self.controller.update(step);self.controller.move(dx,dy,0.)
            sync(self.controller);self.view();return {'RUNNING_MODAL'}
        if event.type in {'WINDOW_DEACTIVATE'}:self.keys.clear();self.mouse=None
        return {'PASS_THROUGH'}

    def finish(self):
        if self.finished:return
        bpy.context.window_manager.event_timer_remove(self.timer)
        bpy.types.SpaceView3D.draw_handler_remove(self.handler,'WINDOW')
        self.space.overlay.show_overlays=self.previous_overlay;self.space.shading.type=self.previous_shading
        scene=bpy.data.scenes.get(CONFIG['scene_name'])
        if scene:bpy.data.objects['B82 | personagem proxy'].hide_set(False,view_layer=scene.view_layers[0])
        self.finished=True;bpy.app.driver_namespace.pop('boas_proxy_operator',None)


class BOAS_PT_proxy_panel(bpy.types.Panel):
    bl_label='Lacerda · protótipo funcional';bl_idname='BOAS_PT_proxy_panel'
    bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='BOAS'
    @classmethod
    def poll(cls,context):return context.scene.name==CONFIG['scene_name']
    def draw(self,context):
        layout=self.layout;layout.label(text='GAMEPLAY_PROXY · APPROXIMATE')
        layout.operator('boas.proxy_play',text='Jogar · entrada superior',icon='PLAY')
        layout.label(text='WASD mover · setas olhar')
        layout.label(text='E chamar / viajar · Esc sair')
        layout.label(text='Ida e volta até Cairu')
        layout.label(text='Substituição futura obrigatória')


def register():
    active=bpy.app.driver_namespace.get('boas_proxy_operator')
    if active:
        try:active.finish()
        except ReferenceError:bpy.app.driver_namespace.pop('boas_proxy_operator',None)
    for cls in (BOAS_OT_proxy_play,BOAS_PT_proxy_panel):
        previous=getattr(bpy.types,cls.__name__,None)
        if previous:bpy.utils.unregister_class(previous)
        bpy.utils.register_class(cls)
    print('BOAS: painel registrado; F3 → BOAS Jogar Lacerda (proxy)')


if __name__=='__main__':register()
