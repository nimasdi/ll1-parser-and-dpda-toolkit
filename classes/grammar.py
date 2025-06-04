class Grammar:
    def __init__(self):
        self.non_terminals = set()
        self.terminals = set()
        self.productions = {}  
        self.start_symbol = None
        self.terminal_patterns = {}  
        
    def read_from_file(self, filepath):
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
            
            current_production_left = None
            current_production_right = ""
            
            for line in lines:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('START ='):
                    self.start_symbol = line.split('=')[1].strip()
                    continue
                elif line.startswith('NON_TERMINALS ='):
                    nt_list = line.split('=')[1].strip()
                    self.non_terminals = {nt.strip() for nt in nt_list.split(',') if nt.strip()}
                    continue
                elif line.startswith('TERMINALS ='):
                    t_list = line.split('=')[1].strip()
                    self.terminals = {t.strip() for t in t_list.split(',') if t.strip()}
                    continue
                elif '->' in line:

                    if current_production_left and current_production_right:
                        self._process_production(current_production_left, current_production_right)
                    
                    parts = line.split('->', 1)
                    left_side = parts[0].strip()
                    right_side = parts[1].strip()
                    
                    if left_side in self.terminals:
                        pattern = right_side.strip()
                        if pattern.startswith('/') and pattern.endswith('/'):
                            pattern = pattern[1:-1] 
                        self.terminal_patterns[left_side] = pattern
                        current_production_left = None
                        current_production_right = ""
                    elif left_side in self.non_terminals:
                        current_production_left = left_side
                        current_production_right = right_side
                else:
                    if current_production_left:
                        current_production_right += " " + line
            
            if current_production_left and current_production_right:
                self._process_production(current_production_left, current_production_right)
            
            return True
                
        except Exception as e:
            print(f"Error reading grammar from file: {e}")
            return False
    
    def _process_production(self, left_side, right_side):
        production_list = []
        for prod in right_side.split('|'):
            prod = prod.strip()
            if prod == 'eps' or prod == '':
                production_list.append('')
            else:
                production_list.append(prod.split())
        self.productions[left_side] = production_list
    
    def get_productions(self, non_terminal):
        return self.productions.get(non_terminal, [])
    
    def get_non_terminals(self):
        return self.non_terminals
    
    def get_terminals(self):
        return self.terminals
    
    def get_start_symbol(self):
        return self.start_symbol
    
    def get_terminal_pattern(self, terminal):
        return self.terminal_patterns.get(terminal)

