
import argparse
import sys
from typing import Sequence

from except_error import GlobalMainError
from parsing import ParsedMapData
from simulation import Simulation
from terminal_colors import DisplayColors




def main(argv: Sequence[str] | None = None) -> int:
    """Run the Fly-in mandatory command line interface."""
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 1:
        print("Usage: python main.py <map_file>", file=sys.stderr)
        return 1

    map_file = argv[0]
    parser = ParsedMapData()

    try:
        parsed_map = parser.parse_file(map_file)
        simulator = Simulation(parsed_map.graph, parsed_map.nb_drones)
        output_lines, _metrics = simulator.run()
    except (GlobalMainError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for line in output_lines:
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
