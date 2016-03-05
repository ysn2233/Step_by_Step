for letter in 'Python':  # example 1
    if letter == 'h':
        break
    print 'Current Letter :', letter

var = 10    # example 2
while var > 0:
    var = var -1
    if var == 5:
        continue
    print 'Current variable value :', var
print "Good bye!"