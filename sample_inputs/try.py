try:
    raise NameError('HiThere')
except NameError:
    print 'An exception flew by!'
    raise

try:
    result = x / y
except ZeroDivisionError:
    print "division by zero!"
else:
    print "result is", result
finally:
    print "executing finally clause"
