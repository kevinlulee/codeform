import re
import textwrap


REAL = "__REAL__"


def surround(
    text: str, bracket_type: str = "()", indent: int = 4, newlines: bool = True
) -> str:
    brackets = {
        "()": ("(", ")"),
        "[]": ("[", "]"),
        "[[]]": ("[[", "]]"),
        "{}": ("{", "}"),
        '"': ('"', '"'),
        "'": ("'", "'"),
        "'''": ("'''", "'''"),
        '"""': ('"""', '"""'),
        "``": ("`", "`"),
        "```": ("```", "```"),
        "({})": ("({", "})"),
        "([])": ("([", "])"),
    }

    open_bracket, close_bracket = brackets[bracket_type]

    if newlines:
        indentation = " " * indent
        indented_text = textwrap.indent(text, indentation)
        return f"{open_bracket}\n{indented_text}\n{close_bracket}"
    else:
        return f"{open_bracket}{text}{close_bracket}"


def real(x, recursive=False):
    """
    Converts various data types to their string representations.

    Args:
        x: The input value to convert.
        recursive: If True, recursively processes arrays and objects.
        REAL: A prefix string to add to certain string representations.

    Returns:
        The string representation of the input value.
    """

    if isinstance(x, str):
        if x.startswith("!"):
            return x[1:]
        if x.startswith("str:"):
            return x[4:]
        return REAL + x

    if isinstance(x, (int, float)):
        return str(x)

    if callable(x):
        return REAL + x.__name__

    if recursive:
        if isinstance(x, list):
            return [real(item, recursive=True) for item in x]
        if isinstance(x, dict):
            return {k: real(v, recursive=True) for k, v in x.items()}
    else:
        return x


class AbstractArgumentFormatter:
    depth_limit = 2
    dictionary_kv_delimiter = ": "
    dictionary_kv_argument_delimiter = "="
    object_delimiters = "{}"
    array_delimiters = "[]"
    null = "null"
    true = "true"
    false = "false"
    undefined = "undefined"

    def __init__(self, indentation=4, max_length=60):
        self.indentation = indentation
        self.max_length = max_length

    def format_args(self, args, opts = {}):
        return [self.format(arg, opts) for arg in args]

    def format_kwargs(self, kwargs, opts = {}):
        multiline = opts.get("multiline", False)
        formatted_kwargs = []
        for k, v in kwargs.items():
            if v == None:
                continue
            formatted_value = self.format(v, opts)
            formatted_kwargs.append(
                self.format_key_value_pair(k, formatted_value, as_argument=True)
            )
        return formatted_kwargs

    def call(self, name, args=None, kwargs=None, **opts):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        args = self.format_args(args, opts)
        kwargs = self.format_kwargs(kwargs, opts)

        items = args + kwargs
        multiline = len(args) > 3 or len(kwargs) > 2 or len(items) > 3

        if multiline:
            return name + surround(items, "()")
        else:
            return f"{name}({', '.join(items)})"

    def _meets_maximum_length(self, value, depth, opts):
        if opts.get("long", False):
            return False
        if depth >= self.depth_limit:
            return False
        if "\n" in value:
            return False
        length = len(value) + depth * self.indentation
        return length < self.max_length

    def format(self, s, opts = {}):
        return self._parse(s, depth=0, opts=opts)

    def _parse(self, s, depth=0, opts={}):
        if depth > self.depth_limit:
            return "..."  # Prevents infinite recursion

        if s is None:
            return self.null
        if s is True:
            return self.true
        if s is False:
            return self.false
        if isinstance(s, (int, float)):
            return str(s)
        if isinstance(s, dict):
            return self.parse_object(s, depth, opts)
        if isinstance(s, list):
            return self.parse_array(s, depth, opts)
        if isinstance(s, str):

            if s == "undefined":
                return self.undefined
            if s in getattr(self, "ignored_strings", []) or (
                hasattr(self, "string_ignore_pattern")
                and re.search(self.string_ignore_pattern, s)
            ):
                return s
            if s in ("''", '""'):
                return '""'
            if s.startswith(REAL): return s.replace(REAL, '')
            return self.parse_string(s)
        return str(s)

    def parse_object(self, obj, depth, opts):
        computed = [(k, self._parse(v, depth + 1, opts=opts)) for k, v in obj.items()]
        return self.format_object(computed, depth)

    def parse_array(self, arr, depth, opts):
        computed = [self._parse(x, depth + 1, opts=opts) for x in arr]
        return self.format_array(computed, depth)

    def parse_string(self, s):
        return f'"{s}"'

    def format_object(self, items, depth):
        return self.format_collection(items, depth, dict)

    def format_array(self, items, depth):
        return self.format_collection(items, depth, list)

    def format_collection(self, items, depth, mode):
        """
        Formats a list or dictionary for output, using the appropriate delimiters.
        """
        collection_delimiter = (
            self.object_delimiters if mode == dict else self.array_delimiters
        )
        if not items:
            return collection_delimiter
        if mode == dict:
            computed = [self.format_key_value_pair(k, v) for k, v in items]
        else:
            computed = items

        sample = surround(", ".join(computed), collection_delimiter, newlines=False)
        if len(items) < 4 and self._meets_maximum_length(sample, depth, {}):
            return sample
        return surround(computed, collection_delimiter, multiline=True)

    def format_key_value_pair(self, key, value, as_argument=False):
        """
        Formats a key-value pair for dictionary output or function arguments.
        """
        dictionary_kv_delimiter = (
            self.dictionary_kv_argument_delimiter
            if as_argument
            else self.dictionary_kv_delimiter
        )
        return f"{key}{dictionary_kv_delimiter}{value}"

    def function_definition(self, name, args, kwargs):
        argstr = ''
        return self.function_definition_template % (name, argstr)

    def variable_definition(self, name, value):
        return self.variable_definition_template % (name, self.format(value))


