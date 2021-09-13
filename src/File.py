import os
import re
from copy import deepcopy


class File:
    """
    """

    def __init__(self, fp, mode = 'r', **kwargs):
        
        if mode in ['r', 'r+'] and not os.path.isfile(fp):
            raise ValueError("File not found at path: {}".format(fp))

        # Interpret user input
        if   mode == "r"  : flags = os.O_RDONLY
        elif mode == "rb" : flags = os.O_RDONLY
        elif mode == "r+" : flags = os.O_RDWR   | os.O_CREAT
        elif mode == "w"  : flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        elif mode == "w+" : flags = os.O_RDWR   | os.O_CREAT | os.O_TRUNC
        elif mode == "a"  : flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        elif mode == "a+" : flags = os.O_RDWR   | os.O_CREAT | os.O_APPEND
        else:
            raise ValueError("Specify a valid file i/o mode.")

        # Create and open the file object.
        if fp.startswith("/"):
            fp = os.path.relpath(fp)

        fd = os.open(fp, flags)
        self.__dict__['_file'] = os.fdopen(fd, mode)

        # Define initial variables.
        self._abspath  = os.path.abspath(fp)
        self._fp       = fp
        self._cl       = ""
        self.eof       = False
        self._position = self.tell() if mode == "a" or mode == "a+" else 0
        self.verbose   = kwargs.get("verbose", False)

        # Other variables
        self._full = "" # full text of file, if it's been read

    @property
    def cl(self):
        """ Current line (most recently read line) of File. """
        return self._cl

    @property
    def abspath(self):
        """ Absolute filepath of File object. """
        return self._abspath

    @property
    def fp(self):
        """ Filepath of File object relative to the calling script's directory. """
        return self._fp

    @property
    def position(self):
        """ Current position in file (in bytes). """
        return self._position


    # Mandatory context-manager and wrapper functions

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._file.close()

    def __getattr__(self, name):
        return getattr(self._file, name)
    
    def __setattr__(self, name, value):
        return setattr(self._file, name, value)
    

    # Add File functionality

    def reinitialize_file(self):
        """ 'Reset' file object, clearing any positional arguments and data. """
        self.seek(0)
        self.eof = False
        self._cl = ""
        self._full = ""

    def readline(self):
        """ Read a line of the file. """
        self._cl = self._file.readline() 
        self._position += len(self._cl)
        return self._cl

    def readlines(self, *args):
        """ Read all remaining lines of the file. """
        data = self._file.readlines(*args)
        self._cl = data[-1]
        self.eof = True
        self._position += sum([len(i) for i in data])
        return data

    def has(self, text):
        """ Tests whether the file has a string, 'text' by reading entire file.
            Uses file.read, which stores the entire file in memory.
        """
        if not self._full:
            position = self.position
            self.seek(0)
            self._full = self.read()
            self.seek(position)
            self.eof = False
        return text in self._full

    def remaining_has(self, text):
        """ Searches the remaining, unread portion of the file for a string.
            Uses file.read, which stores the remaining file portion in memory.
        """
        position  = self.position
        remaining = self.read()
        self.seek(position)
        self.eof = False
        return text in remaining
        
    def seek_end(self):
        """ Go to the end of the file. """
        self.seek(0, os.SEEK_END)
        self._position = self.tell()
        self.eof = True
        self._cl = self.read_previous_line()

    def read_previous_line(self):
        """
        Returns the previous line (the line before the current line).
        I.e. if the parser is on line N (e.g. right at the beginning, or halfway 
        through), it'll walk back to line N-1 and return that.
        """
        position = self.tell()
        original_position = position
        newline_count = 0 # number of "\n"'s encountered
        new_line = []
        while True: 
            try:
                self.seek(position)
            except ValueError:
                # End of file
                self.seek(0, 2)
                position = self.tell()
                
            position -= 1
            new_char = self._file.read(1)
            if new_char == "\n" and newline_count == 0:
                newline_count += 1
                new_line.append(new_char)
            elif new_char == "\n" and newline_count == 1:
                self._position = self.tell()
                return "".join(new_line[::-1])
            elif new_char == "":
                continue
            elif newline_count == 1:
                new_line.append(new_char)
            else:
                continue

    def last_line(self):
        """ Return the last line of the file. 
            File position remains unchanged after the call. 
        """
        f_obj = open(self._fp, 'rb')
        last = get_last_line(f_obj)
        f_obj.close()
        return last

    def last_filled_line(self):
        """ Return the last non-blank line of the file. 
            File position remains unchanged after the call. 
        """
        f_obj = open(self._fp, 'rb')
        last = get_last_filled_line(f_obj)
        f_obj.close()
        return last
        

    def advance_to(self, keyword, **kwargs):

        """ Advances to, and returns, the first line containing the keyword. 
            Many additional functionalities exist.

            Mandatory arguments:
                keyword :  if type(keyword) is str, keyword is the string in line to stop at. 
                           if type(keyword) is list (of strings), stop once any of the keywords is found.
                           if type(keyword) is int, just advance that many lines ahead. 
                           if type(keyword) is int and keyword == -1, advance to end of file.

               
            Kwargs (type, default):
                count_strings (str or [str, ...], []) : count the number of lines containing string(s) until keyword is found.
                                                        strings defined in "junk" do not affect this option.
                count_lines (bool, False) : count the number of lines containing string(s) until keyword is found
                extra    (int, 0) : how many extra lines to read after keyword is found, stopping at end of file
                dump     (bool, False) : for debugging; print every line read
                hold     (int, 0) : return a list of that many lines immediately before keyword is found
                hold_all (bool, False) : return a list of all lines read before keyword is found
                tf       (function, None) : apply a transformation to each line read upon storing it
                verbose  (bool, False) : print warnings about hitting end of file
                exclude  (bool, False) : exclude the last line (keyword) from list of held items
                junk     (str or [str, ...], "") : string leaders (e.g. comments) to be ignored when holding
                                                    (and therefore transforming) lines
                keep_matches (str or [str, ...], "") : keep only lines containing the specified string(s),
                                                        which may be different than the keyword(s).

                include_first (bool, False) : parse the current line in addition to future ones.
                                             not always desirable, so we default this to false.

                write_to (file, None) : writes every line that would be held to the file object argument.
                                        i.e. if there's a transformation argument passed, it'll write
                                        the transformed line.

                NOT IMPLEMENTED:
                    reverse (optional) : Read the file backwards.

            Outputs:
                held (optional) : extra lines stored using hold

        """

        # -------------- Parse input arguments -------------- #

        n             = keyword if type(keyword) is int else 0
        dump          = kwargs.get('dump', False)
        count_strings = kwargs.get('count_strings', [])
        count_lines   = kwargs.get('count_lines', False) 
        extra         = kwargs.get('extra', 0)
        hold_all      = kwargs.get('hold_all', False) if not count_lines else 0
        tf            = kwargs.get('tf', False)
        verbose       = kwargs.get('verbose', self.verbose)
        exclude       = kwargs.get('exclude', False)
        junk          = kwargs.get('junk', "")
        keep_matches  = kwargs.get('keep_matches', "")
        include_first = kwargs.get("include_first", False)
        write_to      = kwargs.get("write_to", False)
        reverse       = kwargs.get("reverse", False)

        # Package some arguments into lists for consistent typing in body of method.
        if junk and type(junk) is str: junk = [junk]
        if keep_matches and type(keep_matches) is str: keep_matches = [keep_matches]
        if count_strings and type(count_strings) is str: count_strings = [count_strings]

        # NOT IMPLEMENTED: Determine whether we're reading forwards or backwards.
        get_next = self.read_previous_line if reverse else self._file.readline
        if reverse:
            raise NotImplementedError("Reverse file reading is not implemented yet.")
        if reverse and self.cl == "":
            self.seek_end()

        # Define "hold" based on various factors
        if count_lines: 
            hold = 0 # don't hold any lines
        elif hold_all: 
            hold = 1 # hold is now used as a flag
        elif keep_matches:
            hold_all = True
            hold = 1
        else: 
            hold = kwargs.get('hold', 0) # hold as many as user wants

        # Update hold if we're excluding the last line.
        if exclude and hold > 0:
            hold += 1 # hold desired number of lines
                      #    after dropping the line containing the keyword
        elif exclude and hold == 0:
            hold = 2 # hold the current and previous lines, return the latter


        if n: # User wants to simply advance n lines.

            keylist = [""]

            # advance to end of file
            if n == -1:
                def condition(keylist, n_read, n) -> bool:
                    return True

            # advance n_lines
            else:
                def condition(keylist, n_read, n) -> bool:
                    return n_read < n
                    
        else: # Generate keylist from all keywords given

            if type(keyword) is list:
                keylist = keyword
            elif type(keyword) is str:
                keylist = [keyword]
            else:
                raise ValueError("keyword must be a string or a list of strings")

            # Search for any of the keywords in each line
            def condition(keylist, n_read, n) -> bool:
                return self._cl == None or not any([re.search(key, self._cl) for key in keylist])


        # create default lambda function for processing input arguments
        if not tf:
            def tf(cl):
                return cl
        elif type(tf) is list:
            types = deepcopy(tf) 
            def tf(cl):
                split = cl.split()
                if len(split) != len(types):
                    s = "Line '{}' has {} elements but {} types provided for conversion"
                    raise ValueError(s.format(cl, len(split), len(types)))
                return [t(val) for t, val in zip(types, split)]
        else:
            # Use tf as given
            pass

        def transform(cl):
            return tf(cl)


        # Go until condition isn't met (i.e. until a keyword is in the current line)
        n_read = 0
        n_counted = 0
        held   = []

        # ------------ File parsing starts here ------------- #

        not_read_any = True # Allow the method to advance if it's looking
                            #  for a future line that matches the first one
        print("hold is", hold)
        while condition(keylist, n_read, n) or not_read_any:

            # Read next line (default) or include it, if user requests.
            if not_read_any and include_first:
                pass
            else:
                self._cl = get_next()

            # If count_strings is enabled, check whether the desired strings are in the line.
            if count_strings and any([re.search(key, self._cl) for key in count_strings]):
                n_counted += 1

            # Exit if end of file is reached.
            # We do this before transforming the line (below) to minimize errors.
            if not self._cl and not(reverse and not_read_any): 
            # (end of file)    (dummy flag, since reverse isn't implemented)  
                self.eof = True

                if verbose:
                    exit_str  = "Warning: EOF hit advancing to: "
                    exit_str += "'{}', " * (len(keylist) - 1) + "'{}'"
                    print(exit_str.format(*keylist))

                if hold or keep_matches: return held   
                elif count_lines:        return n_read
                elif count_strings:      return n_counted
                else:                    return self._cl # empty string

            # We've read at least one line at this point, so switch this flag.
            not_read_any = False

            # Hold and transform current line if desired. Also, write to file if desired.
            if (hold or keep_matches) and self._cl:
                write_this_line = False
                # Skip over the current line if we're watching for junk and there's junk in the line.
                junk_in_line = any(re.search(key, self._cl) for key in junk) if junk else False
                # If there's no junk and we're not holding only certain lines:
                if not junk_in_line and not keep_matches:
                    held.append(transform(self._cl))
                    write_this_line = True
                # If there's no junk and we're looking for certain lines:
                elif not junk_in_line and keep_matches and any([re.search(key, self._cl) for key in keep_matches]):
                    held.append(transform(self._cl))
                    write_this_line = True
                else:
                    pass

                # Write to file. 
                if write_to and write_this_line:
                    # Test condition() to allow for "exclude logic" to affect writing.
                    if (not exclude) or (exclude and condition(keylist, n_read, n)):
                        line = transform(self._cl)
                        write_to.write(line if line.endswith("\n") else line + "\n")
                    
                # Drop oldest held lines if a finite number is to be held.
                if len(held) > hold and not hold_all:
                    held.pop(0)

            # Debugging option.
            if dump: 
                try:
                    print(transform(self._cl))
                except:
                    print("Transform failed from {}".format(self._cl))


            # Increment n_read if the desired string is found.
            if type(count_lines) == str and count_lines and count_lines in self._cl:
                n_read += 1
            elif type(count_lines) == str and count_lines and count_lines not in self._cl:
                pass
            else:
                n_read += 1

        # ---------------- Condition is met ----------------- #

        # Hold on to extra lines if desired. will return (held + extra) lines
        # even if end of file is reached while running through extra lines
        if extra:
            for i in range(extra):
                self._cl = get_next()

                if hold: 
                    held += [transform(self._cl)]
                    if len(held) > (hold + extra) and not hold_all:
                        held.pop(0)

        # ---- Return value depending on what user wants ---- #

        if count_lines: # Return the number of lines counted
            return n_read
        elif count_strings:
            return n_counted
                
        if keep_matches:
            return held

        if hold: # Return all desired lines
            if hold == 1 and not hold_all:
                return held[0]
            else:
                if exclude:
                    return held[:-1]
                else:
                    return held
        else:
            return self._cl

