"""Contrato executável neutro de engine. Estados desconhecidos bloqueiam acesso.

Não executa física: o adaptador deve fornecer medidas e clearance de sweeps reais.
Não confundir porta visual animada com passagem física liberada.
"""
from dataclasses import dataclass
import heapq

@dataclass(frozen=True)
class LandingState:
    cabin_present: bool | None = None
    cabin_stationary: bool | None = None
    landing_aperture: float | None = None
    cabin_aperture: float | None = None
    sill_delta: float | None = None
    capsule_clear: bool | None = None
    landing_supported: bool | None = None

def boarding_allowed(state, character):
    width=2*character['radius']+2*character['contact_tolerance']
    return (state.cabin_present is True and state.cabin_stationary is True
            and state.capsule_clear is True and state.landing_supported is True
            and state.landing_aperture is not None and state.landing_aperture>=width
            and state.cabin_aperture is not None and state.cabin_aperture>=width
            and state.sill_delta is not None
            and abs(state.sill_delta)<=character['boarding_capsule_contact_max_drop'])

def departure_allowed(*, doors_closed, portal_empty, cabin_sweep_clear, occupancy_supported):
    return all(x is True for x in (doors_closed,portal_empty,cabin_sweep_clear,occupancy_supported))

def closing_allowed(*, portal_capsule_empty):
    return portal_capsule_empty is True

def crossing_allowed(*, source_crossing_confirmed, traffic_permission, capsule_clear):
    return all(x is True for x in (source_crossing_confirmed,traffic_permission,capsule_clear))

def permitted_edges(edges, permissions):
    """Mesma máscara para planner, follower e física; não usar A* estático no poço."""
    for edge in edges:
        if all(permissions.get(gate) is True for gate in edge.get('gates',[])):
            yield edge

def find_path(edges,start,goal,permissions):
    adjacency={}
    for e in permitted_edges(edges,permissions):
        adjacency.setdefault(e['from'],[]).append(e)
    heap=[(0,start,[start])];costs={start:0}
    while heap:
        cost,node,path=heapq.heappop(heap)
        if cost!=costs[node]:continue
        if node==goal:return path
        for e in adjacency.get(node,[]):
            n=e['to'];new=cost+e.get('cost',1)
            if new<costs.get(n,float('inf')):
                costs[n]=new;heapq.heappush(heap,(new,n,path+[n]))
    return None

def validate_ride_contract(edges):
    required={'service_contract_approved','cabin_sweep'}
    for e in edges:
        if e.get('mode')=='elevator_service':
            assert required<=set(e['gates']), 'Serviço não pode virar aresta pedonal pelo poço'
        else:
            assert not (e['from']=='cabin_upper' and e['to']=='cabin_lower')

class ElevatorService:
    """Execução temporal. Não exige cabine simultaneamente nos dois pisos.

    A aresta de serviço nunca é seguida como segmento pedonal pelo poço.
    O adaptador físico permanece responsável por suporte/carry e sensores.
    """
    def __init__(self,character):
        self.character=character;self.phase='waiting_upper'
    def board(self,state):
        if self.phase=='waiting_upper' and boarding_allowed(state,self.character):
            self.phase='boarded';return True
        return False
    def depart(self,*,doors_closed,portal_empty,cabin_sweep_clear,occupancy_supported):
        if self.phase=='boarded' and departure_allowed(doors_closed=doors_closed,portal_empty=portal_empty,
                cabin_sweep_clear=cabin_sweep_clear,occupancy_supported=occupancy_supported):
            self.phase='moving';return True
        return False
    def arrive(self,state):
        if self.phase=='moving' and state.cabin_present is True and state.cabin_stationary is True:
            self.phase='arrived_lower';return True
        return False
    def alight(self,state):
        if self.phase=='arrived_lower' and boarding_allowed(state,self.character):
            self.phase='complete';return True
        return False
