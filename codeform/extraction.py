from codeform.treesitter.analysis import build_library, analyze
from codeform.treesitter.deptree import DependencyTree, flatten
from kevinlulee import join_text

def extract_symbol(node: Node, target: str):
    lib = build_library(node)

    def getter(node):
        m = analyze(node)
        return m["missing"]

    deptree = DependencyTree(lib, getter)
    tree = deptree.recursively_get_dependencies(target)
    nodes = flatten(tree)
    return join_text(nodes)
