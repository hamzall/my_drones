
# @dataclass(frozen=True)
# class Metrics:
#     """Summary metrics for a completed simulation."""

#     turns: int
#     moved_per_turn_average: float # the average number of drones that move during all simulation turns

            # Turn 1 → 3 drones
            # Turn 2 → 8 drones
            # Turn 3 → 7 drones
            # (3 + 8 + 7) ÷ 3 = 6


#     average_turns_per_drone: float == 4
            # 🟢 في المتوسط، كل drone كيحتاج 4 turns باش يوصل للهدف
            # D1 وصل فـ turn 3  
            # D2 وصل فـ turn 4  
            # D3 وصل فـ turn 5

            # (3 + 4 + 5) ÷ 3 = 4
            # average_turns_per_drone = 4



#     total_path_cost: int #total cost of all movements made by all drones





# @dataclass(frozen=True)
# class PlannedMove:
#     """A planned movement for a drone during the current turn."""

#     drone_id: int
#     source: str
#     destination: str
#     connection_key: Tuple[str, str]
#     connection_name: str
#     move_cost: int



class 