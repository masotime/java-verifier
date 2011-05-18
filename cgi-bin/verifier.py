#!/usr/bin/python

import cgi
try:
    import json
except ImportError:
    import simplejson as json
import re
import subprocess
import datetime
import threading
import os
import logging
import sys

import formatutils
import shellutils

semapthore = threading.Semaphore()

class MyHandler():
    def __init__(self, path, params):
        self.path = path
        self.params = params

    def do_GET(self):
        path = self.path
        vars = self.params
        return self.do_request(path, 'GET', vars)
    
    def do_POST(self):
        ctype = os.environ.get('CONTENT_TYPE', '')
        if ctype == 'multipart/form-data':
            postvars = {}
            #postvars = cgi.parse_multipart(sys.stdin, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(os.environ.get('CONTENT_LENGTH', 0))
            postvars = cgi.parse_qs(sys.stdin.read(length), keep_blank_values=False)
        else:
            postvars = {}
        return self.do_request(self.path, 'POST', postvars)

    def do_request(self, path, method, vars):
        print "Content-type: application/json\n\n";
        
        # Parse out the posted JSON data
        jsonrequest = vars.get('jsonrequest', '{}')
        if type(jsonrequest) == type([]):
            jsonrequest = jsonrequest[0]
        requestDict = json.loads(jsonrequest)
        solution = requestDict.get('solution').strip()
        tests = requestDict.get('tests').strip()
        #formattedTests, resultList = formatutils.format_tests(tests, solution)

        # Update the Kava test file by pasting in the solution code and tests.
        code = formatutils.render_template('java/Tester.java', {'solution': solution, 'tests': tests})
        compileResult, result = shellutils.compile_java_and_get_results(code)
        
        # Create a valid json respose based on the xcodebuild results or error returned.        
        if compileResult['errors']:
            jsonResult = {'errors': compileResult['errors']}
        else:
            # it probably compiled, look for test results
            if result and result[0] == '{' and result[-1] == '}':
                jsonResult = json.loads(result)
            else: #other unecpected result
                jsonResult = {'errors': '%s\n%s' % (compileResult['warnings_and_errors'], result)}
                
        jsonResult['printed'] = compileResult['warnings_and_errors']
        
        # Return the results
        s = json.dumps(jsonResult)
        print s
        return


def main():
    path = os.environ.get('SCRIPT_NAME','').replace('/cgi-bin/', '')
    params = cgi.parse_qs(os.environ.get('QUERY_STRING',''), keep_blank_values=False)
    h = MyHandler(path, params)
    if os.environ.get('REQUEST_METHOD','') == 'GET':
        h.do_GET()
    else:
        h.do_POST()

main()