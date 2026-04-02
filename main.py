
import argparse
import sys
from typing import Sequence

from except_error import GlobalMainError
from parsing import ParsedMapData, ParsingClassData
from simulation import Simulation
from terminal_colors import DisplayColors

with_color = 14


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Fly-in mandatory command line interface."""
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 1:
        print("Usage: python main.py <map_file>", file=sys.stderr)
        return 1

    map_file = argv[0]
    parser = ParsingClassData()

    try:
        parsed_map = parser.start_parsing(map_file)
        simulator = Simulation(parsed_map.the_graph, parsed_map.drones_num)
        output_lines, _metrics = simulator.run()
    except (GlobalMainError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


    #without color
    if with_color == 0:
        for line in output_lines:
            print(line)
        return 0




    # get color
    for line in output_lines:
        colored_tokens = []

        for token in line.split():
            prefix, raw_destination = token.split("-", 1)
            zone = parsed_map.the_graph.zones.get(raw_destination)

            if zone is None:
                colored_tokens.append(token)
                continue

            colorize_obj = DisplayColors()
            colored_destination = colorize_obj.get_color(raw_destination, zone.color)
            
            colored_tokens.append(f"{prefix}-{colored_destination}")

        print(" ".join(colored_tokens))


    return 0


if __name__ == "__main__":
    raise SystemExit(main())
