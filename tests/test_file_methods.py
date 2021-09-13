from fileParser.src.File import File
import os
import numpy as np
from shutil import copy

class TestFileMethods:
    
    def test_file_codes(self):
        fp      = "files/ozymandias.txt"
        dne     = "files/file_DNE.txt"
        fp_copy = "files/ozymandias_copy.txt"

        # read modes, existing file
        with File(fp, "r") as f:
            assert f.mode == "r"
            assert f.position == f.tell() == 0
        with File(fp, "rb") as f:
            assert f.mode == "rb"
            assert f.position == f.tell() == 0
        with File(fp, "r+") as f:
            assert f.mode == "r+"
            assert f.position == f.tell() == 0

        # read mode, nonexisting file
        try:
            with File(dne, "r") as f:
                assert False, "r cannot create files"
        except ValueError:
            assert True, "r cannot create files"

        try:
            with File(dne, "rb") as f:
                assert False, "rb cannot create files"
        except FileNotFoundError:
            assert True, "rb cannot create files"

        try:
            with File(dne, "r+") as f:
                assert True, "r+ can create files"
                os.remove(dne)
        except ValueError:
            assert True, "r+ can create files"

        # write mode, existing file
        copy(fp, fp_copy)
        with File(fp_copy, "w") as f:
            assert f.mode == "w"
            assert f.position == f.tell() == 0
        copy(fp, fp_copy)
        with File(fp_copy, "w+") as f:
            assert f.mode == "w+"
            assert f.position == f.tell() ==  0
        os.remove(fp_copy)

        # write mode, nonexisting file
        try:
            with File(dne, "w") as f:
                assert True, "w can create files"
                os.remove(dne)
        except ValueError:
            assert False, "w can create files"

        try:
            with File(dne, "w+") as f:
                assert True, "w+ can create files"
                os.remove(dne)
        except ValueError:
            assert True, "w+ can create files"

        # append mode, existing file
        with File(fp, "a") as f:
            assert f.mode == "a"
            assert f.position == f.tell()
        with File(fp, "a+") as f:
            assert f.mode == "a+"
            assert f.position == f.tell()
        
        # append mode, nonexisting file
        try:
            with File(dne, "a") as f:
                assert True, "a can create files"
                os.remove(dne)
        except ValueError:
            assert False, "a can create files"

        try:
            with File(dne, "a+") as f:
                assert True, "a+ can create files"
                os.remove(dne)
        except ValueError:
            assert True, "a+ can create files"
        

    def test_readline(self):
        # Test whether File and in-built python file object read identically
        with open("files/ozymandias.txt") as f:
            trueLine = f.readline()
        with File("files/ozymandias.txt") as f:
            testLine = f.readline()
        assert trueLine == testLine

    def test_readlines(self):
        # Test whether File and in-built python file object read identically
        with open("files/ozymandias.txt") as f:
            trueData = f.readlines()   
        with File("files/ozymandias.txt") as f:
            testData = f.readlines()
            assert f.position == f.tell()
        assert trueData == testData
        assert f.eof 

    def test_current_line(self):
        # Assert that we're on the line we think we're on while reading
        with File("files/ozymandias.txt") as f:
            assert f.cl == ""
            f.readline()
            assert f.cl == '"Ozymandias" by Percy Bysshe Shelley, 1818\n'
            f.readline()
            assert f.cl == "\n"
            f.readline()
            assert f.cl == "I met a traveller from an antique land,\n"

    def test_reinitialize(self):
        # Test file reinitialization
        with File("files/ozymandias.txt") as f:
            f.has("lone and level sands")
            f.reinitialize_file()
            assert f.tell() == 0
            assert not f.eof
            assert f._cl == ""
            assert f._full == ""

    def test_filepaths(self):
        # Test absolute and relative filepath handling
        cwd = os.getcwd()
        parent = "/".join(cwd.split("/")[:-1])
        with File("files/ozymandias.txt") as f:
            assert f.fp == "files/ozymandias.txt"
            assert f.abspath == os.path.join(cwd, "files/ozymandias.txt")
        with File("../README.md") as f:
            assert f.fp == "../README.md"
            assert f.abspath == os.path.join(parent, "README.md")

    def test_has(self):
        # Test `File.has`, which checks whether the file object contains text
        with File("files/ozymandias.txt") as f:
            assert f.has("lone and level sands")
            assert f.has("Shelley")
            assert not f.has("1819")
            assert not f.eof

    def test_remaining_has(self):
        # Check whether the remainder of a file has some text
        with File("files/ozymandias.txt") as f:
            f.readline()
            f.readline()
            f.readline()
            assert f.has("Shelley")
            assert not f.remaining_has("Shelley")
            assert f.has("antique")
            assert not f.remaining_has("antique") 
            assert "antique" in f.cl
            assert f.remaining_has("lone and level sands")
           
    def test_seek_end(self):
        # Test going to end of file
        with File("files/ozymandias.txt") as f:
            f.readline()
            position = f.position
            f.seek_end()
            assert f.position == f.tell() > position
            assert f.eof

    def test_read_previous_line(self):
        # Test reading backwards line by line
        with File("files/ozymandias.txt") as f:
            first_line = f.readline()
            second_line = f.readline()
            third_line = f.readline()
            test_line_1 = f.read_previous_line()
            test_line_2 = f.read_previous_line()
            assert test_line_1 == third_line
            assert test_line_2 == second_line
        

class TestAdvanceTo:
    
    qx = "files/quixote.txt"
    gfp = "files/pdb1gfl.ent"

    def test_keyword(self):
        s1 = 'Chapters I and II of "The History of Don Quixote" by Miguel de Cervantes, \n'
        s2 = 'In a village of La Mancha, the name of which I have no desire to call\n'
        s3 = 'will have it his surname was Quixada or Quesada (for here there is some\n'
        s4 = 'Quexana. This, however, is of but little importance to our tale; it\n'
        s5 = ''
        with File(self.qx) as f:
            f.advance_to("Quixote")
            assert f.cl == s1
            f.advance_to(['village', 'La Mancha']) # will stop at either of these two
            assert f.cl == s2
            f.advance_to(r'Qu\w{4}a') # was he named Quixada or Quesada?
            assert f.cl == s3
            f.advance_to(r'Qu....a') # it may also be Quexana
            assert f.cl == s4
            f.advance_to(-1) # go to end of file, returning blank line
            assert f.cl == s5, [f.cl, s5]


    def test_hold(self):
        # "hold = n" will return a list of length n containing the n-1 lines before
        # keyword is reached and the line with the keyword.
        c11 = "Obtained via Project Gutenerg (https://www.gutenberg.org/files/996/996-0.txt)\n"
        c21 = "In a village of La Mancha, the name of which I have no desire to call\n"
        c22 = "to mind, there lived not long since one of those gentlemen that keep a\n"
        with File(self.qx) as f:
            test_1 = f.advance_to(r"https.*txt", hold = 1)
            assert test_1 == c11 == f.cl
            test_2 = f.advance_to("gentlemen", hold = 2)
            assert test_2 == [c21, c22]
            
    def test_hold_all(self):
        # "hold_all = True" will hold every line read until the keyword is met
        # exclude_first(?)
        c11 = 'Chapters I and II of "The History of Don Quixote" by Miguel de Cervantes, \n'
        c12 = "Translated by John Ormsby.\n"

        c21 = "In a village of La Mancha, the name of which I have no desire to call\n"
        c22 = "to mind, there lived not long since one of those gentlemen that keep a\n"
        c23 = "lance in the lance-rack, an old buckler, a lean hack, and a greyhound\n"
        c24 = "for coursing. An olla of rather more beef than mutton, a salad on most\n"

        with File(self.qx) as f:
            test_1 = f.advance_to("Translated", hold_all = True)
            assert test_1 == [c11, c12]
            # Hold_all will skip the current line unless instructed otherwise
            f.advance_to(r"^In")
            test_2 = f.advance_to(r"\.", hold_all = True, include_first = True)
            assert test_2 == [c21, c22, c23, c24]

    def test_extra(self):
        # "extra = n" kwarg advances n extra lines after the keyword is found
        c11 = "CHAPTER I.\n"
        c12 = "WHICH TREATS OF THE CHARACTER AND PURSUITS OF THE FAMOUS GENTLEMAN DON\n"
        end_str = ''

        with File(self.qx) as f:
            # Test for basic functionality
            c1_test = f.advance_to("CHAPTER", extra = 1)
            assert c1_test == c12 != c11
            # If extra goes past the end of the file, it returns an empty string
            end_test = f.advance_to(r'^knighthood', extra = 10) 
            assert end_test == end_str
            
       
    def test_hold_and_extra(self):
        # Test "hold" and "extra" kwargs together:
        # Hold n lines including and before keyword is found, plus m extra.
        # If we hit the end of the file while going through extra lines,
        #  still return n + m lines; some will be blank.
        naming_rocinante = ["calling he was about to follow. And so, after having composed, struck\n",
                            "out, rejected, added to, unmade, and remade a multitude of names out of\n",
                            "his memory and fancy, he decided upon calling him Rocinante, a name, to\n",
                            "his thinking, lofty, sonorous, and significant of his condition as a\n",
                            "hack before he became what he now was, the first and foremost of all\n",
                            "the hacks in the world.\n"""]
        knighthood = ["not lawfully engage in any adventure without receiving the order of\n",
                      "knighthood.\n", "\n", "\n", "e02.jpg (39K)\n", "", ""]
        with File(self.qx) as f:
            test = f.advance_to("Rocinante", hold = 3, extra = 3)
            assert test == naming_rocinante
            test = f.advance_to("^knighthood", hold = 2, extra = 5)
            assert len(test) == 7 
            assert test == knighthood


    def test_transform(self):
        # "tf" will apply a transformation to every line that's held.
        # valid arguments are functions which operate on a single string.
        residues = ["ALA", "SER", "LYS", "GLY", "GLU", "GLU", "LEU", "PHE",
           "THR", "GLY", "VAL", "VAL", "PRO", "ILE", "LEU", "VAL", "GLU", "LEU",
           "ASP", "GLY", "ASP", "VAL", "ASN", "GLY", "HIS", "LYS", "PHE", "SER",
           "VAL", "SER", "GLY", "GLU", "GLY", "GLU", "GLY", "ASP", "ALA", "THR",
           "TYR", "GLY", "LYS", "LEU", "THR", "LEU", "LYS", "PHE", "ILE", "CYS",
           "THR", "THR", "GLY", "LYS", "LEU", "PRO", "VAL", "PRO", "TRP", "PRO",
           "THR", "LEU", "VAL", "THR", "THR", "PHE", "SER", "TYR", "GLY", "VAL",
           "GLN", "CYS", "PHE", "SER", "ARG", "TYR", "PRO", "ASP", "HIS", "MET",
           "LYS", "ARG", "HIS", "ASP", "PHE", "PHE", "LYS", "SER", "ALA", "MET",
           "PRO", "GLU", "GLY", "TYR", "VAL", "GLN", "GLU", "ARG", "THR", "ILE",
           "PHE", "PHE", "LYS", "ASP", "ASP", "GLY", "ASN", "TYR", "LYS", "THR",
           "ARG", "ALA", "GLU", "VAL", "LYS", "PHE", "GLU", "GLY", "ASP", "THR",
           "LEU", "VAL", "ASN", "ARG", "ILE", "GLU", "LEU", "LYS", "GLY", "ILE",
           "ASP", "PHE", "LYS", "GLU", "ASP", "GLY", "ASN", "ILE", "LEU", "GLY",
           "HIS", "LYS", "LEU", "GLU", "TYR", "ASN", "TYR", "ASN", "SER", "HIS",
           "ASN", "VAL", "TYR", "ILE", "MET", "ALA", "ASP", "LYS", "GLN", "LYS",
           "ASN", "GLY", "ILE", "LYS", "VAL", "ASN", "PHE", "LYS", "ILE", "ARG",
           "HIS", "ASN", "ILE", "GLU", "ASP", "GLY", "SER", "VAL", "GLN", "LEU",
           "ALA", "ASP", "HIS", "TYR", "GLN", "GLN", "ASN", "THR", "PRO", "ILE",
           "GLY", "ASP", "GLY", "PRO", "VAL", "LEU", "LEU", "PRO", "ASP", "ASN",
           "HIS", "TYR", "LEU", "SER", "THR", "GLN", "SER", "ALA", "LEU", "SER",
           "LYS", "ASP", "PRO", "ASN", "GLU", "LYS", "ARG", "ASP", "HIS", "MET",
           "VAL", "LEU", "LEU", "GLU", "PHE", "VAL", "THR", "ALA", "ALA", "GLY",
           "ILE", "THR", "HIS", "GLY", "MET", "ASP", "GLU", "LEU", "TYR", "LYS"]

        coords = [[-1.4093,  6.0494, -0.9249],
                  [-1.4989,  6.1651, -0.8981],
                  [-1.4809,  6.2769, -1.0006],
                  [-1.5790,  6.3397, -1.0384],
                  [-1.4760,  6.2190, -0.7570],
                  [-1.3573,  6.2992, -1.0472],
                  [-1.3364,  6.3821, -1.1651],
                  [-1.2245,  6.3347, -1.2591],
                  [-1.1264,  6.2734, -1.2155],
                  [-1.3236,  6.5292, -1.1216]]
        
        atom12 = ["ATOM", 12, "N", "LYS", "A", 3, -12.516, 63.462, -13.894, 
                    1.00, 38.90, "N"]

        with File(self.gfp) as f:
            
            # Test: get the sequence of residues in the first domain of GFP
            f.advance_to("^SEQRES")
            split = lambda x: x[19:].strip("\n").split()
            # Hold onto the current line containing "SEQRES   1 A", but 
            #  exclude the line containing "SEQRES   1 B"
            res_test = f.advance_to("SEQRES   1 B", hold_all = True, tf = split, 
                                    exclude = True, include_first = True)
            res_test = [res for row in res_test for res in row] # concatenate lists
            assert res_test == residues

            # Test: get the coordinates of the first 10 atoms in nanometers
            #  (PDB records positions in angstroms)
            f.advance_to("^ATOM")
            get_xyz = lambda x: [round(float(i)/10, 4) for i in x.split()[6:9]]
            coords_test = f.advance_to(r"^ATOM\s+11", hold_all = True, tf = get_xyz, 
                                    exclude = True, include_first = True)
            assert coords_test == coords

            # Test: lines can get parsed by passing a list of types:
            tf_list = [str, int, str, str, str, int, float, float, float, 
                        float, float, str]
            atom12_test = f.advance_to(1, hold = 1, tf = tf_list)
            assert atom12_test == atom12

            # Test: if the transformation fails, the error is passed onto user.
            tf_list = [float] * 12
            try:
                atom13_test = f.advance_to(1, hold = 1, tf = tf_list)
                assert False, "Converting 'ATOM' to float will raise ValueError"
            except ValueError:
                assert True, "Converting 'ATOM' to float raised ValueError"
                
            # Test: we raise an error if len(tf_list) != len(f.cl.split())
            tf_list = [str] * 5
            try:
                atom14_test = f.advance_to(1, hold = 1, tf = tf_list)
                assert False, "5 types provided but there are 12 items"
            except ValueError:
                assert True, "5 types provided but there are 12 items"


    def test_count_lines(self):
        # "count_lines" returns the number of lines read until the keyword(s) appear
        with File(self.qx) as f:

            # Test: make sure the first line being read is counted
            n_read = f.advance_to("Chapters", count_lines = True)
            assert n_read == 1

            # Test: standard behavior
            n_read = f.advance_to("Full Size", count_lines = True)
            assert n_read == 12


    def test_count_strings(self):
        # "count_strings" returns the number of lines on which the specified strings are found
        #   until the keyword(s) appear.
        with File(self.qx) as f:
            
            # Test: keyword and strings appear on same line
            n_matches = f.advance_to("Quixote", count_strings = "Quixote")
            assert n_matches == 1

            # Test: multiple keywords appear on same line - only count once
            n_matches = f.advance_to(-1, count_strings = ["[kK]night", "[eE]rrant"])
            assert n_matches == 22

            f.reinitialize_file()

            # Test: how many times "Don Quixote" is mentioned 
            n_matches = f.advance_to(-1, count_strings = "Don Quixote")
            # We miss one compared to a "ctrl+f" result because of line breaks
            assert n_matches == 14
        
    def test_exclude(self):
        # "exclude = True" excludes the line containing the keyword(s) from the list of held lines
        #   returned to the user. "hold = n, exclude = True" still returns n lines.
        with File(self.qx) as f:
            
            # Test: exclude = True, hold = n.
            lines = f.advance_to("[fF]ull [sS]ize", hold = 2, exclude = True)
            assert lines == ["p007.jpg (150K)\n", "\n"]
            
            # Test (edge case): exclude without hold enabled. ought to return one line,
            #  which is the line before the line containing the keyword(s).
            f.reinitialize_file()
            line = f.advance_to("[fF]ull [sS]ize", exclude = True)
            assert line == ["\n"]

            # Test (edge case): exclude without hold = 1. same expected result as last test.
            f.reinitialize_file()
            line = f.advance_to("[fF]ull [sS]ize", hold = 1, exclude = True)
            assert line == ["\n"]

    def test_junk(self):
        # "junk = [str, ...]" ignores lines containing any of the specified strings
        #   when holding (and therefore transforming) lines.
        with File(self.gfp) as f:
            f.advance_to("^HETATM")
            non_water = f.advance_to("^CONECT", include_first = True, hold_all = True, exclude = True,
                                     junk = r"^\w+\s+\w+\s+\w+\s+HOH")
            assert non_water == [] # no non-water heteroatoms

        c11 = 'Chapters I and II of "The History of Don Quixote" by Miguel de Cervantes, \n'
        c12 = "Translated by John Ormsby.\n"
        c13 = "Obtained via Project Gutenerg (https://www.gutenberg.org/files/996/996-0.txt)\n"
        with File(self.qx) as f:
            no_blanks = f.advance_to(4, hold_all = True, junk = "^\n")
            assert no_blanks == [c11, c12, c13]

    def test_keep_matches(self):
        # "keep_matches = [str, ...]" holds onto all lines containing the specified srings.
        # keep_matches and hold cannot both be enabled at the same time.
        images = ["p007.jpg (150K)\n", "p007b.jpg (61K)\n", "p007c.jpg (97K)\n", "p008.jpg (289K)\n", "e02.jpg (39K)\n"]
        conects = ["CONECT  480  495                                                                \n",
                    "CONECT  495  480                                                                \n",
                    "CONECT 2306 2321                                                                \n",
                    "CONECT 2321 2306                                                                \n"]
        with File(self.qx) as f:
            image_lines = f.advance_to(-1, keep_matches = r".jpg")
            assert image_lines == images
        with File(self.gfp) as f:
            conect_lines = f.advance_to(-1, keep_matches = r"^CONECT")
            assert conect_lines == conects

    def test_write_to(self):
        # "write_to = file_object" writes held (and transformed) lines to file_object
        # Test: copy entire file
        qx_temp = "files/quixote_temporary.txt"
        with File(self.qx) as old, File(qx_temp, "w+") as new:
            old.advance_to(-1, hold_all = True, write_to = new)

        with File(self.qx) as old, File(qx_temp, "r") as new:
            old_lines = old.readlines()
            new_lines = new.readlines()
            assert len(old_lines) == len(new_lines)
            for ol, nl in zip(old_lines, new_lines):
                assert ol == nl
        
        # clean up
        os.remove(qx_temp)

        # Test: only hold some lines and transform them
        gfp_temp = "files/outputs/gfp_write_to.txt"
        gfp_test = "files/outputs/gfp_write_to_test.txt"
        tf = lambda x: " ".join([x.split()[0]] + x.split()[6:9])
        with File(self.gfp) as old, File(gfp_temp, "w+") as new:
            old.advance_to(r"^ATOM")
            old.advance_to(r"^HETATM", hold_all = True, junk = "TER", write_to = new, tf = tf, exclude = True)
       
        with File(gfp_temp, 'r') as old, File(gfp_test, 'r') as new:
            old_lines = old.readlines()
            new_lines = new.readlines()
            assert len(old_lines) == len(new_lines)
            for ol, nl in zip(old_lines, new_lines):
                assert ol == nl
            


"""
corner cases:
    - seek end and read previous line
"""

if __name__ == "__main__":
    t = TestAdvanceTo()
    t.test_write_to()
            
