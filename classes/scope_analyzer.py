import re
from classes.symbole_table import SymbolTable

class ScopeAnalyzer:
    def __init__(self, parse_tree, grammar):
        self.parse_tree = parse_tree
        self.grammar = grammar
        self.symbol_table = SymbolTable()
        self.variable_terminals = self._detect_variable_terminals()
    
    def _detect_variable_terminals(self):
        variable_terminals = set()
        identifier_keywords = ['identifier', 'id', 'var', 'name', 'variable']
        
        for terminal in self.grammar.terminals:
            terminal_lower = terminal.lower()
            
            if any(keyword in terminal_lower for keyword in identifier_keywords):
                variable_terminals.add(terminal)
                pattern = self.grammar.terminal_patterns.get(terminal, 'unknown')
                print(f"Detected variable terminal by name: {terminal} with pattern: {pattern}")
        
        if not variable_terminals:
            print("No variable terminals detected.")
            print("Available terminals and their patterns:")
            for terminal, pattern in self.grammar.terminal_patterns.items():
                print(f"  {terminal}: {pattern}")
        
        return variable_terminals
    
    def analyze(self):
        if not self.variable_terminals:
            print("No variable terminals detected in grammar")
            return self.symbol_table
        
        print(f"Using variable terminals: {self.variable_terminals}")
        self._analyze_with_scopes(self.parse_tree)
        
        return self.symbol_table
    
    def _analyze_with_scopes(self, node):
        if not self.symbol_table.scopes:
            self.symbol_table.enter_scope('global')
        
        # if this node creates a new scope
        if self._creates_new_scope(node):
            scope_type = self._get_scope_type(node)
            self.symbol_table.enter_scope(scope_type, node)
            
            for child in node.children:
                self._analyze_with_scopes(child)
            
            self.symbol_table.exit_scope()
        else:
            # if this node is a variable declaration or reference
            if self._is_variable_node(node):
                var_name = self._extract_variable_name(node)
                if var_name:
                    # Determine if this is a declaration or reference based on context
                    if self._is_declaration_context(node):
                        self.symbol_table.declare_symbol(var_name, node.id, node)
                    else:
                        # This is a reference - look for declaration in current and parent scopes
                        declaration_id = self.symbol_table.reference_symbol(var_name, node.id, node)
                        if not declaration_id:
                            self.symbol_table.declare_symbol(var_name, node.id, node)
            
            for child in node.children:
                self._analyze_with_scopes(child)
    
    def _creates_new_scope(self, node):
        if node.is_terminal:
            return False
        
        # Only create new scopes for functions/procedures, not for control flow blocks
        function_scope_symbols = [
            'Function', 'FunctionDeclaration', 'Procedure', 'Method',
            'Program', 'Module', 'Namespace', 'Class'
        ]
        
        return node.symbol in function_scope_symbols
    
    def _get_scope_type(self, node):
        symbol_lower = node.symbol.lower()
        
        if 'function' in symbol_lower or 'procedure' in symbol_lower or 'method' in symbol_lower:
            return 'function'
        elif 'program' in symbol_lower:
            return 'global'
        elif 'class' in symbol_lower:
            return 'class'
        else:
            return 'function'  # Default to function scope
    
    def _is_declaration_context(self, node):
        if not node.parent:
            return True  
        
        parent = node.parent
        
        # Check if this is an assignment (left side of =)
        if parent and len(parent.children) >= 2:
            siblings = parent.children
            try:
                node_index = siblings.index(node)
                
                # If next sibling is assignment operator, this is a declaration/assignment
                if (node_index + 1 < len(siblings) and 
                    siblings[node_index + 1].symbol in ['=', 'EQUALS', 'ASSIGN']):
                    
                    # Check if this variable name already exists in current function scope
                    var_name = self._extract_variable_name(node)
                    if var_name and self.symbol_table.scopes:
                        current_scope = self.symbol_table.scopes[-1]
                        return var_name not in current_scope['symbols']
                    return True
            except ValueError:
                pass
        
        return False
    
    def _is_variable_node(self, node):
        if not node.is_terminal:
            return False
        
        if node.symbol in self.variable_terminals:
            return True
        
        if self._is_variable_value(node.symbol):
            return True
        return False
    
    def _is_variable_value(self, symbol):
        for terminal in self.variable_terminals:
            pattern = self.grammar.terminal_patterns.get(terminal)
            if pattern:
                try:
                    clean_pattern = pattern.replace(' ', '')
                    compiled_pattern = re.compile(f'^{clean_pattern}$')
                    if compiled_pattern.match(symbol):
                        return True
                    if compiled_pattern.match(symbol):
                        return True
                except re.error:
                    continue
        
        return False
    
    def _extract_variable_name(self, node):
        if node.is_terminal:
            if self._is_variable_value(node.symbol):
                return node.symbol
        
            if node.symbol in self.variable_terminals:
                return node.symbol
        
        return None

