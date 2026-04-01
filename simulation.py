from typing import Tuple, Dict, Set, List
from classes_types import Graph, Drone, RestrictedMonitor
from pathfinding import PathFinder




#optional
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
        
        #included only drones these are in a restricted road (id, obj)
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


    def is_all_drone_delevered(self) -> bool:
        for drone in self.drones.values():
            if not drone.arrivaled:
                return False
        return True



# 1. كتشيك الدرونات اللي فـ الطريق
# 2. كتقرر:
# 3. كتكتب فـ movements
# """
# _advance_transit كتقول:
# "شكون اللي كان فـ الطاكسي؟ واش وصل دابا؟"
# """

# كتبدل حالة drones اللي فـ self.transit_by_drone
# كتزيد معلومات فـ movements
# كترجع Set[int] فيه IDs ديال drones اللي وصلو فهاد t

# هاد الدالة كتخدم غير على drones اللي راهوم already فـ الطريق.

# يعني:

# ماشي هي اللي كتبدا الحركة
# هي اللي كتكمّل الحركة

    def apply_restricted_transit(self, movements: List[str]) -> Set[int]:
        """the drone the get out from a zone to a rest zone"""
        # works only with transit drone moves
        
        # for dont move again if a drone already arrivaled
        #ignore double move
        ready_after_arrival: Set[int] = set()
        
        # drones who completed their transit
        # for remove them from self.transit_by_drone
        # if they arriveled
        completed: List[int] = []
        
        
        #                for good formate output always
        for drone_id in sorted(self.transit_by_drone):
            transit_obj = self.transit_by_drone[drone_id]
            in_dest_zone = transit_obj.decrease_and_isarrival()
            
            if in_dest_zone:
                drone_obj = self.drones[drone_id]
                drone_obj.current_zone_name = transit_obj.destination
                self.who_in_zones[transit_obj.destination].add(drone_id)
                
                if transit_obj.destination == self.graph.get_end_zone().name:
                    drone_obj.arrivaled = True
                    self.delivery_turns[drone_id] = self.turn
                
                movements.append("%s-%s" % (drone_obj.get_drone_id(), transit_obj.destination))
                ready_after_arrival.add(drone_id)
                completed.append(drone_id)
            else:
                movements.append("D%d-%s" % (drone_id, transit_obj.connection_name))

        for dro_id in completed:
            del self.transit_by_drone[dro_id]
        
        return ready_after_arrival


#   optional
    def ready_drones_sorted(self, arrivals_this_turn: Set[int]) -> List[int]:
        ready: List[Tuple[int, int, int]] = []
        
        for drone_id, drone_obj in self.drones.items():
            if drone_obj.delivered or drone_id in self.transit_by_drone:
                continue
            if drone_id in arrivals_this_turn:
                continue
            
            route = self.pathfinded.shortest_road(drone_obj.current_zone_name)
            remaining_cost = route.total_cost if route is not None else 10**9
            start_penalty = 1 if drone_obj.current_zone_name == self.graph.get_start_zone().name else 0
            ready.append((remaining_cost, start_penalty, drone_id))
            
        ready.sort()
        return [drone_id for _cost, _start_penalty, drone_id in ready]


# def _has_capacity_after_this_turn(
#         self,
#         zone_name: str,
#         occupancy: Dict[str, int],
#         planned_departures: Dict[str, int],
#         planned_arrivals_now: Dict[str, int],
#         extra_arrival: int,
#     ) -> bool:
#         """Check zone capacity at the end of the current turn."""
#         zone = self.graph.zones[zone_name]
#         if zone.capacity is None:
#             return True

#         projected = (
#             occupancy[zone_name]
#             - planned_departures[zone_name]
#             + planned_arrivals_now[zone_name]
#             + extra_arrival
#         )
#         return projected <= zone.capacity


#     def _has_capacity_next_turn_for_restricted(
#         self,
#         zone_name: str,
#         occupancy: Dict[str, int],
#         planned_departures: Dict[str, int],
#         planned_arrivals_now: Dict[str, int],
#         reserved_arrivals_next_turn: Dict[str, int],
#     ) -> bool:
#         """Check future arrival capacity for a restricted move."""
#         zone = self.graph.zones[zone_name]
#         if zone.capacity is None:
#             return True

#         projected_end_of_current_turn = (
#             occupancy[zone_name]
#             - planned_departures[zone_name]
#             + planned_arrivals_now[zone_name]
#         )
#         projected_on_arrival = (
#             projected_end_of_current_turn
#             + reserved_arrivals_next_turn.get(zone_name, 0)
#             + 1
#         )
#         return projected_on_arrival <= zone.capacity
