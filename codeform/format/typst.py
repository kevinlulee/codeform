from codeform.format.base import AbstractArgumentFormatter, surround
import re


class TypstArgumentFormatter(AbstractArgumentFormatter):
    filetype = "typst"

    ignored_strings = {
        "true",
        "false",
        "none",
        "auto",  # Common keywords
        "left",
        "right",
        "center",
        "top",
        "bottom",  # Alignment keywords
        "black",
        "white",
        "red",
        "green",
        "blue",
        "yellow",
        "cyan",
        "magenta",  # Basic colors
    }
    variable_definition_template = "let %s = %s"
    indentation = 2
    string_ignore_pattern = re.compile(
        r"^[0-9]+(\.[0-9]+)?(pt|mm|cm|in|em|ex|fr|px|%)?$"
    )  # Numbers and units
    null = "none"
    true = "true"
    false = "false"
    undefined = "none"

    dictionary_kv_delimiter = ": "
    dictionary_kv_argument_delimiter = ": "
    needs_dictionary_quotes = False

    object_delimiters = "()"
    array_delimiters = "()"

    declaration_template = "let %s = %s"
    function_template = "let %s = {\n\t%s\n}"
    block_template = "%s %s {\n\t%s\n}"

    def call(self, name, args, kwargs, block=False):
        args = self.format_args(args)
        kwargs = self.format_kwargs(kwargs)
        base = kwargs + args

        comma = "" if block else ","
        items = (comma + "\n").join(base) + comma
        delim = "({})" if block else "()"
        if len(items) < 30:
            return name + f"({items})"
        return name + surround(items, delim)

    def parse_string(self, s):
        newlines = "\n" in s

        # do it smarter kevin.
        # not the hacky way
        def fix(s):
            if newlines:

                def replacer(x):
                    key = x.group(0)
                    return "\n" + "\\\n" * len(key)

                s = re.sub("\n+", replacer, s)
                return surround(s, "[]", indent=self.indentation, newlines=newlines)
            return f'"{s}"'

        return fix(s)


typst = TypstArgumentFormatter()
print(typst.call("hi", [{"a": "aa"}], {}))
# this will also make objects look like typst content blocks ... which is wrong.
