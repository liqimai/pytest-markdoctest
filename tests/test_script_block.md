# Script Block
Script blocks are non-interactive code blocks, i.e. no prompt `>>>`. They are useful for serving as test setup.

First we import some packages and define useful function/class for future use.
```python
import math
from pprint import pprint
def echo(obj):
    print(obj)
```

Then we can use imported packages and predefined functions.
```python
>>> math.pow(2, 2)
4.0
>>> pprint({c: ord(c) for c in 'Hello World!'}, indent=4)
{   ' ': 32,
    '!': 33,
    'H': 72,
    'W': 87,
    'd': 100,
    'e': 101,
    'l': 108,
    'o': 111,
    'r': 114}
>>> echo([1,2,3])
[1, 2, 3]
```

The stdout and stderr of script block is not checked, any output are consider as valid.
```python
print("Hello World!")
```

Script block only fails if the code block raises an exception.
```python
# doctest: +SKIP
a = 3 / 0
```
