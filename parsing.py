from classes_types import Graph
from re import compile
from except_error import ParsingError
from typing import Dict
from classes_types import Connection, Zone, ZoneType


# Capturing Groups
# ^ should start with this
# $ for take all text for match it starting with ^
# r for dont read data with \
# like \n we dont want from it a new line exp
ZONE_SHOULD_BE = compile(
    r"^(start_hub|end_hub|hub):\s+([^\s\-]+)\s+(\d+)\s+(\d+)(?:\s+\[(.*?)\])?$"
)
CONNECTION_SHOULD_BE = compile(
    r"^connection:\s+([^\s\-]+)-([^\s\-]+)(?:\s+\[(.*?)\])?$"
)
DRONES_NUM_SHOULD_BE = compile(r"^nb_drones:\s+(\d+)$")




class ParsedMapData:
    def __init__(self, drones_num: int, the_graph: Graph) -> None:
        self.drones_num = drones_num
        self.the_graph = the_graph



# nb_drones: 2

# start_hub: start 0 0 [color=green]
# hub: waypoint1 1 0 [color=blue]
# hub: waypoint2 2 0 [color=blue]
# end_hub: goal 3 0 [color=red]
# connection: start-waypoint1
# connection: waypoint1-waypoint2
# connection: waypoint2-goal




class ParsingClassData:
    
    def ignore_comments(self, first_line: str) -> str:
        res = first_line.find("#")
        if (res == -1):
            return first_line
        return first_line[:res]


    def get_drone_numbers(self, line: str) -> int:
        match_res = DRONES_NUM_SHOULD_BE.match(line)
        if (match_res is None):
            raise ParsingError("Error, Bad Pattern in the first")
        number_of_drones = int(match_res.group(1))
        if (number_of_drones <= 0):
            raise ParsingError("Error, Please Enter a Positive Drone Numbers")
        return number_of_drones


#      color=yellow  max_drones=2  juyj=56  
    def get_metadata_keyvalue(self, text: str | None, index_of_line: int) -> Dict[str, str]:
        if (text is None):
            return {}
        
        stripped_text = text.strip()
        if (stripped_text is None):
            return {}
        
        result: Dict[str, str] = {}
        
        for ke_va in stripped_text.split(" "):
            if "=" not in ke_va:
                raise ParsingError("Error, invalid metadata in the line %d" % index_of_line)
            
            key, value = ke_va.split("=", 1)
            if not key or not value:
                raise ParsingError("Error, invalid metadata in the line %d" % index_of_line)
            
            if key in result:
                raise ParsingError("Error, Duplicate Key in the line %d" % index_of_line)
            
            result[key] = value
        
        return result


    def get_parse_of_int(self, value: str, line_index: int, field_name: str) -> int:
        try:
            result = int(value)
        except Exception:
            raise ParsingError("Error, invalid syntax/non-positive in (line %d, feild %s)" % (line_index, field_name))
        if (result <= 0):
            raise ParsingError("Error, non-positive in (line: %d, feild: %s)" % (line_index, field_name))
        return result


    def parse_connection(self, line: str, line_index: int) -> Connection:

        match_res = CONNECTION_SHOULD_BE.match(line)
        if (match_res is None):
            raise ParsingError("Error, invalid connection syntax in line %d" % line_index)
        
        zone1, zone2, metadata = match_res.groups()
        if (metadata is not None):
            metadata_dict = self.get_metadata_keyvalue(metadata, line_index)

        capacity_of_max_link = self.get_parse_of_int(
            metadata_dict.get("max_link_capacity", "1") , line_index , "max_link_capacity"
        )
        
        is_there_other_key = set(metadata_dict).difference({"max_link_capacity"})
        if (is_there_other_key == True):
            raise ParsingError("Error, Should be only one key in line %d" % line_index)
        
        return Connection(zone1=zone1, zone2=zone2, max_link_capa=capacity_of_max_link)
    
    
    
    
    


# def _parse_zone(self, line: str, line_index: int) -> Zone:
#         """Parse one zone definition line."""
#         match = _ZONE_RE.match(line)
#         if match is None:
#             raise ParseError(f"Line {line_index}: invalid zone syntax")

#         zone_kind, name, x_str, y_str, metadata_text = match.groups()
#         x = int(x_str)
#         y = int(y_str)
#         metadata = self._parse_metadata(metadata_text, line_index)

#         zone_type_text = metadata.get("zone", ZoneType.NORMAL.value)
#         try:
#             zone_type = ZoneType(zone_type_text)
#         except ValueError as exc:
#             raise ParseError(
#                 f"Line {line_index}: invalid zone type {zone_type_text!r}"
#             ) from exc

#         color = metadata.get("color", "none")
#         max_drones = self._parse_positive_int(
#             metadata.get("max_drones", "1"),
#             line_index,
#             "max_drones",
#         )

#         unsupported = set(metadata).difference({"zone", "color", "max_drones"})
#         if unsupported:
#             field_name = sorted(unsupported)[0]
#             raise ParseError(
#                 f"Line {line_index}: unsupported zone metadata {field_name!r}"
#             )
#         return Zone(name=name, x=x, y=y, zone_type=zone_type, color=color, max_drones=max_drones, is_start=zone_kind == "start_hub",
#             is_end=zone_kind == "end_hub",
# 
# )
#hub: loop_d 1 1 [zone=restricted color=orange]

    def parsing_zone(self, line: str, index_of_line: int) -> Zone:
        match_res = ZONE_SHOULD_BE.match(line)
        if match_res is None:
            raise ParsingError("Error, invalid zone syntax in the line: %d" % index_of_line)

        zone_type_from3, name, x_str, y_str, metadata = match_res.groups()
        x, y = int(x_str), int(y_str)

        metadata_dict = self.get_metadata_keyvalue(metadata, index_of_line)

        zone_type_str = metadata_dict.get("zone", ZoneType.NORMAL.value)
        
        try:
            zone_type = ZoneType(zone_type_str)
        except Exception:
            raise ParsingError("Error, invalid zone type in line: %d" % index_of_line)

        color = metadata_dict.get("color", "none")
        max_drones = self.get_parse_of_int(metadata_dict.get("max_drones"), index_of_line, "max_drones")





    def parsing_file_data(self, data_from_file: str) -> ParsedMapData:
        
        lines = data_from_file.splitlines()
        if (not lines):
            raise ParsingError("Error, in the first line should be 'total_drones: <pos_num>'")
        


# pushiiii