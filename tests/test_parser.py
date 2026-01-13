import pytest
from lib import parser


def test_parse_null():
    assert parser.parse_sql_value('NULL') is None
    assert parser.parse_sql_value(' NULL ') is None


def test_parse_int_and_float():
    assert parser.parse_sql_value('123') == 123
    assert parser.parse_sql_value('-5') == -5
    assert parser.parse_sql_value('12.34') == 12.34


def test_parse_string_simple_and_escapes():
    assert parser.parse_sql_value("'hello'") == 'hello'
    assert parser.parse_sql_value("'it\\'s ok'") == "it's ok"
    assert parser.parse_sql_value("'a\\\\b'") == "a\\b"
    assert parser.parse_sql_value("'quote\"here'") == 'quote"here'


def test_extract_simple_tuple():
    s = "(1,'hello',NULL)"
    vals, pos = parser.extract_tuple_values(s, 0)
    assert vals == [1, 'hello', None]


def test_extract_tuple_with_parentheses_in_string():
    s = "(2,'value (with) paren', 'ok')"
    vals, pos = parser.extract_tuple_values(s, 0)
    assert vals == [2, 'value (with) paren', 'ok']


def test_extract_tuple_with_commas_in_string():
    s = "(3,'a, b, c', 4)"
    vals, pos = parser.extract_tuple_values(s, 0)
    assert vals == [3, 'a, b, c', 4]


def test_extract_from_content_with_prefix():
    s = "INSERT INTO `t_articoli` VALUES (4,'x',5), (6,'y',7);"
    # Start searching after 'VALUES'
    idx = s.find('(')
    vals, pos = parser.extract_tuple_values(s, idx)
    assert vals == [4, 'x', 5]


if __name__ == '__main__':
    pytest.main()
