# ll1-parser-and-dpda-toolkit
A comprehensive toolkit for LL(1) parser construction and deterministic pushdown automaton (DPDA) conversion. Features grammar analysis, parse table generation, lexical analysis, parse tree visualization, and symbol table management for compiler construction and formal language processing.

## Features

- **Grammar Parsing:** Reads and processes context-free grammars from a file.
- **LL(1) Parse Table:** Constructs FIRST and FOLLOW sets, and generates the LL(1) parse table.
- **DPDA Conversion:** Converts the LL(1) parser into a DPDA for input processing.
- **Lexer:** Tokenizes input code based on grammar-defined regular expressions.
- **Parse Tree Construction:** Builds a parse tree during parsing.
- **Scope Analysis:** Analyzes variable/function scopes and builds a symbol table.
- **Parse Tree Visualization:** Visualizes the parse tree using Graphviz.
- **Symbol Renaming:** Supports safe renaming of identifiers throughout the code.
- **Interactive CLI:** Allows users to visualize, select, and rename symbols interactively.

## Project Structure

```
Project/
├── classes/
│   ├── dpda.py
│   ├── grammar.py
│   ├── lexer.py
│   ├── ll1_parser.py
│   ├── ll1_to_dpda.py
│   ├── parse_tree_visualizer.py
│   ├── scope_analyzer.py
│   ├── symbole_renamer.py
│   └── symbole_table.py
├── grammar1.txt
├── code1.txt
├── main.py
└── README.md
```

- `main.py`: Entry point for running the tool.
- `grammar1.txt`: Example grammar definition.
- `code1.txt`: Example source code to parse and analyze.
- `classes/`: Contains all core modules for parsing, analysis, and transformation.

## Getting Started

### Prerequisites

- Python 3.7+
- [Graphviz](https://graphviz.gitlab.io/download/) (for parse tree visualization)
- Python packages: `graphviz`

### Usage

1. **Prepare Grammar and Code:**
   - Edit `grammar1.txt` to define your grammar.
   - Place your source code in `code1.txt`.

2. **Run the Main Program:**
   ```bash
   python main.py
   ```

3. **Interactive CLI:**
   - After parsing, use the CLI to:
     - Visualize the parse tree (`v`)
     - Rename a symbol (`r`)
     - Save renamed code (`s`)
     - Select a node by ID
     - Quit (`q`)

4. **Parse Tree Visualization:**
   - Visualizations are saved as PNG files in the project directory.

## Example

```
function main ( ) {
    x = 42 ;
    y = 3.14 ;
    z = ( x + y ) * 2 ;
    if ( z ) {
        result = z / 1.5 ;
        x = y ;
    }
    while ( x ) {
        x = x - 1 ;
    }
    return result ;
}
```

## Grammar Format

The grammar file should follow this format:
- Productions separated by newlines
- Use `->` to separate left and right sides
- Use `|` for alternatives
- Terminal symbols should be quoted or defined as regex patterns

## Output Files

- `parse_tree_<timestamp>.png`: Generated parse tree visualizations
- Modified source code files (when using rename functionality)
- Parse tables and analysis results (printed to console)

## Customization

- **Grammar:** Modify `grammar1.txt` to support your language.
- **Lexical Rules:** Adjust regex patterns in the grammar file.
- **Input Code:** Place your code in `code1.txt` or specify another file in `main.py`.

---

*Developed for TLA course assignments.*
