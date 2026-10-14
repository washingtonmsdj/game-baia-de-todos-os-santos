"""Quatro equipamentos provisórios com estados independentes; sem teleporte."""
from dataclasses import dataclass
import math

@dataclass
class Lift:
 id:str
 lower:float
 upper:float
 z:float
 clearance_approved:bool=False
 station:str='upper'
 destination:str|None=None
 state:str='CLOSED'
 openness:float=0.
 velocity:float=0.
 passenger_z:float|None=None
 portal_occupied:bool=False

 def request(self,destination):
  if destination not in ('upper','lower') or self.state in ('MOVING','CLOSING','OPENING'):return False
  if self.station==destination:self.state='OPENING';return True
  if not self.clearance_approved:return False
  self.destination=destination;self.state='CLOSING';return True

 def depart(self):
  if self.state!='OPEN' or not self.clearance_approved:return False
  self.destination='lower' if self.station=='upper' else 'upper';self.state='CLOSING';return True

 def landing_open(self,station):
  return self.station==station and self.state=='OPEN' and self.openness==1.

 def update(self,dt):
  assert 0.<dt<=1/30
  dz=0.
  if self.state=='OPENING':
   if self.station is None or abs(self.z-getattr(self,self.station))>1e-5:self.state='CLOSED';self.openness=0.;return 0.
   self.openness=min(1.,self.openness+dt)
   if self.openness==1.:self.state='OPEN'
  elif self.state=='CLOSING':
   if self.portal_occupied:self.state='OPEN';self.openness=1.;return 0.
   self.openness=max(0.,self.openness-dt)
   if self.openness==0.:
    if not self.clearance_approved:self.state='BLOCKED_CCD';return 0.
    self.station=None;self.state='MOVING'
  elif self.state=='MOVING':
   assert self.openness==0. and self.station is None and self.clearance_approved
   target=getattr(self,self.destination);distance=target-self.z
   speed=min(3.,math.sqrt(3.*abs(distance)));desired=math.copysign(speed,distance)
   self.velocity+=max(-1.5*dt,min(1.5*dt,desired-self.velocity));dz=self.velocity*dt
   if abs(dz)>=abs(distance) or abs(distance)<1e-4:dz=distance;self.velocity=0.
   self.z+=dz
   if self.passenger_z is not None:self.passenger_z+=dz
   if self.z==target:self.station=self.destination;self.state='OPENING'
  return dz

def verify_lift(spec):
 l=Lift(spec['id'],spec['lower'],spec['upper'],spec['upper'],True)
 assert not l.landing_open('lower')
 assert l.request('upper')
 for _ in range(61):l.update(1/60)
 assert l.state=='OPEN'
 l.portal_occupied=True;assert l.depart();l.update(1/60);assert l.state=='OPEN'
 l.portal_occupied=False;l.passenger_z=l.z+.015;assert l.depart()
 samples=[]
 for destination in ('lower','upper'):
  if destination=='upper':assert l.depart()
  for _ in range(4000):
   previous=l.z;dz=l.update(1/60)
   assert abs(l.z-previous)<=.051
   assert abs(l.passenger_z-l.z-.015)<1e-7
   if l.state=='MOVING':assert l.openness==0. and not l.landing_open('upper') and not l.landing_open('lower')
   samples.append({'z':l.z,'passenger_z':l.passenger_z,'state':l.state,'openness':l.openness})
   if l.station==destination and l.state=='OPEN':break
  else:raise AssertionError('Equipamento não chegou')
 blocked=Lift(spec['id'],spec['lower'],spec['upper'],spec['upper'],False)
 assert not blocked.request('lower')
 return {'id':spec['id'],'status':'STATE_MACHINE_AND_RIDER_TRANSPORT_PASSED','samples':len(samples),'max_step_m':.05,
         'interlocks':['closed_doors_during_motion','landing_requires_car','portal_sensor_blocks_close','unknown_ccd_blocks_departure'],
         'not_a_full_pedestrian_route_test':True}
