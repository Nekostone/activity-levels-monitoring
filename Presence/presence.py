from statemachine import StateMachine, State

class RoomMonitor(StateMachine):
    # Define areas of presence
    living  = State('living room', initial = True)
    bedroom = State('bedroom')
    kitchen = State('kitchen')
    toilet  = State('toilet')
    out     = State('not home')

    # Define transition states

    # Repeated states
    living2living = living.to(living)
    bed2bed       = bedroom.to(bedroom)
    kitch2kitch   = kitchen.to(kitchen)
    shit2shit     = toilet.to(toilet)

    # Transitions
    liv2bed    = living.to(bedroom)
    bed2liv = bedroom.to(living)

    liv2toilet = living.to(toilet)
    toilet2liv = toilet.to(living)

    liv2kitch  = living.to(kitchen)
    kitch2liv  = kitchen.to(living)

    liv2out    = living.to(out)
    out2liv    = out.to(living)