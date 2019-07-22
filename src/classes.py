from src import bitPack


class Rule:
    def __init__(self):
        self.index = 0
        self.text = ""
        self.lhs = ""
        self.rhs = []
        self.tokenMap = dict()

    def to_string(self):
        s = ""
        s += self.lhs + " -> " + " ".join(self.rhs)
        return s


class Conflict:
    def __init__(self, rule, i, j):
        self.rule = rule
        self.i = i
        self.j = j

    def to_string(self):
        s = ""
        s += self.rule.toString() + ": between " + self.rule.rhs[self.i] + " and " + self.rule.rhs[self.j]
        return s


class ReductionNode:
    def __init__(self, rule_id):
        self.rule_id = rule_id
        self.sons = dict()

    def has_son_with(self, label):
        if label in self.sons:
            return self.sons[label]
        return False

    def get_subtree_size(self):
        size = 2
        for label in self.sons:
            son = self.sons[label]
            size += son.getSubtreeSize()
            size += 2
        return size
  
    # linearised the tree through a post-order visit
    def subtree_to_vector(self, vector, current_position, non_terminals, terminals):
        sons_number = len(self.sons)
        sons_offsets = dict()

        # Call sons and populate sonsOffsets.
        for label in self.sons:
            son = self.sons[label]
            vector, sons_offsets[label], current_position = son.subtreeToVector(vector, current_position,
                                                                                non_terminals, terminals)

        my_offset = current_position
        vector[my_offset] = self.rule_id
        vector[my_offset + 1] = sons_number * 2
        current_position += 2

        for label in self.sons:
            # Get label value.
            label_index = bitPack.token_to_int(label, non_terminals, terminals)
            vector[current_position] = label_index
            vector[current_position + 1] = sons_offsets[label]
            current_position += 2
        return vector, my_offset, current_position
  
    def recursive_to_string(self, base_level):
        s = ""
        s += str(self.rule_id) + "\n"
        for label in self.sons:
            son = self.sons[label]
            s += "  " * (base_level + 1) + label + ":"
            s += son.recursiveToString(base_level + 1)
        return s
