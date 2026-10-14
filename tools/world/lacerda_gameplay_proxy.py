"""Controller provisório, neutro de engine. Não aprova arquitetura B80/B81."""
import math


def local_point(point, center, angle):
    c, s = math.cos(angle), math.sin(angle)
    x, y = point[0]-center[0], point[1]-center[1]
    return c*x+s*y, -s*x+c*y


def box_contact(p, box, radius=.30, height=1.80, skin=.015):
    """Cápsula vertical × caixa OBB; distância ao segmento axial da cápsula."""
    x, y = local_point(p, box['center'], box.get('angle', 0.))
    hx, hy = box['size'][0]/2, box['size'][1]/2
    z0 = box['center'][2]-box['size'][2]/2
    z1 = z0+box['size'][2]
    dx, dy = max(abs(x)-hx, 0.), max(abs(y)-hy, 0.)
    dz = max(z0-(p[2]+height-radius), (p[2]+radius)-z1, 0.)
    return math.sqrt(dx*dx+dy*dy+dz*dz) < radius+skin-1e-8


def floor_height(point, floor):
    x,y = local_point(point, floor['center'], floor.get('angle', 0.))
    if abs(x)>floor['size'][0]/2+1e-8 or abs(y)>floor['size'][1]/2+1e-8:
        return None
    return floor['center'][2] + x*floor.get('slope',0.)


class ProxyController:
    def __init__(self, config):
        self.config=config
        self.radius=.30; self.height=1.80; self.skin=.015; self.step=.25
        self.player=list(config['spawn']); self.player[2]+=self.skin
        self.velocity_z=0.; self.car_z=config['levels']['upper']; self.car_velocity=0.
        self.station='upper'; self.destination=None; self.mode='CLOSED'
        self.openness=0.; self.carrying=False; self.message='E: chamar elevador'
        self.support='upper_walkway'; self.events=[]; self.falls=0; self.elapsed=0.

    def in_cabin(self, p=None, full=True):
        p=p or self.player; margin=self.radius+self.skin if full else 0.
        return (abs(p[0])<self.config['cabin']['length']/2-margin
                and abs(p[1])<self.config['cabin']['width']/2-margin
                and abs(p[2]-self.car_z-self.skin)<.08)

    def portal_occupied(self):
        if self.station is None:return False
        z=self.config['levels'][self.station]
        if not z-self.height<self.player[2]<z+2.5:return False
        side=1 if self.station=='upper' else -1
        return abs(self.player[0]-side*self.config['cabin']['length']/2)<self.radius+self.skin+.16 and abs(self.player[1])<1.2

    def request(self):
        if self.mode in ('TRAVELLING','OPENING','CLOSING'):return False
        if self.in_cabin():
            if self.mode!='OPEN':return False
            self.destination='lower' if self.station=='upper' else 'upper'
            self.mode='CLOSING';self.message='Fechando portas';return True
        level=min(self.config['levels'],key=lambda k:abs(self.player[2]-self.config['levels'][k]))
        side=1 if level=='upper' else -1
        if abs(self.player[2]-self.config['levels'][level])>.20 or math.hypot(self.player[0]-side*2.4,self.player[1])>3.:
            self.message='Aproxime-se da porta para chamar';return False
        self.destination=level
        if self.station==level:
            self.mode='OPENING' if self.mode=='CLOSED' else 'OPEN';self.message='Aguarde a abertura'
        else:
            self.mode='CLOSING';self.message='Cabine a caminho'
        return True

    def cabin_floor(self):
        return {'id':'cabin_floor','center':[0,0,self.car_z], 'size':[self.config['cabin']['length'],self.config['cabin']['width']]}

    def boxes(self):
        boxes=list(self.config['obstacles']);length=self.config['cabin']['length'];width=self.config['cabin']['width']
        # Laterais da cabine e teto: mesma representação física/visual do proxy.
        for side in (-1,1):
            boxes.append({'id':f'cabin_wall_{side}','center':[0,side*(width/2+.06),self.car_z+1.35],'size':[length+.12,.12,2.7]})
        boxes.append({'id':'cabin_roof','center':[0,0,self.car_z+2.76],'size':[length+.24,width+.24,.12]})
        # Porta inteira permanece física até abertura completa; folhas visuais deslizam.
        for landing,z in self.config['levels'].items():
            side=1 if landing=='upper' else -1
            opened=self.station==landing and self.mode=='OPEN' and self.openness==1.
            if not opened:boxes.append({'id':f'landing_door_{landing}','center':[side*(length/2+.06),0,z+1.25],'size':[.12,1.6,2.5]})
        for side in (-1,1):
            opened=(self.mode=='OPEN' and self.openness==1. and self.station==('upper' if side==1 else 'lower'))
            if not opened:boxes.append({'id':f'cabin_door_{side}','center':[side*length/2,0,self.car_z+1.25],'size':[.10,1.6,2.5]})
        return boxes

    def support_at(self, p, maximum):
        found=[]
        for floor in self.config['floors']+[self.cabin_floor()]:
            h=floor_height(p,floor)
            if h is not None and p[2]-.35<=h<=maximum:found.append((h,floor['id']))
        return max(found,default=None)

    def blocked(self,p):
        return next((box['id'] for box in self.boxes() if box_contact(p,box,self.radius,self.height,self.skin)),None)

    def move(self, dx, dy, dt):
        """Subpassos <= 0,025: não saltar portas/parede fina. Apoio e step separados."""
        count=max(1,math.ceil(math.hypot(dx,dy)/.025))
        for _ in range(count):
            previous=self.player[:];p=[previous[0]+dx/count,previous[1]+dy/count,previous[2]]
            support=self.support_at(p,previous[2]+self.step)
            if support and -.03<=support[0]+self.skin-previous[2]<=self.step:
                p[2]=support[0]+self.skin
            blocker=self.blocked(p)
            if blocker:
                # Slide em cada eixo precisa permanecer livre; nunca apagar obstáculo.
                options=[[p[0],previous[1],previous[2]],[previous[0],p[1],previous[2]]]
                for candidate in options:
                    ground=self.support_at(candidate,previous[2]+self.step)
                    if ground and -.03<=ground[0]+self.skin-previous[2]<=self.step:
                        candidate[2]=ground[0]+self.skin
                    if not self.blocked(candidate):p=candidate;blocker=None;break
            if blocker:self.message=f'Bloqueado: {blocker}';continue
            # Proteção de borda explícita: guarda-corpos visuais delimitam a área.
            if not self.support_at(p,p[2]+self.skin) and self.mode!='TRAVELLING':
                self.message='Borda do recorte jogável';continue
            self.player=p
        self.velocity_z-=9.81*dt
        support=self.support_at(self.player,self.player[2]+self.skin)
        if support and self.player[2]+self.velocity_z*dt<=support[0]+self.skin:
            self.player[2]=support[0]+self.skin;self.velocity_z=0.;self.support=support[1]
        else:
            proposed=self.player[:];proposed[2]+=self.velocity_z*dt
            if not self.blocked(proposed):self.player=proposed
        return self.player

    def update(self,dt):
        self.elapsed+=dt
        if self.mode=='OPENING':
            if self.station is None or abs(self.car_z-self.config['levels'][self.station])>1e-6:
                self.mode='CLOSED';self.openness=0.;return
            self.openness=min(1.,self.openness+dt)
            if self.openness==1.:self.mode='OPEN';self.message='Entre e pressione E; ou saia'
        elif self.mode=='CLOSING':
            if self.portal_occupied():
                self.mode='OPEN';self.openness=1.;self.message='Abertura ocupada: fechamento impedido';return
            self.openness=max(0.,self.openness-dt)
            if self.openness==0.:
                self.carrying=self.in_cabin()
                self.station=None;self.mode='TRAVELLING'
                self.events.append({'event':'departure','time':self.elapsed,'door_aperture':0.,'carrying':self.carrying})
        elif self.mode=='TRAVELLING':
            assert self.openness==0.,'Interlock: porta aberta'
            target=self.config['levels'][self.destination];distance=target-self.car_z
            speed=min(4.,math.sqrt(4.*abs(distance)));sign=1 if distance>0 else -1
            desired=sign*speed
            self.car_velocity+=max(-2.*dt,min(2.*dt,desired-self.car_velocity))
            dz=self.car_velocity*dt
            if abs(dz)>=abs(distance) or abs(distance)<.0001:dz=distance;self.car_velocity=0.
            self.car_z+=dz
            if self.carrying:self.player[2]+=dz
            if self.car_z==target:
                self.station=self.destination;self.mode='OPENING';self.events.append({'event':'arrival','landing':self.station,'time':self.elapsed})
        self.move(0.,0.,dt)


def route_walk(controller, points, trace, speed=2.5):
    """Dirige o MESMO controller por inputs; não escreve posições de destino."""
    for point in points:
        for _ in range(20000):
            dx,dy=point[0]-controller.player[0],point[1]-controller.player[1]
            distance=math.hypot(dx,dy)
            if distance<.04:break
            scale=min(distance,speed/60)/distance
            previous=controller.player[:]
            controller.update(1/60);controller.move(dx*scale,dy*scale,0.)
            blocker=controller.blocked(controller.player)
            if blocker:raise RuntimeError('Penetração: '+blocker)
            trace.append({'position':controller.player[:],'car_z':controller.car_z,'mode':controller.mode,'support':controller.support})
            if controller.player==previous:raise RuntimeError('Rota bloqueada: '+controller.message)
        else:raise RuntimeError('Destino não alcançado')


def validate_round_trip(config):
    controller=ProxyController(config);trace=[]
    route_walk(controller,config['upper_route'],trace)
    assert controller.request()
    for _ in range(61):controller.update(1/60)
    assert controller.mode=='OPEN'
    route_walk(controller,[[0,0]],trace)
    assert controller.request()
    for _ in range(2000):
        controller.update(1/60)
        trace.append({'position':controller.player[:],'car_z':controller.car_z,'mode':controller.mode,'support':controller.support})
        if controller.mode=='OPEN' and controller.station=='lower':break
    assert controller.station=='lower' and controller.mode=='OPEN'
    route_walk(controller,config['lower_route'],trace)
    assert math.dist(controller.player[:2],config['lower_route'][-1][:2])<.05
    route_walk(controller,list(reversed(config['lower_route']))+[[0,0]],trace)
    assert controller.request()
    for _ in range(2000):
        controller.update(1/60)
        trace.append({'position':controller.player[:],'car_z':controller.car_z,'mode':controller.mode,'support':controller.support})
        if controller.mode=='OPEN' and controller.station=='upper':break
    assert controller.station=='upper' and controller.mode=='OPEN'
    route_walk(controller,list(reversed(config['upper_route'])),trace)
    assert math.dist(controller.player[:2],config['spawn'][:2])<.05
    return {'status':'GAMEPLAY_PROXY_ROUND_TRIP_PASSED','historical_fidelity_resolved':False,
            'trace':trace,'events':controller.events,'final_position':controller.player,'falls':controller.falls}
