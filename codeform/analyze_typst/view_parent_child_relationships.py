from tree_sitter import Node
def collect_tree_nodetypes(node):
    """
    Recursively collects node types from a Tree-sitter tree, 

    For each node, we record:
      - "fields": immediate child node types where child.text == child.type.
      - "children": immediate child node types where child.text != child.type.

    Delimiter nodes (e.g. "[", "]", "{", "}", ",", ".") are skipped.
    
    The final result is a dict mapping each node type to its info:
      {
        node_type: {
          "fields": [unique field types],
          "children": [unique child types]
        },
        ...
      }
    """
    delimiters = {'#', "[", "]", "{", "}", ",", ".", '(', ')', '=', '=>', ':', ';'}
    global_store = {}  # Maps node type to {"fields": set(), "children": set()}
    no_duplicates = False

    def process_node(node: Node):
        if node.type in delimiters:
            return

        children = node.children
        if not children:
            return

        if node.type not in global_store:
            global_store[node.type] = {"fields": set(), "children": set()}
        
        for i, child in enumerate(children):
            if child.type in delimiters:
                continue
            
            text = child.text.decode()
            field_name = node.field_name_for_child(i)

            if text == child.type:
                global_store[node.type]["fields"].add(child.type)

            elif field_name:
                global_store[node.type]["fields"].add(child.type)

            else:
                global_store[node.type]["children"].add(child.type)
            
            process_node(child)

    process_node(node)
    return global_store

import pprint
from codeform.treesitter.nodes import get_root_node

a = '#if b {} else {}'

b = '#call(sdf)'



def view_parent_child_relationships(items, filetype):

    def merge_dicts(dicts):
      merged = {}
      for d in dicts:
        for key, value in d.items():
          if key not in merged:
            merged[key] = {subkey: set(subval) for subkey, subval in value.items()}
          else:
            for subkey, subval in value.items():
              merged[key][subkey].update(subval)
      return merged

    def callback(x):
        return collect_tree_nodetypes(get_root_node(x, filetype))
    dicts = [callback(el) for el in items]

    result = merge_dicts(dicts)
    return result

if __name__ == '__main__':
    print(view_parent_child_relationships([b], 'typst'))
