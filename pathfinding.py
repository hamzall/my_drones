from typing import List, Dict, Tuple, Optional, Set
import heapq
from classes_types import Graph, ZoneType



"from a current zone to the goal"
class TheRoad:
    
    def __init__(self, zones: List[str], total_cost: int, priority_steps: int) -> None:
        self.zones = zones
        self.total_cost = total_cost
        self.priority_steps = priority_steps
        
    def next_zone_name(self) -> str | None:
        if len(self.zones) < 2:
            return None
        return self.zones[1]


class PathFinder:

    def __init__(self, graph: Graph) -> None:    
        self.graph = graph
        self.the_cache: Dict[Tuple[str, Tuple[str, ...]], Optional[TheRoad]] = {}
    
    
    """Return the preferred shortest route from a zone to the end."""
    def shortest_road(self, current_zone: str, forbidden: Set[str] | None = None) -> Optional[TheRoad]:
        forbidden_set = forbidden or set()
        cache_key = (current_zone, tuple(sorted(forbidden_set)))

        if cache_key in self.the_cache:
            return self.the_cache[cache_key]
        
        end_name = self.graph.get_end_zone().name
        heap: List[Tuple[int, int, int , str, List[str]]] = []
        heapq.heappush(heap, (0,0,0, current_zone, [current_zone]))
        best: Dict[str, Tuple[int, int, int]] = {current_zone: (0, 0, 0)}
        
        while heap:
            cost, neg_priority, hops, zone_name, path = heapq.heappop(heap)
            
            if (zone_name == end_name):
                road_obj = TheRoad(zones=path, total_cost=cost, priority_steps=-neg_priority)
                self.the_cache[cache_key] = road_obj
                return road_obj
            
            if best.get(zone_name) != (cost, neg_priority, hops):
                continue
            
            for neighbor_name, _connection in self.graph.get_neighbors(zone_name):
                if (neighbor_name in forbidden_set and neighbor_name != end_name):
                    continue
                
                neighbor_zone = self.graph.zones[neighbor_name]
                if (neighbor_zone.type_of_zone is ZoneType.BLOCKED):
                    continue
                
                step_cost = neighbor_zone.type_of_zone.cost_of_movement()
                priority_bonus = (1 if neighbor_zone.type_of_zone is ZoneType.PRIORITY else 0)
                
                candidate = (cost + step_cost, neg_priority - priority_bonus, hops + 1)
                
                if neighbor_name not in best or candidate < best[neighbor_name]:
                    best[neighbor_name] = candidate
                    heapq.heappush(heap, (candidate[0], candidate[1], candidate[2], neighbor_name, path + [neighbor_name]))
        
        self.the_cache[cache_key] = None
        return None
