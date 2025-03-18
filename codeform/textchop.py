from codeform.treesitter.nodes import get_root_node, Node
from kevinlulee import join_text

def textchop(text, filetype='python'):
    """
    chops away unnecessary text for a shorter agent query.
    """

    def should_remove_node(node: Node) -> bool:
        # top level strings and integers should never exist
        # a smarter enter
        ignore={"comment", 'string', 'integer', 'call', 'import_statement', 'import_from_statement'}
        if node.type in ignore:
            return True
        if node.type == "expression_statement":
                child = node.named_child(0)
                if child.type in ignore:
                    return True
                if child.type == "assignment":
                    grandchild=child.named_child(1)
                    if grandchild.type in ignore:
                        return True
        return False

    # Get the root node and its children
    root_node = get_root_node(text, filetype)
    new_children = [child.text.decode() for child in root_node.children if not should_remove_node(child)]
    return join_text(new_children)

