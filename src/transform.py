

# Takes as input a description of a grammar H=(non_terminals, terminals, rules, axiom)
# and creates an equivalent invertible grammar G=(v, terminals, P, newAxiom) by applying an
# optimized version of Harrison's algorithm.
def delete_repeated_rhs(non_terminals_list, terminals_list, axiom, new_axiom, rules):
	# To apply Harrison's algorithm, the input grammar H must satisfy the following condition:
	# either it has no copy rules or it can have copy rules, but the axiom must not have rules
	# with the same rhs as other non terminals of H.
	# If these conditions do not hold, all its copy rules will be deleted.
	non_terminals = set(non_terminals_list)
	terminals = set(terminals_list)
	
	dict_rules = initialize_dict_rules(rules)
	
	# Check if the input grammar satisfies the preconditions of the algorithm
	# for keyRhs, valueLhs in dict_rules.items():
	# 	if axiom in valueLhs and len(valueLhs) > 1:
	# 		has_axiom_with_rhs = True
	# 		break

	# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	# --------------------------------------
	# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	# NOTE!!!!! I commented out the two following lines replacing them with the third line so that the copy rules
	# are ALWAYS removed, but they should be enabled again
	# if has_copy_rules(non_terminals, rules) and hasAxiomWith_rhs:
	# 	delete_copy_rules(non_terminals_list, rules, dict_rules)
	delete_copy_rules(non_terminals_list, rules, dict_rules)

	# Initialize the new non terminal set v
	v = set(dict_rules.values())

	# Initialize the new set of productions P with the terminal rules of the original grammar
	# and avoid doing the next checks and expansions for these rules, deleting them from the dictionary of rules
	new_dict_rules = {}
	for keyRhs, valueLhs in dict_rules.items()[:]:
		is_terminal_rule = True
		for token in keyRhs:
			if token in non_terminals:
				is_terminal_rule = False
				break
		if is_terminal_rule:
			new_dict_rules[keyRhs] = valueLhs
			del dict_rules[keyRhs]
	
	# Add the new rules by expanding non terminals in the rhs
	dict_rules_for_iteration = {}
	loop = True
	while loop:
		for keyRhs, valueLhs in dict_rules.items():
			new_rule_rhs = []
			add_new_rules(dict_rules_for_iteration, keyRhs, valueLhs, non_terminals, v, new_rule_rhs)
		added_non_terminals = set(dict_rules_for_iteration.values()).difference(v)
		v.update(added_non_terminals)
		new_dict_rules.update(dict_rules_for_iteration)
		if len(added_non_terminals) == 0:
			loop = False
	
	# List of non terminals of the invertible grammar G
	v = set(new_dict_rules.values())

	# Delete rules with rhs with undefined nonterminals:
	# this implementation of the algorithm can generate rhs of rules with nonterminals which are no more defined.
	# TODO: a bit slightly more efficient version can store beforehand the list of rhs of every nonterminal and then
	#  delete the nonterminals whose rhs are all deleted.
	deleted = True
	while deleted:
		deleted = False
		for keyRhs, valueLhs in new_dict_rules.items()[:]:
			for token in keyRhs:
				if (token not in terminals) and (token not in v):
					del new_dict_rules[keyRhs]
					deleted = True
					break
		if deleted:
			v = set(new_dict_rules.values())
	
	v.add(frozenset([new_axiom]))

	# Add rules for the axiom of G, which have as rhs all new non terminals that contain the old axiom
	for nonTerm in v:
		if axiom in nonTerm:
			# If the rule has exactly the old axiom as rhs, replace it with the new axiom
			if len(nonTerm) == 1 and tuple([nonTerm]) in new_dict_rules:
				new_dict_rules[tuple([frozenset([new_axiom])])] = new_dict_rules[tuple([nonTerm])]
			new_dict_rules[tuple([nonTerm])] = frozenset([new_axiom])

	return new_dict_rules, v


def initialize_dict_rules(rules):
	dict_rules = {}
	for rule in rules:
		# Use frozenset even if they will be united when two lhs have to be merged,
		# but avoid to convert sets representing non terminals in frozen sets within function addNewRules
		value_lhs = frozenset([rule.lhs])
		key_rhs = tuple(rule.rhs)
		if key_rhs in dict_rules:
			dict_rules[key_rhs] = dict_rules[key_rhs].union(value_lhs)
		else:
			dict_rules[key_rhs] = value_lhs
	return dict_rules


def add_new_rules(dict_rules_for_iteration, key_rhs, value_lhs, non_terminals, new_non_terminals, new_rule_rhs):
	if len(key_rhs) == 0:
		new_key_rhs = tuple(new_rule_rhs)
		if new_key_rhs in dict_rules_for_iteration:
			dict_rules_for_iteration[new_key_rhs] = dict_rules_for_iteration[new_key_rhs].union(value_lhs)
		else:
			dict_rules_for_iteration[new_key_rhs] = value_lhs
		return
	token = key_rhs[0]
	if token in non_terminals:
		for non_term_super_set in new_non_terminals:
			if token in non_term_super_set:
				new_rule_rhs.append(non_term_super_set)
				add_new_rules(dict_rules_for_iteration, key_rhs[1:], value_lhs, non_terminals, new_non_terminals, new_rule_rhs)
				new_rule_rhs.pop()
	else: 
		# token in terminals
		new_rule_rhs.append(token)
		add_new_rules(dict_rules_for_iteration, key_rhs[1:], value_lhs, non_terminals, new_non_terminals, new_rule_rhs)
		new_rule_rhs.pop()


def has_copy_rules(non_terminals, rules):
	for rule in rules:
		if len(rule.rhs) == 1 and rule.rhs[0] in non_terminals:
			return True
	return False


def delete_copy_rules(non_terminals, rules, dict_rules):
	# Copy contains the rhs of the copy rules of each nonterminal
	copy = {}
	# Contains the list of rhs of each nonterminal but not the rhs of copy rules
	rhs_dict = {}

	# Initialization
	for n in non_terminals:
		copy[n] = set()

	for rule in rules:
		if len(rule.rhs) == 1 and rule.rhs[0] in non_terminals:
			# It is a copy rule
			# Update the copy set of rule.lhs
			copy[rule.lhs].add(rule.rhs[0])
			# Delete the copy rule from dictRules
			copy_rhs_tuple = tuple(rule.rhs)
			if copy_rhs_tuple in dict_rules:
				del dict_rules[copy_rhs_tuple]
		else:
			# Update the list of rhs of the nonterminal which is the lhs of the rule
			if rule.lhs in rhs_dict:
				rhs_dict[rule.lhs].append(rule.rhs)
			else:
				rhs_dict[rule.lhs] = [rule.rhs]
	# Compute the transitive closure of renaming derivations
	changed_copy_sets = True
	while changed_copy_sets:
		changed_copy_sets = False
		for n in non_terminals:
			len_copy_set = len(copy[n])
			for copyRhs in copy[n].copy():
				copy[n].update(copy[copyRhs])
			if len_copy_set < len(copy[n]):
				changed_copy_sets = True
	# Update dict_rules by replacing copy rules with their expansion
	for n in non_terminals:
		for copyRhs in copy[n]:
			rhs_dict_copyr_rhs = rhs_dict.get(copyRhs, [])
			for rhs in rhs_dict_copyr_rhs:
				# add the rule to dictRule
				rhs_tuple = tuple(rhs)
				if n not in dict_rules[rhs_tuple]:
					dict_rules[rhs_tuple] = dict_rules[rhs_tuple].union({n})
