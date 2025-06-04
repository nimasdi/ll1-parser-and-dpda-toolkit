class LL1Parser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.first_sets = {}
        self.follow_sets = {}
        self.parse_table = {}
        self._compute_first_sets()
        self._compute_follow_sets()
        self._build_parse_table()
    
    def _compute_first_sets(self):
        for terminal in self.grammar.terminals:
            self.first_sets[terminal] = {terminal}
        
        for non_terminal in self.grammar.non_terminals:
            self.first_sets[non_terminal] = set()
        
        self.first_sets['eps'] = {'eps'}
        
        changed = True
        while changed:
            changed = False
            for non_terminal in self.grammar.non_terminals:
                for production in self.grammar.get_productions(non_terminal):
                    if not production:  # epsilon production
                        if 'eps' not in self.first_sets[non_terminal]:
                            self.first_sets[non_terminal].add('eps')
                            changed = True
                    else:
                        first_symbol = production[0]
                        old_size = len(self.first_sets[non_terminal])
                        
                        if first_symbol in self.grammar.terminals:
                            self.first_sets[non_terminal].add(first_symbol)
                        else:
                            self.first_sets[non_terminal] |= (self.first_sets[first_symbol] - {'eps'})
                            
                            if all(symbol in self.grammar.non_terminals and 'eps' in self.first_sets[symbol] 
                                   for symbol in production):
                                self.first_sets[non_terminal].add('eps')
                        
                        if len(self.first_sets[non_terminal]) > old_size:
                            changed = True
    
    def _compute_follow_sets(self):
        for non_terminal in self.grammar.non_terminals:
            self.follow_sets[non_terminal] = set()
        
        self.follow_sets[self.grammar.start_symbol].add('$')
        
        changed = True
        while changed:
            changed = False
            for non_terminal in self.grammar.non_terminals:
                for production in self.grammar.get_productions(non_terminal):
                    for i, symbol in enumerate(production):
                        if symbol in self.grammar.non_terminals:
                            old_size = len(self.follow_sets[symbol])
                            
                            # FIRST of what follows
                            if i + 1 < len(production):
                                next_symbol = production[i + 1]
                                if next_symbol in self.grammar.terminals:
                                    self.follow_sets[symbol].add(next_symbol)
                                else:
                                    self.follow_sets[symbol] |= (self.first_sets[next_symbol] - {'eps'})
                                    
                                    # If next symbol can derive epsilon, add FOLLOW of LHS
                                    if 'eps' in self.first_sets[next_symbol]:
                                        self.follow_sets[symbol] |= self.follow_sets[non_terminal]
                            else:
                                # Add FOLLOW of LHS
                                self.follow_sets[symbol] |= self.follow_sets[non_terminal]
                            
                            if len(self.follow_sets[symbol]) > old_size:
                                changed = True
    
    def _build_parse_table(self):
        self.parse_table = {}
        
        for non_terminal in self.grammar.non_terminals:
            for production in self.grammar.get_productions(non_terminal):
                if not production:  # epsilon production
                    for terminal in self.follow_sets[non_terminal]:
                        if (non_terminal, terminal) in self.parse_table:
                            raise ValueError(f"Grammar is not LL(1): conflict at ({non_terminal}, {terminal})")
                        self.parse_table[(non_terminal, terminal)] = production
                else:
                    first_of_production = self._first_of_string(production)
                    for terminal in first_of_production:
                        if terminal != 'eps':
                            if (non_terminal, terminal) in self.parse_table:
                                raise ValueError(f"Grammar is not LL(1): conflict at ({non_terminal}, {terminal})")
                            self.parse_table[(non_terminal, terminal)] = production
                    
                    if 'eps' in first_of_production:
                        for terminal in self.follow_sets[non_terminal]:
                            if (non_terminal, terminal) in self.parse_table:
                                raise ValueError(f"Grammar is not LL(1): conflict at ({non_terminal}, {terminal})")
                            self.parse_table[(non_terminal, terminal)] = production
    
    def _first_of_string(self, symbols):

        if not symbols:
            return {'eps'}
        
        result = set()
        for symbol in symbols:
            if symbol in self.grammar.terminals:
                result.add(symbol)
                break
            else:
                result |= (self.first_sets[symbol] - {'eps'})
                if 'eps' not in self.first_sets[symbol]:
                    break
        else:
            result.add('eps')
        
        return result
    
    def get_parse_table(self):
        return self.parse_table
    
    def print_parse_table(self):
        print("Parse Table:")
        for (non_terminal, terminal), production in self.parse_table.items():
            prod_str = ' '.join(production) if production else 'eps'
            print(f"  ({non_terminal}, {terminal}) -> {prod_str}")

