from pprint import pprint
from codeform.analyze_typst.parse_scm import parse_scm
from codeform.treesitter.nodes import get_syntax_tree, get_language
from kevinlulee import get_most_recent_file, clip, readfile

dldir = "~/downloads/"

from codeform.analyze_typst.view_parent_child_relationships import (
    view_parent_child_relationships,
)

sample_input = r"""
=====================
positive/000
=====================
a b
---------------------

(source_file
	(text))

=====================
positive/001
=====================
a b#a b
---------------------

(source_file
	(text)
	(code
		(ident))
	(text))

=====================
positive/002
=====================
#if b {} else {}
---------------------

(source_file
	(code
		(branch
			condition: (ident)
			(block)
			(block))))
    """.strip()


def build(o):
    filetype = "typst"
    data = parse_scm(readfile(get_most_recent_file(dldir)))
    data = [el["input"] for el in data]
    relationships = view_parent_child_relationships(data, filetype)
    clip(prepare_for_json(relationships))


def prepare_for_json(o):
    return {
        node_type: {"fields": list(info["fields"]), "children": list(info["children"])}
        for node_type, info in o.items()
    }





def yoba(filetype='typst'):
    
    language = get_language(filetype)
    # data = parse_scm(readfile(get_most_recent_file(dldir)))
    # data = [el["input"] for el in data]

    def callback(s):
        tree = get_syntax_tree(s, filetype)

        query = """
            (code
              (return) @return)
        """
        print(tree.root_node)
        query = '''(source_file(code (let (call)))@return)'''
        query='(group (tagged)) @return'
        query='(group (tagged (_) @a (_) @b)) @return'
        # query = '''(tagged)@return)'''
        # multiple captures
        query_object = language.query(query) 
        # captures = query_object.captures(tree.root_node)
        captures = query_object.matches(tree.root_node)
        pprint(captures)
        return

        # print(return_nodes)
        for name, nodes in captures.items():
            for node in nodes:
                print([node, node.text.decode()])
            # print(a, b)
                # print("sexpr", node)
                # print("text", node.text)

    s = 'a\nb\nc#{[hiiiiii]}\nd'
    s = '#let a()= box()\n\n#let a()= box()'
    s = '#let a = (asd: (asd: 1))'
    s = '#let a = foobar(vv: hi, asd: (asd: 1))'
    callback(s)
    # callback(data[0])
    # results = [callback(s) for s in data]

yoba()
