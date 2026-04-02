from typing import Tuple, Dict, Set, List, Optional
from classes_types import Graph, Drone, RestrictedMonitor
from pathfinding import PathFinder
from classes_types import Zone, Connection, ZoneType
from except_error import SimError


#optional
class Metrics:
    def __init__(self, turns: int, average_turns_drone_to_goal: float, moved_per_turn_average: float, total_path_cost: float) -> None:
        self.turns = turns
        self.moved_per_turn_average = moved_per_turn_average
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
            if drone_obj.arrivaled or drone_id in self.transit_by_drone:
                continue
            if drone_id in arrivals_this_turn:
                continue
            
            route = self.pathfinded.shortest_road(drone_obj.current_zone_name)
            remaining_cost = route.total_cost if route is not None else 10**9
            start_penalty = 1 if drone_obj.current_zone_name == self.graph.get_start_zone().name else 0
            ready.append((remaining_cost, start_penalty, drone_id))
            
        ready.sort()
        return [drone_id for _cost, _start_penalty, drone_id in ready]



    def has_capacity_after_this_turn(
        self, zone_name: str, occupancy: Dict[str, int], planned_departures: Dict[str, int],
        planned_arrivals_now: Dict[str, int], extra_arrival: int) -> bool:
        """Check zone capacity at the end of the current turn."""
        zone_obj = self.graph.zones[zone_name]
        if zone_obj.get_zone_capacity() is None:
            return True
        
        projected = (occupancy[zone_name] - planned_departures[zone_name] + planned_arrivals_now[zone_name] + extra_arrival)
        
        return projected <= zone_obj.get_zone_capacity()
    
    
    
    def has_capacity_next_turn_for_restricted(
        self, zone_name: str, occupancy: Dict[str, int], planned_departures: Dict[str, int],
        planned_arrivals_now: Dict[str, int], reserved_arrivals_next_turn: Dict[str, int]) -> bool:
        
        zone_obj = self.graph.zones[zone_name]
        if (zone_obj.get_zone_capacity() is None):
            return True
        
        projected_end_of_current_turn = (occupancy[zone_name] - planned_departures[zone_name] + planned_arrivals_now[zone_name])
        projected_on_arrival = (projected_end_of_current_turn + reserved_arrivals_next_turn.get(zone_name, 0) + 1)
        
        return projected_on_arrival <= zone_obj.get_zone_capacity()


    def can_schedule(
        self, destination_zone: Zone, connection: Connection, occupancy: Dict[str, int], planned_departures: Dict[str, int],
        planned_arrivals_now: Dict[str, int], reserved_arrivals_next_turn: Dict[str, int], 
        link_usage_now: Dict[Tuple[str, str], int], link_usage_next_turn: Dict[Tuple[str, str], int]) -> bool:
        
        if destination_zone.type_of_zone is ZoneType.BLOCKED:
            return False
        
        if link_usage_now.get(connection.key_as_set(), 0) >= connection.max_link_capa:
            return False
        
        if destination_zone.type_of_zone.cost_of_movement() == 1:
            return self.has_capacity_after_this_turn(
                zone_name=destination_zone.name, occupancy=occupancy, planned_departures=planned_departures,
                planned_arrivals_now=planned_arrivals_now, extra_arrival = 1)
        
        if link_usage_next_turn.get(connection.key_as_set(), 0) >= connection.max_link_capa:
            return False
        
        return self.has_capacity_next_turn_for_restricted(
            zone_name=destination_zone.name, occupancy=occupancy, planned_departures=planned_departures,
            planned_arrivals_now=planned_arrivals_now, reserved_arrivals_next_turn=reserved_arrivals_next_turn)
    


    def choose_move(
        self, drone: Drone, occupancy: Dict[str, int], planned_departures: Dict[str, int],
        planned_arrivals_now: Dict[str, int], reserved_arrivals_next_turn: Dict[str, int],
        link_usage_now: Dict[Tuple[str, str], int], link_usage_next_turn: Dict[Tuple[str, str], int]
    ) -> Optional[MovePlaning]:
        
        current_zone_name = drone.current_zone_name
        
        #optional
        forbidden: Set[str] = set()
        
        for _ in range(len(self.graph.zones) + 1):
            route = self.pathfinded.shortest_road(current_zone_name, forbidden=forbidden)
            
            if route is None or route.next_zone_name() is None:
                return None
            
            next_zone_filled: str = route.next_zone_name()
            destination_zone = self.graph.zones[next_zone_filled]
            connection = self.graph.get_a_connection(current_zone_name, next_zone_filled)
            
            if self.can_schedule(
                destination_zone=destination_zone, connection=connection, occupancy=occupancy, planned_departures=planned_departures,
                planned_arrivals_now=planned_arrivals_now, reserved_arrivals_next_turn=reserved_arrivals_next_turn,
                link_usage_now=link_usage_now, link_usage_next_turn=link_usage_next_turn):
                return MovePlaning(
                    drone_id=drone.drone_id, fromm=current_zone_name,
                    to=destination_zone.name, connet_key=connection.key_as_set(),
                    connet_name=connection.get_names_marged(), move_cost=destination_zone.type_of_zone.cost_of_movement())
        
            forbidden.add(next_zone_filled)
        return  None



    def plan_moves(self, arrivals_this_turn: Set[int]) -> List[MovePlaning]:
        occupancy = {zone_name: len(occupants) for zone_name, occupants in self.who_in_zones.items()}
        planned_departures: Dict[str, int] = {zone_name: 0 for zone_name in self.graph.zones}
        planned_arrivals_now: Dict[str, int] = {zone_name: 0 for zone_name in self.graph.zones}
        reserved_arrivals_next_turn: Dict[str, int] = {}
        link_usage_now: Dict[Tuple[str, str], int] = {}
        link_usage_next_turn: Dict[Tuple[str, str], int] = {}
        planned_moves: List[MovePlaning] = []
        
        for drone_id in self.ready_drones_sorted(arrivals_this_turn):
            drone = self.drones[drone_id]
            move: MovePlaning = self.choose_move(
                drone=drone, occupancy=occupancy, planned_departures=planned_departures, planned_arrivals_now=planned_arrivals_now,
                reserved_arrivals_next_turn=reserved_arrivals_next_turn, link_usage_now=link_usage_now,
                link_usage_next_turn=link_usage_next_turn
            )
            if move is None:
                continue
            
            planned_moves.append(move)
            planned_departures[move.fromm] += 1
            link_usage_now[move.connet_key] = (link_usage_now.get(move.connet_key, 0) + 1)
            if move.move_cost == 1:
                planned_arrivals_now[move.to] += 1
            else:
                link_usage_next_turn[move.connet_key] = (link_usage_next_turn.get(move.connet_key, 0) + 1)
                reserved_arrivals_next_turn[move.to] = (reserved_arrivals_next_turn.get(move.to, 0) + 1)

        return planned_moves



    def commit_moves(self, planned_moves: List[MovePlaning], movements: List[str]) -> None:
        
        for move in planned_moves:
            drone_obj = self.drones[move.drone_id]
            self.who_in_zones[move.fromm].remove(move.drone_id)
            
            if move.move_cost == 1:
                drone_obj.current_zone_name = move.to
                self.who_in_zones[move.to].add(move.drone_id)
                self.total_path_cost += 1
                
                if (move.to == self.graph.get_end_zone().name):
                    drone_obj.arrivaled = True
                    self.delivery_turns[move.drone_id] = self.turn

                movements.append("%s-%s" % (drone_obj.get_drone_id(), move.to))
                continue
            
            self.transit_by_drone[move.drone_id] = RestrictedMonitor(
                drone_id=move.drone_id,source=move.fromm,destination=move.to,
                connection_name=move.connet_name,turns_until_arrival=1)
            self.total_path_cost += 2
            movements.append("%s-%s" % (drone_obj.get_drone_id(), move.connet_name))
    


    def build_metrics(self, output_lines: List[str]) -> Metrics:
        total_moves = sum(len(line.split()) for line in output_lines)
        moved_per_turn_average = total_moves / len(output_lines) if output_lines else 0.0
        average_turns_per_drone = (sum(self.delivery_turns.values()) / self.drones_num if self.drones_num > 0 else 0.0)
        return Metrics(
            turns=self.turn,
            moved_per_turn_average=moved_per_turn_average,
            average_turns_drone_to_goal=average_turns_per_drone,
            total_path_cost=self.total_path_cost
            )


    def run(self) -> Tuple[List[str], Metrics]:
        if (self.pathfinded.shortest_road(self.graph.start_name) is None):
            raise SimError("Error, these is (NO) valid road from start to end")
        
        output_lines: List[str] = []
        
        #optional
        safety_limit = max(1000, self.drones_num * max(4, len(self.graph.zones)) * 20)
        
        while not self.is_all_drone_delevered():
            self.turn += 1
            if self.turn > safety_limit:
                raise SimError("Error, Simulation safety limit reached; possible deadlock")
            
            movements: List[str] = []
            arrivals_this_turn = self.apply_restricted_transit(movements)
            planned_moves = self.plan_moves(arrivals_this_turn)
            self.commit_moves(planned_moves, movements)

            # if not movements:
            #     raise SimulationError(
            #         f"No drone movement was possible at turn {self.turn}"
            #     )
            if not movements:
                output_lines.append("")
                continue
            
            output_lines.append(" ".join(movements))
        return output_lines, self.build_metrics(output_lines)


