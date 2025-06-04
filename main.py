import os
from classes.grammar import Grammar
from classes.scope_analyzer import ScopeAnalyzer
from classes.symbole_renamer import SymbolRenamer
from classes.parse_tree_visualizer import ParseTreeVisualizer
from classes.lexer import Lexer
from classes.ll1_parser import LL1Parser
from classes.ll1_to_dpda import LL1ToDPDA

def main():

    grammar_file = 'grammar1.txt'
    input_file = 'code1.txt'
    folder_address = os.path.dirname(os.path.abspath(__file__))
    
    grammar = Grammar()
    if not grammar.read_from_file(grammar_file):
        print("Failed to read grammar from file.")
        return
    
    print("=== Grammar Information ===")
    print("Non-terminals:", grammar.get_non_terminals())
    print("Terminals:", grammar.get_terminals())
    print("Start Symbol:", grammar.get_start_symbol())
    print()
    
    print("Productions:")
    for nt in grammar.get_non_terminals():
        productions = grammar.get_productions(nt)
        for prod in productions:
            prod_str = ' '.join(prod) if prod else 'eps'
            print(f"  {nt} -> {prod_str}")
    print()
    
    try:
        ll1_parser = LL1Parser(grammar)
        print("=== Parse Table ===")
        ll1_parser.print_parse_table()
        print()
        
        # Convert to DPDA
        converter = LL1ToDPDA(ll1_parser)
        dpda = converter.convert_to_dpda()
        
        print("=== DPDA Information ===")
        print("States:", dpda.states)
        print("Input Alphabet:", dpda.input_alphabet)
        print("Stack Alphabet:", dpda.stack_alphabet)
        print("Start State:", dpda.start_state)
        print("Accept States:", dpda.accept_states)
        print()
        
        print("Transitions:")
        for (from_state, input_sym, stack_sym), (to_state, new_stack) in dpda.transitions.items():
            input_str = input_sym if input_sym else 'ε'
            stack_str = ' '.join(new_stack) if new_stack else 'ε'
            print(f"  δ({from_state}, {input_str}, {stack_sym}) = ({to_state}, {stack_str})")
        print()
        
        print("=== Lexer Test ===")
        lexer = Lexer(grammar)

        with open(input_file, 'r') as file:
            test_input = file.read()
        test_input = test_input.strip()
        if not test_input:
            raise ValueError("Input file is empty or contains only whitespace.")
        print(f"Input: {test_input}")
        tokens = lexer.tokenize(test_input)
        print("Tokens:")
        for token_type, token_value in tokens:
            print(f"  {token_type}: '{token_value}'")
        print()
        
        print("=== DPDA Test with Parse Tree ===")
        token_string = [token_type for token_type, _ in tokens if token_type != 'ERROR'] + ['$']
        print(f"Token sequence: {' '.join(token_string)}")
        
        lexeme_values = {}
        for token_type, token_value in tokens:
            if token_type != 'ERROR':
                if token_type not in lexeme_values:
                    lexeme_values[token_type] = []
                lexeme_values[token_type].append(token_value)
        
        dpda.current_lexeme_values = lexeme_values
        
        accepted, trace, parse_tree = dpda.process_input_with_tree(token_string)
        print("DPDA Execution Trace:")
        for step in trace:
            print(f"  {step}")
        
        if parse_tree:
            analyzer = ScopeAnalyzer(parse_tree, grammar)
            symbol_table = analyzer.analyze()
            
            visualizer = ParseTreeVisualizer(parse_tree, symbol_table)
            
            # visualizer.list_all_nodes()
            
            renamer = SymbolRenamer(parse_tree, symbol_table, lexer)
            
            while True:
                try:
                    choice = input("\nEnter 'v' for visualization, 'r' to rename symbol, 's' to save renamed code, node ID to select, or 'q' to quit: ").strip()
                    
                    if choice.lower() == 'q':
                        break
                    elif choice.lower() == 'v':
                        visualizer.visualize_tree(output_path=folder_address)
                    elif choice.lower() == 'r':
                        try:
                            node_id = int(input("Enter node ID to rename: "))
                            symbol_info = renamer.get_symbol_info(node_id)
                            
                            if symbol_info['type'] == 'not_symbol':
                                print(f"Node {node_id} is not a symbol (identifier/variable)")
                                continue
                            
                            print(f"Symbol info: {symbol_info}")
                            new_name = input(f"Enter new name for '{symbol_info['name']}': ").strip()
                            
                            if new_name:
                                renamed_code = renamer.rename_symbol(node_id, new_name)
                                print("\n=== Renamed Code ===")
                                print(renamed_code)
                                print("=" * 25)
                                
                                save_choice = input("Save to file? (y/n): ").strip().lower()
                                if save_choice == 'y':
                                    filename = input("Enter filename (e.g., 'renamed_code.txt'): ").strip()
                                    if filename:
                                        renamer.save_renamed_code_to_file(node_id, new_name, filename, prefix_address=folder_address)
                            else:
                                print("Invalid name entered.")
                                
                        except ValueError as e:
                            print(f"Error: {e}")
                        except Exception as e:
                            print(f"Unexpected error: {e}")
                
                    elif choice.lower() == 's':
                        try:
                            node_id = int(input("Enter node ID to rename: "))
                            symbol_info = renamer.get_symbol_info(node_id)
                            
                            if symbol_info['type'] == 'not_symbol':
                                print(f"Node {node_id} is not a symbol (identifier/variable)")
                                continue
                            
                            print(f"Symbol info: {symbol_info}")
                            new_name = input(f"Enter new name for '{symbol_info['name']}': ").strip()
                            filename = input("Enter output filename: ").strip()
                            
                            if new_name and filename:
                                renamer.save_renamed_code_to_file(node_id, new_name, filename, prefix_address=folder_address)
                            else:
                                print("Invalid input.")
                                
                        except ValueError as e:
                            print(f"Error: {e}")
                        except Exception as e:
                            print(f"Unexpected error: {e}")
                            
                    elif choice.isdigit():
                        node_id = int(choice)
                        if not visualizer.select_node_by_id(node_id):
                            print(f"Node with ID {node_id} not found.")
                    else:
                        print("Invalid input. Enter 'v' for visualization, 'r' for renaming, 's' to save, node ID to select, or 'q' to quit.")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")
        else:
            print("No parse tree generated (parsing failed).")
        
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
