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
>>> pprint({c: ord(c) for c in 'Hello'})
{'H': 72, 'e': 101, 'l': 108, 'o': 111}
>>> echo([1,2,3])
[1, 2, 3]
```

The stdout and stderr of script block is not checked, any output are consider as valid.
```python
print("Hello World!")
```

Script block only fails to pass the test if the code block raises an exception.

<!-- doctest: +SKIP -->
```python
# this shall fails to pass the test
a = 3 / 0
```
