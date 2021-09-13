This module presents a Python-based file parser,
prioritizing utility and flexiblity of possible file operations.

The parser defines a `File` class which works in the `with` context:

```
with File("ozymandias.txt") as f:
  data = f.readlines()
  print(data[1:4])

>>>  ['"Ozymandias" by Percy Bysshe Shelley, 1818\n', '\n', 'I met a traveller from an antique land,\n', 'Who said—“Two vast and trunkless legs of stone\n']
```


