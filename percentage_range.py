
def perc(value, perc, fun=lambda n:n):
    """
    value => a number
    perc  => the requested percentage of $value to get
    fun   => a callable to be applied to the result
             (like int(), math.floor(), ...).
             Default to the identity function.
    """
    x = perc * value / 100
    return fun(x)

def in_perc_range(num, value, perc_value, fun=lambda n:n):
    """
    Returns True if $num is in the ±$perc range of $value.
    """
    x = perc(value, perc_value, fun)
    return num >= (value - x) and num <= (value + x)


"""
>>> in_perc_range(110, 100, 10)
True
>>> in_perc_range(111, 100, 10)
False
>>> in_perc_range(90, 100, 10)
True
>>> in_perc_range(89, 100, 10)
False
>>> 
"""
