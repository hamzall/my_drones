from classes_types import Graph
from re import compile
from except_error import ParsingError
from typing import Dict
from classes_types import Connection, Zone, ZoneType

#max_drones
# Capturing Groups
# ^ should start with this
# $ for take all text for match it starting with ^
# r for dont read data with \
# like \n we dont want from it a new line exp
ZONE_SHOULD_BE = compile(
    r"^(start_hub|end_hub|hub):\s+([^\s\-]+)\s+(-?\d+)\s+(-?\d+)(?:\s+\[(.*?)\])?$"
)
CONNECTION_SHOULD_BE = compile(
    r"^connection:\s+([^\s\-]+)-([^\s\-]+)(?:\s+\[(.*?)\])?$"
)
DRONES_NUM_SHOULD_BE = compile(r"^nb_drones:\s+(\d+)$")




class ParsedMapData:
    def __init__(self, drones_num: int, the_graph: Graph) -> None:
        self.drones_num = drones_num
        self.the_graph = the_graph



class ParsingClassData:
    
    def ignore_comments(self, line: str) -> str:
        res = line.find("#")
        if (res == -1):
            return line
        return line[:res]


    def get_drone_numbers(self, first_line: str) -> int:
        match_res = DRONES_NUM_SHOULD_BE.match(first_line)
        if (match_res is None):
            raise ParsingError("Error, Bad Pattern in the first line")
        number_of_drones = int(match_res.group(1))
        if (number_of_drones <= 0):
            raise ParsingError("Error, Please Enter a Positive Drone Numbers")
        return number_of_drones


    def get_metadata_keyvalue(self, text: str | None, index_of_line: int) -> Dict[str, str]:
        if (text is None):
            return {}
        
        stripped_text = text.strip()
        if (not stripped_text):
            return {}
        
        result: Dict[str, str] = {}
        
        for ke_va in stripped_text.split():
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
        # here negative mybe should pass
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
        
        metadata_dict = self.get_metadata_keyvalue(metadata, line_index)

        capacity_of_max_link = self.get_parse_of_int(
            metadata_dict.get("max_link_capacity", "1") , line_index , "max_link_capacity"
        )
        
        is_there_other_key = set(metadata_dict).difference({"max_link_capacity"})
        if (is_there_other_key):
            raise ParsingError("Error, Should be only one key in line %d" % line_index)
        
        return Connection(zone1=zone1, zone2=zone2, max_link_capa=capacity_of_max_link)
    

    def parsing_zone(self, line: str, index_of_line: int) -> Zone:
        match_res = ZONE_SHOULD_BE.match(line)
        if match_res is None:
            raise ParsingError("Error, invalid zone syntax in the line: %d" % index_of_line)

        zone_type_from3, name, x_str, y_str, metadata = match_res.groups()
        x, y = int(x_str), int(y_str)

        metadata_dict = self.get_metadata_keyvalue(metadata, index_of_line)

        zone_type_str = metadata_dict.get("zone", ZoneType.NORMAL.value)
        
        try:
            zone_type_en = ZoneType(zone_type_str)
        except Exception:
            raise ParsingError("Error, invalid zone type in line: %d" % index_of_line)

        color = metadata_dict.get("color", "none")
        max_drones = self.get_parse_of_int(metadata_dict.get("max_drones", "1"), index_of_line, "max_drones")
        
        is_there_other_key = set(metadata_dict).difference({"zone", "color", "max_drones"})
        if (is_there_other_key):
            raise ParsingError("Error, more than expected keys in zone metadata, line: %d" % index_of_line)
        
        return Zone(
            name=name, x=x, y=y, type_of_zone=zone_type_en, color=color,
            max_drones=max_drones, is_start=(zone_type_from3 == "start_hub"), is_end=(zone_type_from3 == "end_hub"))


    def parsing_file_data(self, data_from_file: str) -> ParsedMapData:
        lines = data_from_file.splitlines()
        if (not lines):
            raise ParsingError("Error, in the first line should be 'nb_drones: <pos_num>'")
        ###
        nb_drones = None
        start_index = 0
        for i, raw_line in enumerate(lines):
            clean_line = self.ignore_comments(raw_line).strip()
            if not clean_line:
                continue
            try:
                nb_drones = self.get_drone_numbers(clean_line)
            except ParsingError:
                raise ParsingError(f"Line {i+1}: expected 'nb_drones: <positive_integer>' as first non-comment line")
            start_index = i + 1
            break
        if nb_drones is None:
            raise ParsingError("Missing 'nb_drones: <positive_integer>'")
        ###
        graph_obj = Graph({}, {}, {})
        
        
        ##
        for index_of_line, data_in_line in enumerate(lines[start_index:], start=start_index + 1):
        ##
            good_line = self.ignore_comments(data_in_line).strip()
            if not good_line or good_line == "":
                continue
            
            if (good_line.startswith("connection:")):
                connection_obj = self.parse_connection(good_line, index_of_line)
                try:
                    graph_obj.add_connection(connection_obj)
                except Exception:
                    raise ParsingError("Error, When Add a Connection line: %d" % index_of_line)
                continue
            
            zone_obj = self.parsing_zone(good_line, index_of_line)
            try:
                graph_obj.add_zone(zone_obj)
            except Exception:
                raise ParsingError("Error, When Add a Zone, line %d" % index_of_line)
        
        if graph_obj.start_name is None:
            raise ParsingError("Error, Map must al least include one start_hub as max and min")
        
        if graph_obj.end_name is None:
            raise ParsingError("Error, Map must al least include one end_hub as max and min")
        
        return ParsedMapData(drones_num=nb_drones, the_graph=graph_obj)


    def start_parsing(self, file_name: str) -> ParsedMapData:
        with open(file_name, "r") as file:
            file_data = file.read()
            return self.parsing_file_data(file_data)



# pushiiii
# nb_drones: +2
# (+2, -0)...