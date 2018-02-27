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

def get_current_count(item_set, transaction_list, support_count):
	current_track = {}
	for item in item_set:
		for transaction in transaction_list:
			if item.issubset(transaction):
				count_current = current_track.get(item, 0) + 1
				current_track[item] = count_current
				if count_current >= support_count:
					break;
	return current_track

def purge_items_less_than_min(current_track, support_count):
	new_item_set = set()
	for item, count in current_track.items():
		if count >= support_count:
			new_item_set.add(item)
	return new_item_set

def create_next_itemset(item_set, k):
	new_set = set([i.union(j) for i in item_set for j in item_set if len(i.union(j)) == k])
	for i
	return new_set

def get_all_item_sets(minimum_support, transaction_list,item_set):
	print('Support is set to be '+ str(int(minimum_support*100))+'%')
	support_count = get_support_count(minimum_support, len(transaction_list))
	#keep track of total
	total_count = 0

	#prune for first item set -> length or k = 1 in nCk
	k = 1
	current_track = get_current_count(item_set, transaction_list, support_count)
	pruned_set = purge_items_less_than_min(current_track, support_count)
	total_count += len(pruned_set)
	print('number of length-' + str(k) + ' frequent itensets: ' + str(total_count))

	k += 1

	while len(pruned_set):
		pruned_set = create_next_itemset(pruned_set, k)
		current_track = get_current_count(pruned_set, transaction_list, support_count)
		pruned_set = purge_items_less_than_min(current_track, support_count)
		total_count += len(pruned_set)
		if len(pruned_set):
			print('number of length-' + str(k) + ' frequent itemsets:' + str(len(pruned_set)))
		k += 1
	print('number of all lengths frequent itemsets:' + str(total_count))


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

	