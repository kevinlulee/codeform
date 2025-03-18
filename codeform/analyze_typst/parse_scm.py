import re

def parse_scm(text):
    """
    Parses test cases from the given text.
    
    Expected structure per test case:
    
      <header delimiter>           (a line of one or more '=' characters)
      <desc block>                 (one or more lines; may be multi-line)
      <header delimiter>           (a line of '=' characters)
      <input block>                (one or more lines; may be multi-line)
      <dashed delimiter>           (a line of one or more '-' characters)
      <output block>               (all remaining lines until the next header delimiter or EOF)
    
    Returns a list of dictionaries with keys: 'desc', 'input', 'output'.
    """
    lines = text.splitlines()
    i = 0
    tests = []
    
    while i < len(lines):
        # Skip any blank lines.
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        if i >= len(lines):
            break

        # Expect a header delimiter (line of '=' characters).
        if not re.match(r"^=+$", lines[i].strip()):
            raise ValueError(f"Expected header delimiter at line {i+1}")
        i += 1

        # Gather the description block until the next header delimiter.
        desc_lines = []
        while i < len(lines) and not re.match(r"^=+$", lines[i].strip()):
            desc_lines.append(lines[i])
            i += 1
        desc = "\n".join(desc_lines).strip()

        # Expect the second header delimiter.
        if i < len(lines) and re.match(r"^=+$", lines[i].strip()):
            i += 1
        else:
            raise ValueError(f"Expected second header delimiter at line {i+1}")

        # Gather the input block until we reach the dashed delimiter.
        input_lines = []
        while i < len(lines) and not re.match(r"^-+$", lines[i].strip()):
            input_lines.append(lines[i])
            i += 1
        test_input = "\n".join(input_lines).strip()

        # Expect a dashed delimiter.
        if i < len(lines) and re.match(r"^-+$", lines[i].strip()):
            i += 1
        else:
            raise ValueError(f"Expected dashed delimiter at line {i+1}")

        # Skip blank lines after the dashed delimiter.
        while i < len(lines) and lines[i].strip() == "":
            i += 1

        # Gather the output block until the next header delimiter or end-of-file.
        output_lines = []
        while i < len(lines) and not re.match(r"^=+$", lines[i].strip()):
            output_lines.append(lines[i])
            i += 1
        test_output = "\n".join(output_lines).strip()

        tests.append({
            "desc": desc,
            "input": test_input,
            "output": test_output
        })
    
    return tests

# Example usage:
if __name__ == "__main__":
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

    parsed_tests = parse_scm(sample_input)
    for test in parsed_tests:
        print("Description:")
        print(test["desc"])
        print("Input:")
        print(test["input"])
        print("Output:")
        print(test["output"])
        print("-" * 40)

