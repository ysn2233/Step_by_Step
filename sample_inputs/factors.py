def factors(number, name):
    factor = number - 1
    while (factor > 1):
        if (number%factor == 0):
            factors(number//factor)
            factors(factor)
            return
        factor += 1
    print(number)

factors(144)
