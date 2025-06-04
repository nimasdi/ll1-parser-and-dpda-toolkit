import re

class SymbolRenamer:
    def __init__(self, parse_tree, symbol_table, lexer):
        self.parse_tree = parse_tree
        self.symbol_table = symbol_table
        self.lexer = lexer
        self.original_tokens = []
    
    def rename_symbol(self, target_node_id, new_name):
        if new_name in {'function', 'return'}:
            raise ValueError(f"Renaming to '{new_name}' is not allowed (reserved keyword)")

        if not self._is_valid_identifier(new_name):
            raise ValueError(f"'{new_name}' is not a valid identifier")
        
        declaration_node_id = None
        # Check if target node is a declaration
        if target_node_id in self.symbol_table.declarations:
            declaration_node_id = target_node_id
        # Check if target node is a reference
        elif target_node_id in self.symbol_table.references:
            declaration_node_id = self.symbol_table.references[target_node_id]['declaration_node_id']
        else:
            raise ValueError(f"Node {target_node_id} is not a symbol declaration or reference")
        
        if not declaration_node_id or declaration_node_id not in self.symbol_table.declarations:
            raise ValueError(f"Declaration not found for node {target_node_id}")
        
        declaration_info = self.symbol_table.declarations[declaration_node_id]
        # Prevent renaming if the original name is 'function' or 'return'
        if declaration_info['name'] in {'function', 'return'}:
            raise ValueError(f"Renaming symbol '{declaration_info['name']}' is not allowed (reserved keyword)")

        nodes_to_rename = [declaration_node_id] + declaration_info['references']
        
        print(f"Renaming '{declaration_info['name']}' to '{new_name}' in nodes: {nodes_to_rename}")
        
        leaves = self.parse_tree.get_leaves()
        
        return self._reconstruct_source_with_rename(leaves, nodes_to_rename, new_name)
    
    def get_symbol_info(self, node_id):
        info = {}
        
        if node_id in self.symbol_table.declarations:
            decl = self.symbol_table.declarations[node_id]
            info['type'] = 'declaration'
            info['name'] = decl['name']
            info['scope_id'] = decl['scope_id']
            info['references'] = decl['references']
        
        elif node_id in self.symbol_table.references:
            ref = self.symbol_table.references[node_id]
            info['type'] = 'reference'
            info['name'] = ref['name']
            info['declaration_node_id'] = ref['declaration_node_id']
        
        else:
            info['type'] = 'not_symbol'
        
        return info
    
    def save_renamed_code_to_file(self, target_node_id, new_name, output_filename, prefix_address="E:\IUST\Term4\TLA-Entezari\Project"):
        try:
            renamed_code = self.rename_symbol(target_node_id, new_name)
            
            if '/' not in output_filename:
                output_filename = f'{prefix_address}/{output_filename}'
            
            with open(output_filename, 'w') as f:
                f.write(renamed_code)
            
            print(f"Renamed code saved to: {output_filename}")
            return True
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False
    
    def _is_valid_identifier(self, name):
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))
    
    def _reconstruct_source_with_rename(self, leaves, nodes_to_rename, new_name):
        result = []

        for leaf in leaves:
            if leaf.symbol == 'ε':
                continue

            # Prevent renaming of 'function' and 'return' in the leaves
            if leaf.id in nodes_to_rename and leaf.symbol not in {'function', 'return'}:
                result.append(new_name)
                print(f"Renamed node {leaf.id}: '{leaf.symbol}' -> '{new_name}'")
            else:
                result.append(leaf.symbol)

        return self.add_spacing(result)
    
    def add_spacing(self, tokens):
        if not tokens:
            return ""
        
        spaced_result = [tokens[0]]
        
        for i in range(1, len(tokens)):
            prev_token = tokens[i-1]
            current_token = tokens[i]
            
            needs_space = self._needs_space_between(prev_token, current_token)
            
            if needs_space:
                spaced_result.append(' ')
            
            spaced_result.append(current_token)
        
        return ''.join(spaced_result)
    
    def _needs_space_between(self, prev_token, current_token):
        return True
    
    def _is_alphanumeric_token(self, token):
        return token.replace('_', '').isalnum()

