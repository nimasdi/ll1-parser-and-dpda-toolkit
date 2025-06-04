import re

class Lexer:
    def __init__(self, grammar):
        self.grammar = grammar
        self.compiled_patterns = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        for terminal, pattern in self.grammar.terminal_patterns.items():
            try:
                clean_pattern = pattern.replace(' ', '')
                self.compiled_patterns[terminal] = re.compile(clean_pattern)
            except re.error as e:
                print(f"Invalid regex pattern for {terminal}: {pattern} - {e}")
    
    def tokenize(self, input_string):
        tokens = []
        position = 0
        
        while position < len(input_string):

            if input_string[position].isspace():
                position += 1
                continue
            
            match_found = False
            longest_match = ""
            matched_terminal = None
            
            for terminal, compiled_pattern in self.compiled_patterns.items():
                match = compiled_pattern.match(input_string, position)
                if match:
                    matched_text = match.group(0)
                    # longest match logic
                    if len(matched_text) > len(longest_match):
                        longest_match = matched_text
                        matched_terminal = terminal
                        match_found = True
            
            if match_found:
                tokens.append((matched_terminal, longest_match))
                position += len(longest_match)
            else:
                tokens.append(('ERROR', input_string[position]))
                position += 1
        
        return tokens
    
    def get_terminal_types(self):
        return list(self.grammar.terminals)

