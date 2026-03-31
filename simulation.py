from typing import Tuple, Dict, Set
from classes_types import Graph, Drone, RestrictedMonitor
from pathfinding import PathFinder


#     def _all_delivered(self) -> bool:
#         """Return ``True`` when all drones reached the end."""
#         return all(drone.delivered for drone in self.drones.values())


# def _advance_transit(self, movements: List[str]) -> Set[int]:
#         """Advance drones already moving through restricted connections."""
#         ready_after_arrival: Set[int] = set()
#         completed: List[int] = []

#         for drone_id in sorted(self.transit_by_drone):
#             transit = self.transit_by_drone[drone_id]
#             arrived_now = transit.tick()

#             if arrived_now:
#                 drone = self.drones[drone_id]
#                 drone.current_zone = transit.destination
#                 self.zone_occupants[transit.destination].add(drone_id)

#                 if transit.destination == self.graph.end.name:
#                     drone.delivered = True
#                     self.delivery_turns[drone_id] = self.turn

#                 movements.append(f"{drone.label}-{transit.destination}")
#                 ready_after_arrival.add(drone_id)
#                 completed.append(drone_id)
#             else:
#                 movements.append(f"D{drone_id}-{transit.connection_name}")

#         for drone_id in completed:
#             del self.transit_by_drone[drone_id]

#         return ready_after_arrival


# #optional
#     def _ready_drones_sorted(self, arrivals_this_turn: Set[int]) -> List[int]:
#         """Return drones that may act this turn, sorted by useful priority."""
#         ready: List[Tuple[int, int, int]] = []

#         for drone_id, drone in self.drones.items():
#             if drone.delivered or drone_id in self.transit_by_drone:
#                 continue
#             if drone_id in arrivals_this_turn:
#                 continue

#             route = self.pathfinder.shortest_route(drone.current_zone)
#             remaining_cost = route.total_cost if route is not None else 10**9
#             start_penalty = 1 if drone.current_zone == self.graph.start.name else 0
#             ready.append((remaining_cost, start_penalty, drone_id))

#         ready.sort()
#         return [drone_id for _cost, _start_penalty, drone_id in ready]






class Metrics:
    
    def __init__(self, turns: int, average_turns_drone_to_goal: float, total_path_cost: float) -> None:
        self.turns = turns
        self.average_turns_drone_to_goal = average_turns_drone_to_goal
        self.total_path_cost = total_path_cost



# without executed it, what i will do in this move
# move = action from zone to zone
class MovePlaning:
    
    def __init__(
        self, drone_id: int, fromm: str, to: str, connet_key: Tuple[str, str], connet_name: str, move_cost: int
    ) -> None:    
        self.drone_id = drone_id
        self.fromm = fromm
        self.to = to
        self.connet_key = connet_key        
        self.connet_name = connet_name
        self.move_cost = move_cost
    



class Simulation:
    
    def __init__(self, graph: Graph, drones_num: int) -> None:
        self.graph = graph
        self.drones_num = drones_num
        self.pathfinded = PathFinder(graph)
        self.drones: Dict[int, Drone] = self.create_drones()
        #set for the duplicate -> zone name + drones id in it
        self.who_in_zones: Dict[str, Set[int]] = self.fill_who_in_zones()
        self.transit_by_drone: Dict[int, RestrictedMonitor] = {}
        self.turn = 0
        #are optional
        self.total_path_cost = 0
        self.delivery_turns: Dict[int, int] = {}
    
    
    
    def create_drones(self) -> Dict[int, Drone]:
        result: Dict[int, Drone] = {}
        for i in range(self.drones_num):
            result.update({i + 1: Drone(i + 1, self.graph.get_start_zone().name)})
        return result
        
    
    def fill_who_in_zones(self) -> Dict[str, Set[int]]:
        result: Dict[str, Set[int]] = {}
        for zone_name in self.graph.zones.keys():
            result.update({zone_name: set()})
        result[self.graph.get_start_zone().name] = {value for value in self.drones.keys()}
        return result

    
    
            