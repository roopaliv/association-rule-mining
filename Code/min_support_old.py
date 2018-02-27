'''
Created on Sep 21, 2017
@author: Roopali Vij
'''

import pandas as pd
from itertools import combinations, chain


RULE = "RULE"
BODY = "BODY"
HEAD = "HEAD"
ANY = "ANY"
NONE = "NONE"
AND = "and"
OR = "or"

def preprocess_data(file_path):
	df = pd.read_table(file_path, delimiter='\t', header = None)
	columns = []
	for i in range(len(df.columns)-1):
		columns.append('G'+ str(i+1))
		df[df.columns[i]] = 'G'+ str(i+1) + '_'+ df[df.columns[i]]
	columns.append('Diagnosis')
	df.columns = columns
	return df

def get_support_count(minimum_support, total_transactions):
	support_count = minimum_support * total_transactions
	return support_count

def get_transactions(data_frame):
    transaction_list = list()
    for index, row in data_frame.iterrows():
        transaction = frozenset(row)
        transaction_list.append(transaction)
    return transaction_list

def get_len_one_item_set(data_frame):
	first_item_set = set()
	for col in data_frame.columns:
		for item in list(data_frame[col].unique()):
			first_item_set.add(frozenset([item]))
	return first_item_set

def get_current_count(item_set, transaction_list, track_transactions):
	current_track = {}
	for item in item_set:
		for transaction in transaction_list:
			if item.issubset(transaction):
				track_transactions[item] = track_transactions.get(item, 0) + 1
				current_track[item] = current_track.get(item, 0) + 1
	return current_track

def purge_items_less_than_min(current_track, support_count):
	new_item_set = set()
	for item, count in current_track.items():
		if count >= support_count:
			new_item_set.add(item)
	return new_item_set

def create_next_itemset(item_set, k):
	new_set = set([i.union(j) for i in item_set for j in item_set if len(i.union(j)) == k])
	return new_set

def get_all_item_sets(minimum_support, transaction_list,item_set):
	print('Support is set to be '+ str(int(minimum_support*100))+'%')
	support_count = get_support_count(minimum_support, len(transaction_list))
	track_transactions = {}
	all_items = {}
	#keep track of total
	total_count = 0

	#prune for first item set -> length or k = 1 in nCk
	k = 1
	current_track = get_current_count(item_set, transaction_list, track_transactions)
	pruned_set = purge_items_less_than_min(current_track, support_count)
	total_count += len(pruned_set)
	all_items[k] = pruned_set
	print('number of length-' + str(k) + ' frequent itensets: ' + str(total_count))

	k += 1

	while len(pruned_set):
		pruned_set = create_next_itemset(pruned_set, k)
		current_track = get_current_count(pruned_set, transaction_list, track_transactions)
		pruned_set = purge_items_less_than_min(current_track, support_count)
		total_count += len(pruned_set)
		if len(pruned_set):
			all_items[k] = pruned_set
			print('number of length-' + str(k) + ' frequent itemsets:' + str(len(pruned_set)))
		k += 1
	print('number of all lengths frequent itemsets:' + str(total_count))
	return all_items, track_transactions

def get_rules(support, confidence, total_transactions, track_transactions, all_items):
	rules = []
	for k, v in all_items.items():
		for item in v:
			for head in map(frozenset, [a for a in (chain(*[combinations(item, i + 1) for i, a in enumerate(item)]))]):
				body = item.difference(head)
				if len(body):
					if (float(track_transactions[item]))/(float(track_transactions[head])) >= confidence:
						rules.append((set(head), set(body)))
	return rules

def get_queries():
	template_1_queries = []
	template_2_queries = []
	template_3_queries = []

	template_1_queries.append(("RULE", "ANY", ['G59_Up']))
	template_1_queries.append(("RULE", "NONE", ['G59_Up']))
	template_1_queries.append(("RULE", 1, ['G59_Up', 'G10_Down']))
	template_1_queries.append(("BODY", "ANY", ['G59_Up']))
	template_1_queries.append(("BODY", "NONE", ['G59_Up']))
	template_1_queries.append(("BODY", 1, ['G59_Up', 'G10_Down']))
	template_1_queries.append(("HEAD", "ANY", ['G59_Up']))
	template_1_queries.append(("HEAD", "NONE", ['G59_Up']))
	template_1_queries.append(("HEAD", 1, ['G59_Up', 'G10_Down']))

	template_2_queries.append(("RULE", 3))
	template_2_queries.append(("BODY", 2))
	template_2_queries.append(("HEAD", 1))

	template_3_queries.append(("1or1", ("BODY", "ANY", ['G10_Down']), ("HEAD", 1, ['G59_Up'])))
	template_3_queries.append(("1and1", ( "BODY", "ANY",['G10_Down']), ("HEAD", 1, ['G59_Up'])))
	template_3_queries.append(("1or2", ("BODY", "ANY", ['G10_Down']), ("HEAD", 2)))
	template_3_queries.append(("1and2", ("BODY", "ANY",['G10_Down']), ("HEAD", 2)))
	template_3_queries.append(("2or2", ("BODY", 1), ( "HEAD", 2)))
	template_3_queries.append(("2and2", ( "BODY", 1), ("HEAD", 2)))

	return template_1_queries ,template_2_queries, template_3_queries

def get_rule_size(item, check_head, check_body):
	total_rule_size = 0
	if check_head:
		total_rule_size += len(item[1])
	if check_body:
		total_rule_size += len(item[0])
	return total_rule_size

def answer_template_1_query(query, rules):
	check_body = True
	check_head = True
	check = query[0]
	if check == BODY:
		check_head = False
	elif check == HEAD:
		check_body = False
	operator = query[1]
	items_match_list = query[2]
	results = []
	for item in rules:
		remaining_set = set()
		total_item = set()
		if check_head:
			total_item = item[1] 
		if check_body:
			total_item = total_item.union(item[0])
		remaining_set = total_item - set(items_match_list)
		total_rule_size = get_rule_size(item, check_head, check_body)
		len_remainung_items = len(remaining_set)
		if operator == ANY and total_rule_size > len_remainung_items:
			results.append(item)
		elif operator == NONE and total_rule_size == len_remainung_items:
			results.append(item)
		elif operator == 1 and total_rule_size - len_remainung_items == 1:
			results.append(item)
	return results


def answer_template_1_queries(template_1_queries, rules):
	all_results = []
	for query in template_1_queries:
		results = answer_template_1_query(query, rules)
		all_results.append(results)
	return all_results

def answer_template_2_query(query, rules):
	check_body = True
	check_head = True
	check = query[0]
	if check == BODY:
		check_head = False
	elif check == HEAD:
		check_body = False
	size = query[1]
	results = []
	for item in rules:
		total_rule_size = get_rule_size(item, check_head, check_body)
		if total_rule_size >= size:
			results.append(item)
	return results

def answer_template_2_queries(template_2_queries, rules):
	all_results = []
	for query in template_2_queries:
		results = answer_template_2_query(query, rules)
		all_results.append(results)
	return all_results

def answer_template_3_query(query, rules):
	info = query[0]
	first_query_type = info[0]
	operation = info[1:-1]
	second_query_type = info[-1:]
	query_1 = query[1]
	query_2 = query[2]
	if first_query_type == '1':
		results_1 = answer_template_1_query(query_1, rules)
	else:
		results_1 = answer_template_2_query(query_1, rules)

	if second_query_type == '1':
		results_2 = answer_template_1_query(query_2, rules)
	else:
		results_2 = answer_template_2_query(query_2, rules)
	if operation == AND:
		results =  [e for e in results_2 if e in results_1]
	else: #union
		results =  results_1 + [e for e in results_2 if e not in results_1]
	 
	
	return results

def answer_template_3_queries(template_3_queries, rules):
	all_results = []
	for query in template_3_queries:
		results = answer_template_3_query(query, rules)
		all_results.append(results)
	return all_results

if __name__ == "__main__":

	#get data frame
	file_path = 'associationruletestdata.txt'
	data_frame = preprocess_data(file_path)

	#get transactions and first item set
	transaction_list = get_transactions(data_frame)
	item_set = get_len_one_item_set(data_frame)
	
	print('##############################')
	print('###### PART 1 Begins #########')
	print('##############################')
	#get item count for various supports
	minimum_support_list = [0.3, 0.4, 0.5, 0.6, 0.7]
	for minimum_support in minimum_support_list:
		get_all_item_sets(minimum_support, transaction_list,item_set)
	
	print('##############################')
	print('###### PART 2 Begins #########')
	print('##############################')

	#get rules for support = 50 and confidence = 70
	support = 0.5
	confidence = 0.7
	all_items, track_transactions = get_all_item_sets(support, transaction_list, item_set)
	rules = get_rules(support, confidence , len(transaction_list), track_transactions, all_items)
	
	'''print('###### All rules #########')
	for item in rules:
		print(str(item[0]) + "==>" + str(item[1]))'''	


	template_1_queries ,template_2_queries, template_3_queries = get_queries()
	
	print('###### Template 1 queries #########')
	results_template_1 = answer_template_1_queries(template_1_queries, rules)
	i = 0
	for value in results_template_1:
		print('Starting results for query: ' + str(template_1_queries[i]) + " count:" + str(len(value)))
		'''for item in value:
			print(str(item[0]) + "==>" + str(item[1]))
		print('Ending results for query: ' + str(template_1_queries[i]) + " count:" + str(len(value)))
		'''
		i+=1

	print('###### Template 2 queries #########')
	results_template_2 = answer_template_2_queries(template_2_queries, rules)
	i = 0
	for value in results_template_2:
		print('Starting results for query: ' + str(template_2_queries[i]) + " count:" + str(len(value)))
		'''for item in value:
			print(str(item[0]) + "==>" + str(item[1]))
		print('Ending results for query: ' + str(template_2_queries[i]) + " count:" + str(len(value)))
		'''
		i+=1

	print('###### Template 3 queries #########')
	results_template_3 = answer_template_3_queries(template_3_queries, rules)
	i = 0
	for value in results_template_3:
		print('Starting results for query: ' + str(template_3_queries[i]) + " count:" + str(len(value)))
		'''for item in value:
			print(str(item[0]) + "==>" + str(item[1]))
		print('Ending results for query: ' + str(template_3_queries[i]) + " count:" + str(len(value)))
		'''
		i+=1

	