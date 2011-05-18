import re
import logging

types = [
    {'call': 'AssertEquals'},
    {'call': 'AssertEqualObjects'},
]

def correct_line_numbers(string, src_file):
    result = ''
    for line in string.split('\n'):
        mo = re.compile('^(.*%s:)([0-9]+)(:.*)$' % src_file).search(line)
        if mo:
            lineno = int(mo.group(2)) - 3
            line = '%s%s%s' % (mo.group(1), lineno, mo.group(3))
        if result:
            result += '\n'
        result += '%s' % line
    return result
    
def grep(string, pattern):
    matches = ''
    for line in string.split('\n'):
        match = (pattern in line)
        if not match:
            try:
                match = True if re.compile(pattern).search(line) else False
            except:
                pass
        if match:
            matches += str(line) + '\n'
    return matches

def format_tests(tests, solution):
    global types
    res = ''
    resultList = []
    testCases = tests.splitlines()
    line_number = 11 + len(solution.splitlines()) #the first test line
    for testCase in testCases:
        testCase = testCase.strip()
        type = None
        if not testCase.startswith('//'):
            for t in types:
                if t['call'] in testCase:
                    type = t
                    break
        if type:
            exp = '([^,]+)'
            parse_exp = '%s\(%s *, *%s\);' % (type['call'], exp, exp)
            mo = re.compile(parse_exp).search(testCase)
            if mo:
                call = mo.group(1)
                expected = mo.group(2)
                resultList.append({
                    'call': call,
                    'expected': expected,
                    'received': expected,
                    'correct': None,
                    'line': line_number,
                    'type': type
                    })
                res += '%s(%s, %s);\n' % (type['call'], call, expected)
            else:
                res += '%s\n' % testCase
        else:
            res += '%s\n' % testCase
        line_number += 1
    logging.info('res:\n%s\nresultList: %s' % (res, resultList))
    return res, resultList

def render_template(path, variables):
    f = open(path, 'r')
    template = f.read()
    return template % variables
