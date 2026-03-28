from enum import Enum
from typing import Tuple, Dict, Optional, Iterable




class ZoneType(str, Enum):
    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"

    def cost_of_movement(self) -> int:
        if (self is ZoneType.NORMAL):
            return 1
        elif (self is ZoneType.PRIORITY):
            return 1
        elif (self is ZoneType.RESTRICTED):
            return 2
        elif (self is ZoneType.BLOCKED):
            raise ValueError("invalid movement cost, Blocked Zone")
        else:
            return 0


class Zone:

    def __init__(
        #"None" as string or real None
        self, name: str, x: int, y: int, type_of_zone: ZoneType = ZoneType.NORMAL,
        color: str = "none", drones_capa: int = 1,
        is_start: bool = False, is_end: bool = False 
        ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.type_of_zone = type_of_zone
        self.color = color
        self.drones_capa = drones_capa
        self.is_start = is_start
        self.is_end = is_end

    
    def get_zone_capacity(self) -> int | None:
        "None means unlimited drones"
        if (self.is_start or self.is_end):
            return None
        return self.drones_capa



class Connection:

    def __init__(self, zone1: str, zone2: str, max_link_capa: int = 1) -> None:
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capa = max_link_capa


    # give key tuple of the linked zones :
    def key_as_set(self) -> Tuple[str, str]:
        return tuple(sorted((self.zone1, self.zone2)))


    # name of two zones linked :
    def get_names_marged(self) -> str:
        f, s = self.key_as_set()
        return ("%s-%s" % (f, s))
    

    # connect with what ?
    def get_opposite_zone(self, name_of_zone: str) -> str:
        if self.zone1 == name_of_zone:
            return self.zone2
        elif self.zone2 == name_of_zone:
            return self.zone1    
        else:
            raise ValueError("Error, Wrong Part Zone Name")



class Graph:

    def __init__(
            self, zones: Dict[str, Zone], connections: Dict[Tuple[str, str], Connection],
            neighbors: Dict[str, Dict[str, Connection]], start_name: Optional[str] = None,
            end_name: Optional[str] = None
        ) -> None:
        self.zones = zones
        self.connections = connections
        self.neighbors = neighbors
        self.start_name = start_name
        self.end_name = end_name


    def add_zone(self, zone: Zone) -> None:
        if (" " in zone.name or "-" in zone.name):
            raise ValueError("Error: Invalid zone name")

        if zone.x < 0 or zone.y < 0:
            raise ValueError("Zone coordinates must be positive integers")
    
        #self.zones.keys()
        if (zone.name in self.zones):
            raise ValueError("Error: Invalid zone name, Already Exists")
        
        if (zone.is_start and self.start_name is not None):
            raise ValueError("Error, Already Exists, Multiple start zones are not allowed")
        
        if zone.is_end and self.end_name is not None:
            raise ValueError("Multiple end_hub zones are not allowed")
        
        self.zones[zone.name] = zone
        self.neighbors[zone.name] = {}

        if zone.is_start:
            self.start_name = zone.name
        
        if zone.is_end:
            self.end_name = zone.name


    def add_connection(self, connection: Connection) -> None:
        if connection.zone1 == connection.zone2:
            raise ValueError("Error, I can not add a connection with the same zone")
        
        #self.zones.key()
        if (connection.zone1 not in self.zones or connection.zone2 not in self.zones):
            raise ValueError("Error, Some zone part not exists in (gragh zones)")
        
        key = connection.key_as_set()
        if (key in self.connections):
            raise ValueError("Error, Duplicate connection")
        
        self.connections[key] = connection
        self.neighbors[connection.zone1][connection.zone2] = connection
        self.neighbors[connection.zone2][connection.zone1] = connection


    def get_start_zone(self) -> Zone:
        if (self.start_name is None):
            raise ValueError("Start zone not defined")
        return self.zones[self.start_name]
    

    def get_end_zone(self) -> Zone:
        if (self.end_name is None):
            raise ValueError("End zone not defined")
        return self.zones[self.end_name]


    def get_a_connecton(self, z1: str, z2: str) -> Connection:
        key = tuple(sorted((z1, z2)))
        return self.connections[key]


    def get_neighbors(self, name_of_zone: str) -> Iterable[Tuple[str, Connection]]:
        return self.neighbors[name_of_zone].items()



class Drone:

    def __init__(self, drone_id: int, current_zone_name: str, arrivaled: bool = False) -> None:
        self.drone_id = drone_id
        self.current_zone_name = current_zone_name
        self.arrivaled = arrivaled

    def get_drone_id(self) -> str:
        return ("D%d" % self.drone_id)


# without this class will algo make the restricted zones like the normal zones
class RestrictedMonitor:
    
    def __init__(
            self, drone_id: int, frrom: str, to: str,
            name_of_connec: str, turns_until_arrival: int
        ) -> None:
        self.drone_id = drone_id
        self.source = frrom
        self.destination = to
        self.connection_name = name_of_connec
        #this always will be 1
        self.turns_until_arrival = turns_until_arrival


    def decrease_and_isarrival(self) -> bool:
        self.turns_until_arrival -= 1
        return self.turns_until_arrival == 0

