class SymbolTable:
    def __init__(self):
        self.scopes = []  
        self.declarations = {}  # Maps node_id to declaration info
        self.references = {}  # Maps node_id to reference info
        self.scope_counter = 0
    
    def enter_scope(self, scope_type, scope_node=None):
        self.scope_counter += 1
        scope = {
            'id': self.scope_counter,
            'type': scope_type,  # 'function', 'block', 'global'
            'node': scope_node,
            'symbols': {},  # Maps symbol_name to declaration_node_id
            'parent': self.scopes[-1]['id'] if self.scopes else None
        }
        self.scopes.append(scope)
        return scope['id']
    
    def exit_scope(self):
        if self.scopes:
            return self.scopes.pop()
        return None
    
    def declare_symbol(self, symbol_name, node_id, node):
        if not self.scopes:
            return False
        
        current_scope = self.scopes[-1]
        current_scope['symbols'][symbol_name] = node_id
        
        self.declarations[node_id] = {
            'name': symbol_name,
            'scope_id': current_scope['id'],
            'node': node,
            'references': [] 
        }
        return True
    
    def reference_symbol(self, symbol_name, node_id, node):
        # Find the declaration in current scope only for function-scoped variables
        current_scope = self.scopes[-1] if self.scopes else None
        
        if current_scope and symbol_name in current_scope['symbols']:
            declaration_node_id = current_scope['symbols'][symbol_name]
            
            self.references[node_id] = {
                'name': symbol_name,
                'declaration_node_id': declaration_node_id,
                'node': node
            }
            
            if declaration_node_id in self.declarations:
                self.declarations[declaration_node_id]['references'].append(node_id)
            
            return declaration_node_id
        
        # Only search parent scopes if current scope is not a function scope
        if current_scope and current_scope['type'] != 'function':
            for scope in reversed(self.scopes[:-1]):  # Exclude current scope
                if symbol_name in scope['symbols']:
                    declaration_node_id = scope['symbols'][symbol_name]
                    
                    self.references[node_id] = {
                        'name': symbol_name,
                        'declaration_node_id': declaration_node_id,
                        'node': node
                    }
                    
                    if declaration_node_id in self.declarations:
                        self.declarations[declaration_node_id]['references'].append(node_id)
                    
                    return declaration_node_id
                
                # Stop at function boundaries
                if scope['type'] == 'function':
                    break
        
        return None
    
    def get_current_scope(self):
        return self.scopes[-1] if self.scopes else None

