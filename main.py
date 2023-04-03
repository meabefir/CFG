import copy


def remove_dupes(list):
    return [el for i, el in enumerate(list) if i == list.index(el)]

class Rule:
    def __init__(self, _from, _to):
        self._from = _from
        self._to = _to

    def __str__(self):
        ret = f"{self._from} -> "
        for group in self._to:
            for el in group:
                ret += str(el)
                if el == group[-1]:
                    ret += " "
                    break
                ret += ", "
            if group == self._to[-1]:
                break
            ret += " | "
        return ret

    def __repr__(self):
        return self.__str__() + '\n'

class CFG:
    def __init__(self, terminals, rules):
        self.terminals = terminals
        self.rules = {}
        for rule in rules:
            self.rules[rule._from] = rule
        self.start = rules[0]._from

    def print_all_first(self):
        for rule in self.rules.values():
            print(f'first of ({rule._from}) is {self.first(rule._from)}')

    def print_all_follow(self):
        for rule in self.rules.values():
            print(f'follow of ({rule._from}) is {self.follow(rule._from)}')

    def first(self, el):
        if el not in [rule._from for rule in self.rules.values()]:
            return None

        ret = []
        for group in self.rules[el]._to:
            idx = 0
            has_epsilon = True
            while has_epsilon:
                if idx >= len(group):
                    ret += ["_"]
                    break
                local_ret = []
                if group[idx] in terminals or group[idx] == '_':
                    local_ret += [group[idx]]
                else:
                    if group[idx] != self.rules[el]._from:
                        local_ret += self.first(group[idx])

                if '_' in local_ret:
                    idx += 1
                else:
                    has_epsilon = False
                ret += local_ret

        ret = remove_dupes(ret)
        return ret

    def follow(self, el):
        if el not in [rule._from for rule in self.rules.values()]:
            return None

        ret = [] if el != self.start else ['$']
        for rule in self.rules.values():
            for group in rule._to:
                for i, group_el in enumerate(group):
                    if el == group_el:
                        # if it is at the end of the group
                        if i == len(group)-1:
                            if rule._from == el:
                                pass
                            else:
                                ret += self.follow(rule._from)
                        # if not,
                        else:
                            j = i + 1
                            if group[j] in self.terminals:
                                ret += [group[j]]
                                return remove_dupes(ret)
                            else:
                                first_of_j = self.first(group[j])
                                while True:
                                    for f in first_of_j:
                                        if f in terminals:
                                            ret += [f]
                                    if "_" in first_of_j:
                                        j += 1
                                        if j == len(group):
                                            if rule._from == self.start:
                                                ret += ["$"]
                                                break
                                            else:
                                                ret += self.follow(rule._from)
                                                break
                                        else:
                                            try:
                                                first_of_j = self.first(group[j])
                                            except:
                                                print("here")
                                                print(group, j)
                                                exit(0)
                                    else:
                                        break
        return remove_dupes(ret)

    def remove_left_recursion(self):
        new_rules = []
        for rule in self.rules.values():
            groups1 = []
            groups2 = []
            left, right = [], []
            for group in rule._to:
                if group[0] == rule._from:
                    left += [group]
                else:
                    right += [group]
            if len(left) == 0:
                new_rules += [copy.deepcopy(rule)]
                continue

            new_nonterminal = rule._from + "'"
            for el in right:
                groups2 += [el+[new_nonterminal]]
            for el in left:
                groups1 += [el[1:]+[new_nonterminal]]
            groups1 += [["_"]]

            new_rules += [Rule(rule._from, groups2)]
            new_rules += [Rule(new_nonterminal, groups1)]

        return CFG(self.terminals, new_rules)

    def left_factor(self):
        new_rules_to_add = []
        for rule in self.rules.values():
            groups = sorted(rule._to, key=lambda el: -len(el))
            max_len = len(groups[0])
            for current_len in range(max_len-1, 0, -1):
                # for each group that has at least this len, see if group[:len] is a common substring
                for i, group in enumerate(rule._to):
                    if len(group) < current_len:
                        continue
                    # search in other groups for commonalities
                    common = [group]
                    for j, group2 in enumerate(rule._to):
                        if i == j:
                            continue
                        if len(group2) < current_len:
                            continue
                        if group[:current_len] == group2[:current_len]:
                            common += [group2]
                    # factor what is in common
                    # remove them from rule._to first
                    if len(common) == 1:
                        continue
                    for g in common:
                        rule._to.remove(g)

                    new_symbol = rule._from+"'"
                    rule._to += [group[:current_len]+[new_symbol]]
                    new_groups = []
                    # print(common)
                    for g in common:
                        new_groups += [g[current_len:] if current_len < len(g) else ['_']]
                    new_rules_to_add += [Rule(new_symbol, new_groups)]
                    break
        return CFG(copy.deepcopy(self.terminals), copy.deepcopy(list(self.rules.values()))+new_rules_to_add)



    def __str__(self):
        return str(self.terminals) + '\n' + str(list(self.rules.values()))

with open("input.txt") as f:
    terminals = f.readline().split()
    rules = []

    line = f.readline()[:-1]
    while len(line):
        _from, _to = [el.strip() for el in line.split("->")]
        _to = [el.strip() for el in _to.split('|')]
        _to = [[el for el in group.split(',')] for group in _to]

        rules += [Rule(_from, _to)]
        line = f.readline()[:-1]

cfg = CFG(terminals, rules)
print(cfg)

cfg.print_all_first()
cfg.print_all_follow()

new_cfg = cfg.remove_left_recursion()
print(new_cfg)

factorized_cfg = cfg.left_factor()
print(factorized_cfg)
