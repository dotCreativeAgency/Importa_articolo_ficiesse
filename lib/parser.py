"""SQL tuple parser utilities extracted from import_articoli_to_sqlite.py

Provides:
- parse_sql_value(value_str)
- extract_tuple_values(content, start_pos)

Designed to be small and easily testable.
"""
import re


def parse_sql_value(value_str):
    """Converts a SQL literal into a Python value.

    - NULL -> None
    - numeric -> int or float
    - quoted strings: unescape common escapes
    """
    if value_str is None:
        return None
    s = value_str.strip()

    # NULL
    if s.upper() == 'NULL':
        return None

    # Quoted string
    if s.startswith("'") and s.endswith("'") and len(s) >= 2:
        val = s[1:-1]
        # Handle SQL escapes: \' -> ', \" -> ", \\ -> \
        val = val.replace("\\'", "'")
        val = val.replace('\\"', '"')
        val = val.replace('\\\\', '\\')
        return val

    # Numeric
    # Try integer then float
    try:
        if re.match(r'^-?\d+$', s):
            return int(s)
        if re.match(r'^-?\d+\.\d+$', s):
            return float(s)
    except Exception:
        pass

    # Fallback: return raw string
    return s


def extract_tuple_values(content, start_pos):
    """Extract a tuple starting at or after start_pos in content.

    Returns (values_list, next_pos) or (None, start_pos) if no tuple found.
    """
    i = start_pos
    l = len(content)

    # Find the opening parenthesis
    while i < l and content[i] != '(':
        i += 1

    if i >= l:
        return None, start_pos

    i += 1  # skip '('

    values = []
    current = ''
    in_quotes = False
    escape = False
    paren_level = 0

    while i < l:
        ch = content[i]

        if escape:
            current += ch
            escape = False
            i += 1
            continue

        if ch == '\\':
            escape = True
            # don't add backslash itself; next char will be added in escape path
            i += 1
            continue

        if ch == "'":
            in_quotes = not in_quotes
            current += ch
            i += 1
            continue

        if in_quotes:
            current += ch
            i += 1
            continue

        if ch == '(':
            paren_level += 1
            current += ch
            i += 1
            continue

        if ch == ')':
            if paren_level > 0:
                paren_level -= 1
                current += ch
                i += 1
                continue
            # end of tuple
            if current.strip() != '':
                values.append(parse_sql_value(current.strip()))
            return values, i + 1

        if ch == ',':
            # value separator
            values.append(parse_sql_value(current.strip()))
            current = ''
            i += 1
            continue

        # default char
        current += ch
        i += 1

    return None, start_pos
