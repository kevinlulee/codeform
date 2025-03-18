import json
import functools
import inspect
import pprint
from codeform.treesitter.nodes import get_root_node
from tree_sitter import Node

# YAML configuration as a Python dictionary.


CONFIG = {
    "module": {"fields": ["body"], "children": "*"},  # "*" means collect all children
    "decorated_definition": {
        "fields": [],
        "children": ["function_definition", "class_definition", "decorator"],
    },
    "function_definition": {
        "fields": ["async", "identifier", "type"],
        "children": ["parameters", "block"],
    },
    "class_definition": {"fields": ["identifier", "bases"], "children": ["block"]},
    "block": {"fields": [], "children": "*"},  # collect all children
    "parameters": {
        "fields": [],
        "children": [
            "identifier",
            "typed_parameter",
            "typed_default_parameter",
            "list_splat",
            "dictionary_splat",
        ],
    },
    "if_statement": {
        "fields": ["if", "elif", "else"],
        "children": ["condition", "consequence", "alternative"],
    },
    "while_statement": {"fields": ["while"], "children": ["condition", "block"]},
    "for_statement": {
        "fields": ["for", "in"],
        "children": ["identifier", "iterable", "block"],
    },
    "try_statement": {
        "fields": ["try"],
        "children": ["block", "except_clause", "else_clause", "finally_clause"],
    },
    "with_statement": {
        "fields": ["with"],
        "children": ["with_clause", "block"],  # using with_clause instead of with_items
    },
    "import_statement": {
        "fields": ["import"],
        "children": ["dotted_name", "alias", "import_list"],
    },
    "import_from_statement": {
        "fields": ["from", "import"],
        "children": ["module_name", "import_list"],
    },
    "assignment": {"fields": ["identifier"], "children": ["expression"]},
    "binary_operator": {
        "fields": ["operator"],
        "children": ["expression", "expression"],
    },
    "call": {"fields": ["identifier"], "children": ["argument_list"]},
    "argument_list": {"fields": [], "children": ["argument", "named_argument"]},
    "list": {
        "fields": [],
        "children": ["expression"],  # using "expression" to denote any expression node
    },
    "tuple": {
        "fields": [],
        "children": ["expression"],  # using "expression" to denote any expression node
    },
    "dictionary": {
        "fields": [],
        "children": ["pair"],  # using "pair" instead of "pairs"
    },
    "set": {
        "fields": [],
        "children": ["expression"],  # using "expression" to denote any expression node
    },
}


class Element:
    def __init__(self, node):
        self.type = node.type
        # Collect text for leaf nodes.
        self.text = node.text.decode("utf-8") if len(node.children) == 0 else ""
        self.fields = {}  # Holds field values as defined in CONFIG.
        self.children = []  # Holds child Elements.

    def to_json(self):
        """Serialize this element and its subtree to a JSON-compatible dict,
        including only truthy fields and non-empty children."""
        result = {"type": self.type}
        if self.text:
            result["text"] = self.text
        if self.fields:
                result["fields"] = self.fields
        if self.children:
            result["children"] = [child.to_json() for child in self.children]
        return result

    def to_json_string(self):
        return json.dumps(self.to_json(), indent=2)


def build_element_tree(node: Node):
    """
    Recursively builds an Element tree from a treesitter node using CONFIG.

    For each child in node.children:
      - If the child's type is in the current node's config "fields", assign its decoded text
        to the element's fields.
      - If the current node's config "children" is "*" then build an Element from the child and add it.
      - Else if the child's type is in the current node's config "children", build an Element from it and add it.
    """
    element = Element(node)
    config = CONFIG.get(node.type, {"fields": [], "children": "*"})
    expressions = ["integer", "string", "identifier", "call", "binary_operator"]

    def build_and_append(child):
        child_element = build_element_tree(child)
        element.children.append(child_element)

    for i, child in enumerate(node.children):
        text = child.text.decode("utf-8")
        field_name = node.field_name_for_child(i)
        if child.type in config["fields"]:
            element.fields[child.type] = text
        elif config["children"] == "*":
            if child.type == text:
                continue
            build_and_append(child)
        elif child.type in config["children"]:
            build_and_append(child)
        elif "expression" in config["children"] and child.type in expressions:
            build_and_append(child)
        elif child.type == text and len(text) <= 2:
            pass
        elif child.type == 'comment':
            build_and_append(child)
        else:
            # child_element = build_element_tree(child)
            # element.children.append(child_element)
            print('skipped', child.type, text)
            # Otherwise, ignore the child.
            pass  # Explicitly skipping as indicated in original code.
    return element


# Example usage:
def bar(a):
    return a


@bar
@bar
@bar
def foo() -> str:
    # with abc as foskjdfh:
    # pass
    # a = [1]
    # a = {'a': 1}
    a = b + boo()
    '''aaa'''
    foo()


source = inspect.getsource(foo)
ts_tree = get_root_node(source, "python")
root_element = build_element_tree(ts_tree)
print(root_element.to_json_string())
