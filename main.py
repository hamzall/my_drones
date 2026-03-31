
import parsing




obj = parsing.ParsingClassData()



# r"^connection:\s+([^\s\-]+)-([^\s\-]+)(?:\s+\[(.*?)\])?$"



try:
    res = (obj.start_parsing("map"))
    
    print(res.drones_num)
    
except Exception as o:
    print(o)
    





