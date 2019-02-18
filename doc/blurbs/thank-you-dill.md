
I've been developing [a cryptocurrency trading
bot](https://gitlab.com/metaperl/adsactly-gridtrader) for a year or
two off and on. The data structures used in the code are fairly
nested. For instance, there is a class `GridTrader` which has a
2-level dictionary whose terminal value is an instance of class `Grid`
and grid has a list of floats within it.

Without really planning for long-term, I started by persisting the
state of the program between runs using the core module
[pickle](https://docs.python.org/3/library/pickle.html). However, I
eventually ran into some data structures which pickle could not
handle. A quick Google and lo and behold
[dill](https://github.com/uqfoundation/dill) to the rescue!

I've been using it ever since to store the entire state of my trading
application between shell invocations with no hitches whatsoever.

Had I chosen an external (No)SQL approach, [my
code](https://gitlab.com/metaperl/adsactly-gridtrader/blob/master/gridtrader/gridtrader.py#L380)
would be even more complex because I would have to write logic to
marshal data to and from the external storage mechanism.

**THANK YOU DILL!**
