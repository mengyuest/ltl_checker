import subprocess

# check whether the brackets are matching (and valid)
def check_bracket(ltl_str):
    n_br = 0
    for i in range(len(ltl_str)):
        if ltl_str[i] == "(":
            n_br += 1
        elif ltl_str[i] == ")":
            n_br -= 1
        if n_br < 0:
            return False
    return n_br == 0


def convert(ltl_str):
    # add space between GF, FG
    # merge verb noun, and possible comma
    # change G to []
    # change F to <>
    # change | to ||
    # change & to &&
    # change - to !
    if check_bracket(ltl_str) == False:
        return "BRACKET MISSING"

    spin_str = ltl_str.replace("GF", "G F")
    rev = {"F": "G", "G": "F"}
    need_format = True
    while need_format:
        need_format = False
        finished_mod = False
        for i in range(1, len(spin_str)):
            if finished_mod:
                break
            if spin_str[i] == "G" or spin_str[i] == "F":
                for j in range(i-1, -1, -1):
                    if spin_str[j] == rev[spin_str[i]]:
                        need_format = True
                        # s[..., j] = "...F"
                        # s[j+1, i] = "   G"
                        # s[i+1, k] = "
                        n_br = 0
                        opened=False
                        for k in range(i+1, len(spin_str)):
                            if spin_str[k] == "(":
                                n_br += 1
                                opened=True
                            elif spin_str[k] == ")":
                                n_br -=1
                            if n_br == 0 and opened:
                                break
                        spin_str = spin_str[:j+1] + "(" + spin_str[j+1:k+1] + ")" + spin_str[k+1:]
                        finished_mod = True
                        break
                    elif spin_str[j] == " ":
                        continue
                    else:
                        break

    # remove the verb noun
    # whenever encounter a verb
    #   1. if no noun -> pass
    #   2. if one noun -> link them
    #   3. if two nouns with || && -> distributed
    #   4. if two nouns with , -> connect nouns and verb

    # ( F ( grab_v ( ( apple_n ) & ( orange_n ) ) ) )
    # ( F ( ( take_v ( pear_n ) ) U ( put_v ( pear_n , bucket_n ) ) ) )
    # ( F ( take_v ( ( pear_n ) | ( orange_n ) ) ) )
    spin_str = spin_str.replace("\'", "_")
    spin_str = spin_str.replace("(", " ( ")
    spin_str = spin_str.replace(")", " ) ")
    spin_str = spin_str.replace("  (  ", " ( ")
    spin_str = spin_str.replace(" (  ", " ( ")
    spin_str = spin_str.replace("  ( ", " ( ")
    spin_str = spin_str.replace("  )  ", " ) ")
    spin_str = spin_str.replace(" )  ", " ) ")
    spin_str = spin_str.replace("  ) ", " ) ")
    spin_str = spin_str.replace(", ", " , ")
    spin_str = spin_str.replace("  , ", " , ")

    need_recheck = True
    while need_recheck:
        need_recheck = False
        pieces = spin_str.split(" ")
        for pi, piece in enumerate(pieces):
            if is_v(piece):
                need_recheck = True
                if pi+1 == len(pieces) or pieces[pi + 1] != "(":  # single verb
                    pieces[pi] = link(piece)
                else:  # verb with (single / multi) nouns
                    noun_list = []
                    logic_sym = None
                    n_br = 0
                    opened = False
                    for k in range(1, len(pieces) - pi):
                        if is_n(pieces[pi + k]):
                            noun_list.append(pieces[pi+k])
                        elif pieces[pi + k] == "&" or pieces[pi+k] == "|":
                            logic_sym = pieces[pi + k]
                        elif pieces[pi + k] == "(":
                            n_br += 1
                            opened = True
                        elif pieces[pi + k] == ")":
                            n_br -= 1
                        elif pieces[pi + k] in [",", " "]:
                            do_nothing = True
                        else:
                            print("ERROR: haven't seen \"%s\", maybe add *_n or *_v"%(pieces[pi+k]))
                            raise NotImplementedError

                        if opened and n_br == 0:
                            break
                    if len(noun_list) == 1:  # single noun:            go_to_v(tree_n)
                        pieces[pi] = link(piece, noun_list[0])
                    else:  # multi nouns
                        if logic_sym is None:  # multi nouns:            put_v(pear_n, basket_n)
                            assert len(noun_list) == 2
                            pieces[pi] = link(piece, noun_list[0], noun_list[1])
                        else:  # multi nouns with logic: get_v (apple_n | banana_n)
                            cat_list = []
                            for noun in noun_list:
                                v_n_cat = link(piece, noun)
                                cat_list.append(v_n_cat)
                            cat_logic = (" " + logic_sym + " ").join(cat_list)
                            pieces[pi] = cat_logic

                    del pieces[pi + 1: pi + k + 1]
                break

        spin_str = " ".join(pieces)

    # convert to spin format
    spin_str = spin_str.replace("G", "[]")
    spin_str = spin_str.replace("F", "<>")
    spin_str = spin_str.replace("|", "||")
    spin_str = spin_str.replace("&", "&&")
    spin_str = spin_str.replace("-", "!")

    return spin_str


def is_v(s):
    return s[-2:] == "_v"


def is_n(s):
    return s[-2:] == "_n"


def link(v, n1=None, n2=None):
    if n1 is None:
        return v[:-2]
    elif n2 is None:
        return v[:-2] + "_" + n1[:-2]
    else:
        return v[:-2] + "_" + n1[:-2] + "_" + n2[:-2]


if __name__ == "__main__":

    file_path = "ltl300.txt"  # TODO change this path to other file if needed
    with open(file_path) as f:
        lines = f.readlines()

    n_total = 0
    n_valid = 0
    n_real = 0

    state_list=[]
    save_list=[]
    for li, line in enumerate(lines):
        if len(line.strip())==0:
            break
        if li<199 or li >200:
            continue
        n_total += 1
        save_list.append(dict())
        spin_ltl = convert(line)
        print(li, line, spin_ltl)

        cmd_line = "gltl2ba -f \"%s\" -t" % (spin_ltl)
        result = subprocess.run(cmd_line, shell=True, capture_output=True, text=True)

        save_list[-1]['stdout'] = result.stdout
        save_list[-1]['stderr'] = result.stderr
        save_list[-1]['ltl'] = line
        save_list[-1]['spin'] = spin_ltl

        if len(result.stdout) > 0:
            n_valid += 1
            if "accept" in result.stdout:
                n_real += 1
                state_list.append(2)
            else:
                state_list.append(1)
        else:
            state_list.append(0)

    print("%04d total   %04d valid (%.2f%%)   %04d real (%.2f%%)" % (n_total, n_valid, n_valid / max(1, n_total) * 100, n_real, n_real / max(1,n_total) * 100))

    for i in range(len(state_list)):
        if state_list[i] == 0:
            print("Error", i)
            print('ltl:', save_list[i]['ltl'])
            print('spin:', save_list[i]['spin'])
            print("err:", save_list[i]['stderr'])
        if state_list[i] == 1:
            print("False", i)
            print('ltl:', save_list[i]['ltl'])
            print('spin:', save_list[i]['spin'])
            print("fal:", save_list[i]['stdout'])