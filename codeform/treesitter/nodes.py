from tree_sitter import Language, Parser,  Node, Tree


def get_language(filetype: str) -> Language:
    """Returns the tree-sitter Language object for the given filetype."""
    match filetype:
        case "python":
            import tree_sitter_python
            return Language(tree_sitter_python.language())
        case "javascript":
            import tree_sitter_javascript
            return Language(tree_sitter_javascript.language())
        case "typst":
            import tree_sitter_typst
            return Language(tree_sitter_typst.language())
        case _:
            raise ValueError(f"Unsupported filetype: {filetype}")
def get_syntax_tree(text: str, filetype: str) -> Tree:
    """Parses source code into a tree-sitter tree.

    Args:
        text: The source code to parse as a string.
        filetype: The type of the file, e.g., "python"

    Returns:
        - "tree": The tree-sitter Tree object representing the parsed code.
    """

    language = get_language(filetype)
    parser = Parser()
    parser.language = language
    tree = parser.parse(bytes(text, "utf8"))
    return tree


def get_root_node(text: str, filetype: str):
    return get_syntax_tree(text, filetype).root_node


def get_identifier_node(node: Node) -> Node:
    ''' this is only for python '''
    if node.type == "expression_statement":
        node = node.named_child(0)
        if node.type == "assignment":
            return node.named_child(0)
    elif node.type in ["function_definition", "class_definition"]:
        return node.named_child(0)

