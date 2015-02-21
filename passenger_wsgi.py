import sys, os
#sys.path.append(os.getcwd())
os.environ['DJANGO_SETTINGS_MODULE'] = "pim1.settings"

# following needed to find south
sys.path.append('/home/bhadmin13/python_pkgs/South-0.7.3-py2.5.egg')
#sys.path.append('/home/bhadmin13/python_pkgs/')
#sys.path.append('/home/bhadmin13/python_pkgs/lib/python2.5/site-packages/')
#sys.path.append('/home/bhadmin13/dx.bernardhecker.com/pim1/library')

## to handle wsgi error reporting glitch
cwd = os.getcwd()
myapp_directory = cwd + '/pim1'
### THE FOLLOWING LINE ERRORS IF UNCOMMENTED SINCE AN
### UNKNOWN DREAMHOST UPDATE, BEFORE 2014-05-30
### hope the fix works without it.
#sys.stdout = sys.stderr
sys.path.insert(0,myapp_directory)
sys.path.append(os.getcwd())


from paste.exceptions.errormiddleware import ErrorMiddleware

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

# To cut django out of the loop, comment the above application = ... line ,
# and remove "test" from the below function definition.

def testapplication(environ, start_response):
     status = '200 OK'
     output = 'Hello World! Running Python version ' + sys.version + '\n\n'
     response_headers = [('Content-type', 'text/plain'),
                         ('Content-Length', str(len(output)))]
     # to test paste's error catching prowess, uncomment the following line
     # while this function is the "application"
     #raise("error")
     start_response(status, response_headers)
     return [output]
application = ErrorMiddleware(application, debug=True)
