
"""Create My Custome Exception Errors"""



# for all project errors
class GlobalMainError(Exception):
    pass


# only simulation errors
class SimError(GlobalMainError):
    pass


# for parsing errors
class ParsingError(GlobalMainError):
    pass

