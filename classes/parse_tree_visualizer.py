import graphviz

class ParseTreeVisualizer:
    def __init__(self, parse_tree, symbol_table=None):
        self.parse_tree = parse_tree
        self.selected_node = None
        self.symbol_table = symbol_table
        
    
    def visualize_tree(self, output_path=None):
        if not self.parse_tree:
            print("No parse tree to visualize")
            return
        self.draw(output_path=output_path)

    def draw(self, filename='parse_tree.png', view=True, output_path=None):
        if not self.parse_tree:
            print("No parse tree to visualize")
            return
        dot = graphviz.Digraph(comment='Parse Tree')
        self._add_graphviz_nodes(dot, self.parse_tree)
        dot.format = 'png'
        
        if output_path:
            full_output_path = f'{output_path}/{filename}'
        else:
            full_output_path = filename
            
        dot.render(full_output_path, view=view, cleanup=True)

    def _add_graphviz_nodes(self, dot, node):
        label = f"{node.symbol}\\n[{node.id}]"
        if node.production_rule:
            label += f"\\n{node.production_rule}"
        shape = 'ellipse' if node.is_terminal else 'box'
        color = 'lightblue' if node.is_terminal else 'lightgreen'
        dot.node(str(node.id), label, shape=shape, style='filled', fillcolor=color)
        for child in node.children:
            dot.edge(str(node.id), str(child.id))
            self._add_graphviz_nodes(dot, child)
    
    def _get_all_nodes(self, node):
        nodes = [node]
        for child in node.children:
            nodes.extend(self._get_all_nodes(child))
        return nodes
    
    def select_node_by_id(self, node_id):
        all_nodes = self._get_all_nodes(self.parse_tree)
        for node in all_nodes:
            if node.id == node_id:
                self.select_node(node)
                return True
        return False
    
    def select_node(self, node):
        self.selected_node = node
        print(f"\n=== Selected Node Information ===")
        print(f"Node ID: {node.id}")
        print(f"Symbol: {node.symbol}")
        print(f"Type: {'Terminal' if node.is_terminal else 'Non-terminal'}")
        if node.production_rule:
            print(f"Production Rule: {node.production_rule}")
        print(f"Parent: {node.parent.symbol if node.parent else 'None (Root)'}")
        print(f"Children: {[child.symbol for child in node.children]}")
        print(f"Is Leaf: {len(node.children) == 0}")
        
        if self.symbol_table:
            if node.id in self.symbol_table.declarations:
                decl = self.symbol_table.declarations[node.id]
                print(f"Symbol Info: DECLARATION of '{decl['name']}' in scope {decl['scope_id']}")
                print(f"References: {decl['references']}")
            elif node.id in self.symbol_table.references:
                ref = self.symbol_table.references[node.id]
                print(f"Symbol Info: REFERENCE to '{ref['name']}' (declared at node {ref['declaration_node_id']})")
            else:
                print("Symbol Info: Not a symbol")
        
        print("=" * 35)
    
    def list_all_nodes(self):
        all_nodes = self._get_all_nodes(self.parse_tree)
        print("\n=== All Nodes in Parse Tree ===")
        for node in all_nodes:
            node_type = "Terminal" if node.is_terminal else "Non-terminal"
            print(f"[{node.id}] {node.symbol} ({node_type})")
        print("=" * 32)

