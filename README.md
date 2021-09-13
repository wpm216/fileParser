This module presents a Python-based file parser,
prioritizing utility and flexiblity of possible file operations.

The parser defines a `File` class which works in the `with` context:

```
with File("ozymandias.txt") as f:
  data = f.readlines()
  print(data[1:4])

>>>  ['"Ozymandias" by Percy Bysshe Shelley, 1818\n', '\n', 'I met a traveller from an antique land,\n', 'Who said—“Two vast and trunkless legs of stone\n']
```

Wrapped around the python `file object`,`File` has identical behavior for in-built functions.
Files can be opened in any mode:
```
with File(test_path, 'w+') as f:
    f.write('Hello world!'\n)
```

Additionally, a variety of utility functions are implemented for convenient parsing:

Advance to the first line containing any item in the list of keywords
(regex included) and return the line.
```
with File(path) as f:
    current_line = f.advance_to(["keyword1", r"^(\s+)"]) 
```

Advance forward five lines or to the end of the file:
```
with File(path) as f:
    cl = f.advance_to(5)

# go to end of file
with File(path) as f:
    cl = f.advance_to(-1)
```

Count the number of lines containing a string or strings:
```
with File(path) as f:
    number = f.advance_to(-1, count_strings = ["WARNING", "ERROR"])
```

Return lines before and after the (like grep -A and grep -B)
```
with File(path) as f:
    # (hold = 1 returns the current line, so hold = n returns the
    #  line containing the keyword and n-1 additional lines)
    cl = f.advance_to("treasure", hold = n_before + 1, extra = n_after)
```

Transform lines, e.g. turning some items in the line into floats:
```
with File(path) as f:
    subset_to_float = lambda x: [float(i) for i in x.split()[2:5]]
    data = f.advance_to(10, tf = subset_to_float)
```

Keep only the lines containing some keywords
```
with File(path) as f:
    molecule_data = f.advance_to(-1, keep_matches = [r"^ATOM", r"^TER", r^"HETATM", r"^CONECT"])
```

Skip some lines without transforming or holding them, e.g. blank lines:
```
with File(path) as f:
    lines_with_data = f.advance_to(-1, hold_all = True, junk = [r"^\n", r"^\r", r"^(\s+)\n"])
```

Write held (and optinally transformed) lines to a new file. 
Can skip lines by defining `junk`:
```
with File(path) as f, File(new_file_path, 'w+') as new:
    # emphasize our appreciation for mangoes over apples
    transform = lambda x: x.replace("mango", "MANGO").replace("mangoes", "MANGOES")
    f.advance_to(-1, tf = transform, write_to = new, junk = r"(\s+)apple(\s+)")
```

For a more extensive list of examples and keyword interactions, 
see `tests/test_file_methods.py`.

