from typing import Dict

COLORS: Dict[str, str] = {
    "yellow": "33",
    "white": "37",
    "grey": "90",
    "black": "30",
    "red": "31",
    "green": "32",
    "blue": "34"
}
RESET = "\033[0m"


class DisplayColors:
    
    def get_color(self, text: str, color_choosen: str) -> str:
        color = COLORS.get(color_choosen.lower(), "35")
        return "\033[%sm%s%s" % (color, text, RESET)
