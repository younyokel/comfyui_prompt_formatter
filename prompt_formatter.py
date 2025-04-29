import re
import unicodedata

from .config import BRACKET2WEIGHT, CONV_SPACE_UNDERSCORE, BLACKLISTED_TAGS

# Bracket handling
brackets_opening = set("([{")
brackets_closing = set(")]}")
bracket_pairs = dict(zip("([{", ")]}"))
bracket_pairs_reverse = dict(zip(")]}", "([{"))
bracket_pattern = r'(?<!\\)(?:\([^)]*\)|\[[^\]]*\])(?=(?:\s*(?:,|BREAK|<[^>]+>)|\s*$))'

# Regular expression patterns
re_break = re.compile(r"\s*BREAK\s*")
re_angle_bracket = re.compile(r"<[^>]+>")
re_brackets = re.compile(r'([([{<])|([)\]}>])')
re_brackets_open = re.compile(r"(?<!\\)(\(+|\[+)")

"""
Functions
"""

def get_bracket_opening(c: str):
    return bracket_pairs_reverse.get(c, '')

def normalize_characters(data: str):
    return unicodedata.normalize("NFKC", data)

def remove_whitespace_excessive(prompt: str):
    lines = prompt.split("\n")
    cleaned_lines = [" ".join(line.split()).strip() for line in lines if line.strip()]
    return "\n".join(cleaned_lines)

def align_brackets(prompt: str):
    return re_brackets.sub(lambda m: m.group(1) or m.group(2), prompt)

def space_and(prompt: str):
    def helper(match: re.Match):
        return " ".join(match.groups())

    return re.sub(r"(.*?)\s*(AND)\s*(.*?)", helper, prompt)

def align_commas(prompt: str):
    split = [s.strip() for s in prompt.split(',') if s.strip()]
    return ", ".join(split)

def remove_mismatched_brackets(prompt: str):
    stack = []
    pos = []
    result = []

    for i, c in enumerate(prompt):
        if c in brackets_opening:
            stack.append(c)
            pos.append(len(result))
            result.append(c)
        elif c in brackets_closing:
            if stack and stack[-1] == get_bracket_opening(c):
                stack.pop()
                pos.pop()
                result.append(c)
        else:
            result.append(c)

    for p in reversed(pos):
        result.pop(p)

    return "".join(result)

def space_brackets(prompt: str):
    def helper(match: re.Match):
        return " ".join(match.groups())

    parts = re.split(r'(<[^>]+>)', prompt)
    for i in range(len(parts)):
        if not parts[i].startswith('<'):
            parts[i] = re.sub(r"([)\]}>])([([{<])", helper, parts[i])

    return ''.join(parts)

def align_alternating(prompt: str):
    return re.sub(r"\s*(\|)\s*", lambda match: match.group(1), prompt)

def bracket_to_weights(prompt: str):
    if not BRACKET2WEIGHT:
        return prompt
    
    # Identify regions enclosed within angle brackets
    excluded_regions = []
    for match in re_angle_bracket.finditer(prompt):
        excluded_regions.append((match.start(), match.end()))

    # Split the prompt into sections that are not within angle brackets
    segments = []
    previous_position = 0
    for start, end in excluded_regions:
        segments.append(prompt[previous_position:start])
        previous_position = end
    segments.append(prompt[previous_position:])

    # Process each segment separately
    updated_segments = []
    for segment in segments:
        depths, gradients, brackets = get_mappings(segment)
        pos = 0
        ret = segment

        while pos < len(ret):
            if ret[pos] in brackets_opening:
                open_bracketing = re_brackets_open.match(ret, pos)
                if open_bracketing:
                    consecutive = len(open_bracketing.group(0))
                    gradient_search = "".join(
                        map(
                            str,
                            reversed(
                                range(
                                    int(depths[pos]) - 1,
                                    int(depths[pos]) + consecutive
                                ),
                            )
                        )
                    )
                    is_square_brackets = "[" in open_bracketing.group(0)

                    insert_at, weight, valid_consecutive = get_weight(
                        ret,
                        gradients,
                        depths,
                        brackets,
                        open_bracketing.end(),
                        consecutive,
                        gradient_search,
                        is_square_brackets,
                    )

                    if weight:
                        # If weight already exists, ignore
                        current_weight = re.search(
                            r"(?<=:)(\d+.?\d*|\d*.?\d+)(?=[)\]]$)",
                            ret[:insert_at + 1]
                        )
                        if current_weight:
                            ret = (
                                ret[:open_bracketing.start()]
                                + "("
                                + ret[
                                    open_bracketing.start() + valid_consecutive : insert_at
                                ]
                                + ")"
                                + ret[insert_at + consecutive :]
                            )
                        else:
                            ret = (
                                ret[:open_bracketing.start()]
                                + "("
                                + ret[
                                    open_bracketing.start() + valid_consecutive : insert_at
                                ]
                                + f":{weight:.2f}".rstrip("0").rstrip(".")
                                + ")"
                                + ret[insert_at + consecutive :]
                            )

                    depths, gradients, brackets = get_mappings(ret)
                    pos += 1

            match = re.search(r"(?<!\\)[([]", ret[pos:])

            if not match:  # no more potential weight brackets to parse
                break

            pos += match.start()
        updated_segments.append(ret)

    # Reassemble the final prompt with the excluded regions
    final_prompt = ""
    for i, segment in enumerate(updated_segments):
        final_prompt += segment
        if i < len(excluded_regions):
            final_prompt += prompt[excluded_regions[i][0]:excluded_regions[i][1]]

    # Remove round brackets with weight 1
    final_prompt = re.sub(r'(?<!\\)\(([^:]+):1(?:\.0*)?\)', r'\1', final_prompt)

    return final_prompt

def depth_and_gradient(s: str):
    depth = 0
    depth_map = []
    gradient = []
    for c in s:
        if c in brackets_opening:
            depth += 1
            gradient.append('^')
        elif c in brackets_closing:
            depth -= 1
            gradient.append('v')
        else:
            gradient.append('-')
        depth_map.append(str(depth))
    return ''.join(depth_map), ''.join(gradient)

def get_mappings(s: str):
    depth_map, gradient = depth_and_gradient(s)
    brackets = ''.join(c if c in "[]()<>" else " " for c in s)
    return depth_map, gradient, brackets

def calculate_weight(d: str, is_square_brackets: bool):
    return 1 / 1.1 ** int(d) if is_square_brackets else 1 * 1.1 ** int(d)

def get_weight(
    prompt: str,
    map_gradient: list,
    map_depth: list,
    map_brackets: list,
    pos: int,
    ctv: int,
    gradient_search: str,
    is_square_brackets: bool = False,
):
    """Returns 0 if bracket was recognized as prompt editing, alternation, or composable."""
    # CURRENTLY DOES NOT TAKE INTO ACCOUNT COMPOSABLE?? DO WE EVEN NEED TO?
    # E.G. [a AND B :1.2] == (a AND B:1.1) != (a AND B:1.1) ????
    while pos + ctv <= len(prompt):
        if ctv == 0:
            return prompt, 0, 1
        a, b = pos, pos + ctv
        if prompt[a] in ":|" and is_square_brackets:
            if map_depth[-2] == map_depth[a]:
                return prompt, 0, 1
            if map_depth[a] in gradient_search:
                gradient_search = gradient_search.replace(map_depth[a], "")
                ctv -= 1
        elif map_gradient[a:b] == "v" * ctv and map_depth[a - 1 : b] == gradient_search:
            return a, calculate_weight(ctv, is_square_brackets), ctv
        elif "v" == map_gradient[a] and map_depth[a - 1 : b - 1] in gradient_search:
            narrowing = map_gradient[a:b].count("v")
            gradient_search = gradient_search[narrowing:]
            ctv -= 1
        pos += 1

    msg = f"Somehow weight index searching has gone outside of prompt length with prompt: {prompt}"
    raise Exception(msg)

def space_to_underscore(prompt: str):
    if CONV_SPACE_UNDERSCORE == "None":
        return prompt
    elif CONV_SPACE_UNDERSCORE == "Spaces to underscores":
        match = re.compile(r"(?<!BREAK) +(?!BREAK|[^<]*>)")
        replace = "_"
    elif CONV_SPACE_UNDERSCORE == "Underscores to spaces":
        match = re.compile(r"(?<!BREAK|_)_(?!_|BREAK|[^<]*>)")
        replace = " "

    tokens = [t.strip() for t in prompt.split(",")]
    tokens = [re.sub(match, replace, t) for t in tokens]

    return ",".join(tokens)

def dedupe_tokens(prompt: str):
    # Define separators and dedupe pattern
    separators = [',', re_break.pattern, r'<[^>]+>']
    dedupe_pattern = re.compile(f'({bracket_pattern}|(?:{"|".join(separators)}))')
    
    lines = prompt.splitlines()
    processed_lines = []
    seen = set()
    
    for line in lines:
        # If no separator is found, leave the line unchanged.
        if not re.search(f'(?:{"|".join(separators)})', line):
            processed_lines.append(line)
            continue
        
        # Split the line while preserving tokens.
        parts = [p for p in dedupe_pattern.split(line) if p is not None]
        result = []
        
        for part in parts:
            normalized = part.strip()
            if not normalized:
                continue

            # Check if this part is one of the separators.
            if any(re.fullmatch(sep, normalized) for sep in separators):
                if normalized == "BREAK":
                    result.append(" BREAK ")
                elif re.fullmatch(r'<[^>]+>', normalized):
                    result.append(f" {normalized} ")
                else:
                    result.append(f" {normalized} ")
            else:
                if normalized not in seen:
                    seen.add(normalized)
                    result.append(part)
        
        output = ''.join(result)
        output = re_break.sub(r' BREAK ', output).strip()
        processed_lines.append(' '.join(output.split()))
    
    return '\n'.join(processed_lines).strip()

def comma_before_bracket(prompt: str):
    return re.sub(r',\s*(<)', r' \1', prompt)

def format_prompt(prompt):
    # Clean up the string
    prompt = normalize_characters(prompt)
    prompt = remove_mismatched_brackets(prompt)

    # Remove duplicates
    prompt = dedupe_tokens(prompt)

    # Clean up whitespace for cool beans
    prompt = remove_whitespace_excessive(prompt)
    prompt = space_to_underscore(prompt)
    prompt = align_brackets(prompt)
    prompt = space_and(prompt) # for proper compositing alignment on colons
    prompt = space_brackets(prompt)
    prompt = align_commas(prompt)
    prompt = align_alternating(prompt)
    prompt = bracket_to_weights(prompt)
    prompt = comma_before_bracket(prompt)

    return prompt

def convert_tags(prompt):
    remove_parens = str.maketrans({"(": "", ")": ""})
    output_lines = []

    for line in prompt.splitlines(keepends=True):
        # Skip special cases
        if not line.strip() or "BREAK" in line or "," in line or (("(" in line or ")" in line) and "_" not in line):
            output_lines.append(line)
            continue

        # Process tags
        raw_tags = line.strip().split()
        filtered_tags = [
            tag for tag in raw_tags
            if not any(pat.fullmatch(tag.translate(remove_parens)) for pat in BLACKLISTED_TAGS)
        ]

        # Format tags: replace underscores & escape parentheses
        formatted_tags = [
            tag.replace("_", " ")
                .replace("\\(", "(")
                .replace("\\)", ")")
                .replace("(", r"\(")
                .replace(")", r"\)")
            for tag in filtered_tags
        ]

        # Convert to final format
        result = ", ".join(formatted_tags)
        result += ","

        output_lines.append(result + ("\n" if line.endswith("\n") else ""))

    return "".join(output_lines)
