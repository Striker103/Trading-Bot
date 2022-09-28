from transitions import Machine, State


class Fsm(object):
    """The FSM for all Live and Backtest Strategies"""
    states = [State(name='entry', on_enter='enter_entry'),
              State(name='long', on_enter='enter_long', on_exit='exit_long'),
              State(name='short', on_enter='enter_short', on_exit='exit_short'),
              State(name='stop_loss', on_enter='enter_stop_loss'),
              State(name='done', on_enter='enter_done')]

    def __init__(self, strategy):

        # Initialize the state machine
        self.machine = Machine(model=strategy, states=Fsm.states, initial='entry')

        # internal transitions in the corresponding state. When conditions in this State are met it will transition
        # to a specific State. When trigger is called this transition is executed. internal transition DO NOT execute
        # on enter and on exit
        self.machine.add_transition(trigger='entry_to_entry', source='entry',  dest=None, after='execute_entry')
        self.machine.add_transition(trigger='long_to_long', source='long',  dest=None, after='execute_long')
        self.machine.add_transition(trigger='short_to_short', source='short',  dest=None, after='execute_short')
        self.machine.add_transition(trigger='stop_loss_to_stop_loss', source='stop_loss',  dest=None,
                                    after='execute_stop_loss')

        # transitions from one state to another
        self.machine.add_transition(trigger='entry_to_long', source='entry', dest='long')
        self.machine.add_transition(trigger='long_to_entry', source='long', dest='entry')
        self.machine.add_transition(trigger='entry_to_short', source='entry', dest='short')
        self.machine.add_transition(trigger='short_to_entry', source='short', dest='entry')
        self.machine.add_transition(trigger='short_to_stop_loss', source='short', dest='stop_loss')
        self.machine.add_transition(trigger='long_to_stop_loss', source='long', dest='stop_loss')
        self.machine.add_transition(trigger='stop_loss_to_entry', source='stop_loss', dest='entry')
        self.machine.add_transition(trigger='entry_to_done', source='entry', dest='done')
        self.machine.add_transition(trigger='short_to_done', source='short', dest='done')
        self.machine.add_transition(trigger='long_to_done', source='long', dest='done')
        self.machine.add_transition(trigger='stop_loss_to_done', source='stop_loss', dest='done')
