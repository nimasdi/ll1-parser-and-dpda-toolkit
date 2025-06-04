class ParseTreeNode:
    node_counter = 0
    
    def __init__(self, symbol, is_terminal=False, production_rule=None):
        ParseTreeNode.node_counter += 1
        self.id = ParseTreeNode.node_counter
        self.symbol = symbol
        self.is_terminal = is_terminal
        self.children = []
        self.parent = None
        self.production_rule = production_rule
        
    def add_child(self, child):
        child.parent = self
        self.children.append(child)
        
    def get_leaves(self):
        if not self.children:
            return [self]
        leaves = []
        for child in self.children:
            leaves.extend(child.get_leaves())
        return leaves
    
    def __str__(self):
        return f"Node({self.id}: {self.symbol})"
    
    def __repr__(self):
        return self.__str__()


class GeneralDPDA:
    def __init__(self):
        self.states = set()
        self.input_alphabet = set()
        self.stack_alphabet = set()
        self.transitions = {}
        self.start_state = None
        self.start_stack_symbol = None
        self.accept_states = set()
    
    def add_state(self, state, is_start=False, is_accept=False):
        self.states.add(state)
        if is_start:
            self.start_state = state
        if is_accept:
            self.accept_states.add(state)
    
    def add_input_symbol(self, symbol):
        self.input_alphabet.add(symbol)
    
    def add_stack_symbol(self, symbol, is_start=False):
        self.stack_alphabet.add(symbol)
        if is_start:
            self.start_stack_symbol = symbol
    
    def add_transition(self, from_state, input_symbol, stack_symbol, to_state, new_stack_symbols):
        key = (from_state, input_symbol, stack_symbol)
        if key in self.transitions:
            raise ValueError(f"Transition already exists for {key}")
        
        if from_state not in self.states:
            raise ValueError(f"State '{from_state}' is not defined")
        if to_state not in self.states:
            raise ValueError(f"State '{to_state}' is not defined")
        if input_symbol and input_symbol not in self.input_alphabet and input_symbol != '':
            raise ValueError(f"Input symbol '{input_symbol}' is not in the input alphabet")
        if stack_symbol not in self.stack_alphabet:
            raise ValueError(f"Stack symbol '{stack_symbol}' is not in the stack alphabet")
        for symbol in new_stack_symbols:
            if symbol not in self.stack_alphabet:
                raise ValueError(f"Stack symbol '{symbol}' is not in the stack alphabet")
        
        self.transitions[key] = (to_state, new_stack_symbols)
    
    def process_input(self, input_string):
        if self.start_state is None:
            raise ValueError("Start state is not defined")
        if self.start_stack_symbol is None:
            raise ValueError("Start stack symbol is not defined")
        
        current_state = self.start_state
        remaining_input = list(input_string)
        stack = [self.start_stack_symbol]
        
        trace = [f"Initial: State={current_state}, Stack={stack}, Input={remaining_input}"]
        
        step_count = 0
        
        while True:
            step_count += 1
            
            if not stack:
                break
                
            stack_top = stack[-1]
            current_input = remaining_input[0] if remaining_input else '$'
            
            # Handle Z0 and transitions
            if stack_top == 'Z0':
                if current_input == '$':
                    current_state = 'q2'
                    break
                elif (current_state, '', stack_top) in self.transitions:
                    next_state, stack_action = self.transitions[(current_state, '', stack_top)]
                    stack.pop()
                    for symbol in reversed(stack_action):
                        stack.append(symbol)
                    trace.append(f"Step {step_count}: Initialize with start symbol, Stack={stack}")
                    current_state = next_state
                    continue
                else:
                    break
            
            # epsilon transitions
            elif (current_state, '', stack_top) in self.transitions:
                next_state, stack_action = self.transitions[(current_state, '', stack_top)]
                stack.pop()
                for symbol in reversed(stack_action):
                    stack.append(symbol)
                trace.append(f"Step {step_count}: ε-transition on {stack_top} -> {stack_action}, Stack={stack}")
                current_state = next_state
                continue
            
            # input transitions
            elif current_input and (current_state, current_input, stack_top) in self.transitions:
                next_state, stack_action = self.transitions[(current_state, current_input, stack_top)]
                stack.pop()
                consumed = remaining_input.pop(0)
                for symbol in reversed(stack_action):
                    stack.append(symbol)
                trace.append(f"Step {step_count}: Match '{consumed}' with {stack_top}, Stack={stack}")
                current_state = next_state
                continue
            
            else:
                trace.append(f"Step {step_count}: ERROR - No transition available for state={current_state}, input='{current_input}', stack_top='{stack_top}'")
                break
        
        # Accept by final state or empty stack
        is_accepted = (current_state == 'q2' or current_state in self.accept_states or 
                      (not remaining_input or remaining_input == ['$']) and 
                      (not stack or stack == ['Z0']))
        
        trace.append(f"Final: State={current_state}, Stack={stack}, Remaining={remaining_input}")
        trace.append(f"Result: {'ACCEPTED' if is_accepted else 'REJECTED'}")
        
        return is_accepted, trace


class DPDA:
    def __init__(self):
        self.states = set()
        self.input_alphabet = set()
        self.stack_alphabet = set()
        self.transitions = {}
        self.start_state = None
        self.start_stack_symbol = None
        self.accept_states = set()
        self.parse_table = {}
        self.grammar = None
        self.parse_tree = None
        self.node_stack = []  # track nodes
    
    def add_state(self, state, is_start=False, is_accept=False):
        self.states.add(state)
        if is_start:
            self.start_state = state
        if is_accept:
            self.accept_states.add(state)
    
    def add_input_symbol(self, symbol):
        self.input_alphabet.add(symbol)
    
    def add_stack_symbol(self, symbol, is_start=False):
        self.stack_alphabet.add(symbol)
        if is_start:
            self.start_stack_symbol = symbol
    
    def add_transition(self, from_state, input_symbol, stack_symbol, to_state, new_stack_symbols):
        key = (from_state, input_symbol, stack_symbol)
        if key in self.transitions:
            raise ValueError(f"Transition already exists for {key}")
        
        if from_state not in self.states:
            raise ValueError(f"State '{from_state}' is not defined")
        if to_state not in self.states:
            raise ValueError(f"State '{to_state}' is not defined")
        if input_symbol and input_symbol not in self.input_alphabet and input_symbol != '':
            raise ValueError(f"Input symbol '{input_symbol}' is not in the input alphabet")
        if stack_symbol not in self.stack_alphabet:
            raise ValueError(f"Stack symbol '{stack_symbol}' is not in the stack alphabet")
        for symbol in new_stack_symbols:
            if symbol not in self.stack_alphabet:
                raise ValueError(f"Stack symbol '{symbol}' is not in the stack alphabet")
        
        self.transitions[key] = (to_state, new_stack_symbols)
    
    def process_input(self, input_string):
        if self.start_state is None:
            raise ValueError("Start state is not defined")
        if self.start_stack_symbol is None:
            raise ValueError("Start stack symbol is not defined")
        
        current_state = self.start_state
        remaining_input = list(input_string)
        stack = [self.start_stack_symbol]
        
        trace = [f"Initial: State={current_state}, Stack={stack}, Input={remaining_input}"]
        
        step_count = 0
        
        while True:
            step_count += 1
            
            if not stack:
                break
                
            stack_top = stack[-1]
            current_input = remaining_input[0] if remaining_input else '$'
            
            # ll1 parse
            if self.parse_table and self.grammar and stack_top in self.grammar.non_terminals:
                if (stack_top, current_input) in self.parse_table:
                    production = self.parse_table[(stack_top, current_input)]
                    stack.pop()
                    
                    if production:
                        for symbol in reversed(production):
                            stack.append(symbol)
                        trace.append(f"Step {step_count}: Expand {stack_top} -> {' '.join(production)}, Stack={stack}")
                    else:
                        trace.append(f"Step {step_count}: Expand {stack_top} -> ε, Stack={stack}")
                    continue
                else:
                    trace.append(f"Step {step_count}: ERROR - No parse table entry for ({stack_top}, {current_input})")
                    break
            
            # terminal matching with input
            elif (self.grammar and stack_top in self.grammar.terminals) or stack_top in self.input_alphabet:
                if current_input == stack_top:
                    stack.pop()
                    if remaining_input:
                        consumed = remaining_input.pop(0)
                        trace.append(f"Step {step_count}: Match '{consumed}', Stack={stack}, Remaining={remaining_input}")
                    continue
                else:
                    trace.append(f"Step {step_count}: ERROR - Expected '{stack_top}' but found '{current_input}'")
                    break
            
            #(Z0 and transitions)
            elif stack_top == 'Z0':
                if current_input == '$':
                    current_state = 'q2'
                    break
                elif (current_state, '', stack_top) in self.transitions:
                    next_state, stack_action = self.transitions[(current_state, '', stack_top)]
                    stack.pop()
                    for symbol in reversed(stack_action):
                        stack.append(symbol)
                    trace.append(f"Step {step_count}: Initialize with start symbol, Stack={stack}")
                    current_state = next_state
                    continue
                else:
                    break
            
            # epsilon transitions
            elif (current_state, '', stack_top) in self.transitions:
                next_state, stack_action = self.transitions[(current_state, '', stack_top)]
                stack.pop()
                for symbol in reversed(stack_action):
                    stack.append(symbol)
                trace.append(f"Step {step_count}: ε-transition on {stack_top} -> {stack_action}, Stack={stack}")
                current_state = next_state
                continue
            
            # input transitions
            elif current_input and (current_state, current_input, stack_top) in self.transitions:
                next_state, stack_action = self.transitions[(current_state, current_input, stack_top)]
                stack.pop()
                consumed = remaining_input.pop(0)
                for symbol in reversed(stack_action):
                    stack.append(symbol)
                trace.append(f"Step {step_count}: Match '{consumed}' with {stack_top}, Stack={stack}")
                current_state = next_state
                continue
            
            else:
                trace.append(f"Step {step_count}: ERROR - No transition available for state={current_state}, input='{current_input}', stack_top='{stack_top}'")
                break
        
        is_accepted = (current_state == 'q2' or current_state in self.accept_states or 
                      (not remaining_input or remaining_input == ['$']) and 
                      (not stack or stack == ['Z0']))
        
        trace.append(f"Final: State={current_state}, Stack={stack}, Remaining={remaining_input}")
        trace.append(f"Result: {'ACCEPTED' if is_accepted else 'REJECTED'}")
        
        return is_accepted, trace

    def process_input_with_tree(self, input_string):
        if self.start_state is None:
            raise ValueError("Start state is not defined")
        if self.start_stack_symbol is None:
            raise ValueError("Start stack symbol is not defined")
        
        ParseTreeNode.node_counter = 0
        self.parse_tree = None
        self.node_stack = []
        
        current_state = self.start_state
        remaining_input = list(input_string)
        stack = [self.start_stack_symbol]
        
        trace = [f"Initial: State={current_state}, Stack={stack}, Input={remaining_input}"]
        
        step_count = 0
        
        while True:
            step_count += 1
            
            if not stack:
                break
                
            stack_top = stack[-1]
            current_input = remaining_input[0] if remaining_input else '$'
            
            if self.parse_tree is None and stack_top == 'Z0':
                if (current_state, '', stack_top) in self.transitions:
                    next_state, stack_action = self.transitions[(current_state, '', stack_top)]
                    stack.pop()
                    
                    start_symbol = stack_action[0] if stack_action else None
                    if start_symbol and start_symbol in self.grammar.non_terminals:
                        self.parse_tree = ParseTreeNode(start_symbol)
                        self.node_stack = [self.parse_tree]
                    
                    for symbol in reversed(stack_action):
                        stack.append(symbol)
                    trace.append(f"Step {step_count}: Initialize with start symbol, Stack={stack}")
                    current_state = next_state
                    continue
                else:
                    break
            
            # parse table entries for non-terminals
            if self.parse_tree and self.grammar and stack_top in self.grammar.non_terminals:
                if (stack_top, current_input) in self.parse_table:
                    production = self.parse_table[(stack_top, current_input)]
                    stack.pop()
                    
                    # find the corresponding node in node_stack
                    current_node = None
                    for i in range(len(self.node_stack) - 1, -1, -1):
                        if self.node_stack[i].symbol == stack_top:
                            current_node = self.node_stack.pop(i)
                            break
                    
                    if current_node:
                        current_node.production_rule = f"{stack_top} -> {' '.join(production) if production else 'ε'}"
                        
                        # children for the current node     
                        if production:
                            for symbol in production:
                                child_node = ParseTreeNode(
                                    symbol, 
                                    is_terminal=(symbol in self.grammar.terminals),
                                    production_rule=None
                                )
                                current_node.add_child(child_node)
                                
                                if symbol in self.grammar.non_terminals:
                                    self.node_stack.append(child_node)
                            
                            for symbol in reversed(production):
                                stack.append(symbol)
                        else:
                            # epsilon production
                            epsilon_child = ParseTreeNode('ε', is_terminal=True)
                            current_node.add_child(epsilon_child)
                        
                        trace.append(f"Step {step_count}: Expand {stack_top} -> {' '.join(production) if production else 'ε'}, Stack={stack}")
                    continue
                else:
                    trace.append(f"Step {step_count}: ERROR - No parse table entry for ({stack_top}, {current_input})")
                    break
            
            # terminal matching
            elif (self.grammar and stack_top in self.grammar.terminals) or stack_top in self.input_alphabet:
                if current_input == stack_top:
                    stack.pop()
                    if remaining_input:
                        consumed = remaining_input.pop(0)
                        
                        if hasattr(self, 'current_lexeme_values') and stack_top in self.current_lexeme_values:
                            actual_value = self.current_lexeme_values[stack_top].pop(0) if self.current_lexeme_values[stack_top] else consumed
                            self._update_terminal_node_with_lexeme(stack_top, actual_value)
                        
                        trace.append(f"Step {step_count}: Match '{consumed}', Stack={stack}, Remaining={remaining_input}")
                    continue
                else:
                    trace.append(f"Step {step_count}: ERROR - Expected '{stack_top}' but found '{current_input}'")
                    break
            
            elif stack_top == 'Z0':
                if current_input == '$':
                    current_state = 'q2'
                    break
                else:
                    break
            else:
                trace.append(f"Step {step_count}: ERROR - No transition available")
                break
        
        is_accepted = (current_state == 'q2' or current_state in self.accept_states or 
                      (not remaining_input or remaining_input == ['$']) and 
                      (not stack or stack == ['Z0']))
        
        trace.append(f"Final: State={current_state}, Stack={stack}, Remaining={remaining_input}")
        trace.append(f"Result: {'ACCEPTED' if is_accepted else 'REJECTED'}")
        
        return is_accepted, trace, self.parse_tree
    
    def _update_terminal_node_with_lexeme(self, terminal_type, actual_value):
        """Find and update terminal nodes with actual lexeme values"""
        def update_node(node):
            if node.is_terminal and node.symbol == terminal_type:
                node.symbol = actual_value
                return True
            for child in node.children:
                if update_node(child):
                    return True
            return False
        
        if self.parse_tree:
            update_node(self.parse_tree)
