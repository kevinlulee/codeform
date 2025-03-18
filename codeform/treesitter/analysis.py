from .deptree import DependencyTree
from .nodes import get_root_node, get_identifier_node, Node
from .environment import Environment


def build_library(node):
    return {
        name.text: el
        for el in node.children
        if (name := get_identifier_node(node)) != None
    }


class Analyzer:
    declarators = {"import_statement", "import_from_statement", "function_definition", "class_definition"}

    def __init__(self):
        self.errors = []

    def visit(self, node, env):
        """Generic traversal for Tree-sitter nodes."""
        if hasattr(self, f"visit_{node.type}"):
            getattr(self, f"visit_{node.type}")(node, env)
        else:
            self.visit_each(node, env)

    def visit_each(self, node, env):
        """Visit all child nodes recursively."""
        for child in node.named_children:
            self.visit(child, env)

    def visit_identifier(self, node, env):
        """Handle identifier nodes."""
        if node.parent.type in self.declarators:
            env.add(node)
        elif not env.touch(node, silent=True):
            self.errors.append(node.parent.type)

    def visit_function_definition(self, node, env):
        """Handle function definitions and manage scope."""
        identifier, params, *_, body = node.named_children
        env.add(identifier)
        new_env = env.create_env()
        self.visit_parameters(params, env, new_env)
        self.visit(body, new_env)

    def visit_lambda(self, node, env):
        """Handle lambda expressions."""
        params, body = node.children
        new_env = env.create_env()
        self.visit_parameters(params, env, new_env)
        self.visit(body, new_env)

    def visit_import_statement(self, node, env):
        """Handle import statements."""
        child = node.child(1)
        env.add(child if child.is_leaf() or child.type == 'dotted_name' else child.child(2))

    def visit_assignment(self, node, env):
        """Handle variable assignments."""
        identifier, body = node.named_children
        env.add(identifier) if identifier.type in {"identifier", "pattern_list"} else self.visit(identifier, env)
        self.visit(body, env)

    def visit_parameters(self, node, env, new_env):
        """Process function parameters."""
        for child in node.named_children:
            if child.type == "identifier":
                new_env.add(child)
            elif child.type == "default_parameter":
                new_env.add(child.child(1))
                self.visit(child.child(2), env)


def analyze(node: Node):
    def runner(env):
        missing = set(env.missing)

        for child in env.children:
            child_missing = runner(child)
            missing.update(child_missing)

        return missing

    env = Environment()
    Analyzer().visit(node, env)

    unused = env.variables - env.touched
    missing = runner(env)

    return dict(unused = list(unused), missing = list(missing - set(python_builtins)))
