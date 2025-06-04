from classes.dpda import DPDA

class LL1ToDPDA:
    def __init__(self, ll1_parser):
        self.ll1_parser = ll1_parser
        self.grammar = ll1_parser.grammar
        self.parse_table = ll1_parser.get_parse_table()
    
    def convert_to_dpda(self):
        dpda = DPDA()
        
        dpda.add_state('q0', is_start=True)
        dpda.add_state('q1')
        dpda.add_state('q2', is_accept=True)
        
        # input terminals
        for terminal in self.grammar.terminals:
            dpda.add_input_symbol(terminal)
        dpda.add_input_symbol('$')
        
        # terminals + non-terminals + special symbols
        dpda.add_stack_symbol('Z0', is_start=True)
        for terminal in self.grammar.terminals:
            dpda.add_stack_symbol(terminal)
        for non_terminal in self.grammar.non_terminals:
            dpda.add_stack_symbol(non_terminal)
        
        dpda.parse_table = self.parse_table
        dpda.grammar = self.grammar
        
        dpda.add_transition('q0', '', 'Z0', 'q1', [self.grammar.start_symbol, 'Z0'])
        
        for terminal in self.grammar.terminals:
            dpda.add_transition('q1', terminal, terminal, 'q1', [])
    
        dpda.add_transition('q1', '$', 'Z0', 'q2', [])
        
        return dpda

