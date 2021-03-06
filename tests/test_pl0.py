from intergen.intergen import get_parser, GrammarError
import pytest


@pytest.fixture
def parser():
    return get_parser()


def test_assign(parser):
    "最简单的assign"
    code = "a := b"
    result = parser(code)
    assert len(result) == 1
    assert result[0] == 'a := b'


def test_expression(parser):
    "来自讲义随堂练习"
    code = "a := b * ( - c + d )"
    result = parser(code)
    assert result == ['temp0 := uminus c', 'temp1 := temp0 + d', 'temp2 := b * temp1', 'a := temp2']


def test_expression2(parser):
    code = "e := - ( a + b ) * ( c + d ) + ( a + b + c )"
    result = parser(code)
    assert result == ['temp0 := a + b', 'temp1 := c + d', 'temp2 := temp0 * temp1', 'temp3 := uminus temp2',
                      'temp4 := a + b', 'temp5 := temp4 + c', 'temp6 := temp3 + temp5', 'e := temp6']


def test_expression3(parser):
    "测试优先级"
    code = "e := - a + b * c + d"
    result = parser(code)
    assert result == ['temp0 := uminus a', 'temp1 := b * c', 'temp2 := temp0 + temp1', 'temp3 := temp2 + d',
                      'e := temp3']


def test_if_then(parser):
    code = "if a then b := c"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 3', 'b := c']


def test_if_else(parser):
    code = "if a then b := c else b := d"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 4', 'b := c', 'j, -, -, 5', 'b := d']

def test_if_not_else(parser):
    code = "if not a then b := c else b := d"
    result = parser(code)
    print(result)
    assert result == ['jnz, a, -, 4', 'j, -, -, 2', 'b := c', 'j, -, -, 5', 'b := d']


def test_nested_if(parser):
    code = "if a then if b then c := d"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 5', 'jnz, b, -, 4', 'j, -, -, 5', 'c := d']


def test_nested_if_else(parser):
    code = "if a then if b then c := d else e := f"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 7', 'jnz, b, -, 4', 'j, -, -, 6', 'c := d', 'j, -, -, 7', 'e := f']


def test_nested_if_else2(parser):
    code = "if a then if b then c := d else e := f else g := h"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 8', 'jnz, b, -, 4', 'j, -, -, 6', 'c := d', 'j, -, -, 9', 'e := f',
                      'j, -, -, 9', 'g := h']


def test_expression1(parser):
    code = "a := i + j"
    result = parser(code)
    assert result == ['temp0 := i + j', 'a := temp0']


def test_bool_id(parser):
    code = "if not a then c := d"
    result = parser(code)
    assert result == ['jnz, a, -, 3', 'j, -, -, 2', 'c := d']


def test_bool_paren(parser):
    # 括号总是加在expression上而不是bool_expression上
    code = "if not ( ( a ) ) then c := d"
    result = parser(code)
    assert result == ['jnz, a, -, 3', 'j, -, -, 2', 'c := d']


def test_bool_not(parser):
    code = "if not a > b then c := d"
    result = parser(code)
    assert result == ['j>, a, b, 3', 'j, -, -, 2', 'c := d']


def test_bool_and(parser):
    code = "if not a > b and c <= d then e := f"
    result = parser(code)
    assert result == ['j>, a, b, 5', 'j, -, -, 2', 'j<=, c, d, 4', 'j, -, -, 5', 'e := f']


def test_bool_or(parser):
    code = "if not a > b and c <= d or e <> f then g := h"
    result = parser(code)
    assert result == ['j>, a, b, 4', 'j, -, -, 2', 'j<=, c, d, 6', 'j, -, -, 4', 'j<>, e, f, 6', 'j, -, -, 7', 'g := h']

def test_bool_mult(parser):
    code = "if not not not a > b then c := d"
    result = parser(code)
    assert result == ['j>, a, b, 3', 'j, -, -, 2', 'c := d']

def test_bool(parser):
    code = "if not ( a > b and c or d ) or not e <> f and not g then h := i"
    result = parser(code)
    assert result == ['j>, a, b, 2', 'j, -, -, 4', 'jnz, c, -, 6', 'j, -, -, 4', 'jnz, d, -, 6', 'j, -, -, 10',
                      'j<>, e, f, 11', 'j, -, -, 8', 'jnz, g, -, 11', 'j, -, -, 10', 'h := i']


def test_bool_expression(parser):
    code = "if not ( - a + b ) * c and ( d or a + b > d + e ) then b := c"
    result = parser(code)
    assert result == ['temp0 := uminus a', 'temp1 := temp0 + b', 'temp2 := temp1 * c', 'jnz, temp2, -, 12',
                      'j, -, -, 5', 'jnz, d, -, 11', 'j, -, -, 7', 'temp3 := a + b', 'temp4 := d + e',
                      'j>, temp3, temp4, 11', 'j, -, -, 12', 'b := c']


def test_while(parser):
    code = "while a < b do a := b"
    result = parser(code)
    assert result == ['j<, a, b, 2', 'j, -, -, 4', 'a := b', 'j, -, -, 0']


def test_while_nested(parser):
    code = "while a do while a do a := a + ( - a )"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 9', 'jnz, a, -, 4', 'j, -, -, 0', 'temp0 := uminus a',
                      'temp1 := a + temp0', 'a := temp1', 'j, -, -, 2', 'j, -, -, 0']


def test_while2(parser):
    code = "while a + b < c * d do while not ( - a + b ) * c and ( d or a + b > d + e ) do if not ( ( a ) ) then b := c else a " \
           ":= - ( a + b ) * ( c + d ) + ( a + b + c ) "
    result = parser(code)
    assert result == ['temp0 := a + b', 'temp1 := c * d', 'j<, temp0, temp1, 4', 'j, -, -, 29', 'temp2 := uminus a', 'temp3 := temp2 + b', 'temp4 := temp3 * c', 'jnz, temp4, -, 0', 'j, -, -, 9', 'jnz, d, -, 15', 'j, -, -, 11', 'temp5 := a + b', 'temp6 := d + e', 'j>, temp5, temp6, 15', 'j, -, -, 0', 'jnz, a, -, 19', 'j, -, -, 17', 'b := c', 'j, -, -, 4', 'temp7 := a + b', 'temp8 := c + d', 'temp9 := temp7 * temp8', 'temp10 := uminus temp9', 'temp11 := a + b', 'temp12 := temp11 + c', 'temp13 := temp10 + temp12', 'a := temp13', 'j, -, -, 4', 'j, -, -, 0']

def test_while3(parser):
    code = "while a do while not b * c and ( d or e ) do if not ( ( a ) ) then b := c else a := f"
    result = parser(code)
    assert result == ['jnz, a, -, 2', 'j, -, -, 16', 'temp0 := b * c', 'jnz, temp0, -, 0', 'j, -, -, 5', 'jnz, d, -, 9', 'j, -, -, 7', 'jnz, e, -, 9', 'j, -, -, 0', 'jnz, a, -, 13', 'j, -, -, 11', 'b := c', 'j, -, -, 2', 'a := f', 'j, -, -, 2', 'j, -, -, 0']

def test_call(parser):
    code = "call f ( a , b )"
    result = parser(code)
    assert result == ['param a', 'param b', 'call f']

def test_call2(parser):
    code = "call f ( a , x + y )"
    result = parser(code)
    assert result == ['temp0 := x + y', 'param a', 'param temp0', 'call f']

def test_goto(parser):
    code = "{ l : a := b ; goto l }"
    result = parser(code)
    assert result == ['a := b', 'j, -, -, 0']

def test_goto1(parser):
    code = "{ d := c ; l : a := b ; goto l }"
    result = parser(code)
    assert result == ['d := c', 'a := b', 'j, -, -, 1']

def test_goto2(parser):
    code = "{ b := a ; goto l ; l : a := b }"
    result = parser(code)
    assert result == ['b := a', 'j, -, -, 2', 'a := b']

def test_label_error(parser):
    code = "{ l : a := b ; l : c := d }"
    with pytest.raises(GrammarError):
        parser(code)

def test_goto_variable(parser):
    code = "{ a := b ; goto a }"
    with pytest.raises(GrammarError):
        parser(code)
