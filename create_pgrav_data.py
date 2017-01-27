# dicts_from_file = []

# with open('pnetdata.txt', 'r') as f:
# 	for line in f:
# 		dicts_from_file.append(eval(line))


# print(dicts_from_file)

# particles = []

# for minidict in dicts_from_file:

import random as r

lists_from_file = []
with open('pnetdata_bygroups.txt', 'r') as f:
	for line in f:
		lists_from_file.append(eval(line))



longassjsstring = ""
for group in lists_from_file:
	for group_index, lists_of_affinities in enumerate(group):
		for list_of_affinities in lists_of_affinities:
			jsstring = """particles.push({x: screen.width*Math.random(),y: screen.height*Math.random(),group:'#""" + '{0:06X}'.format(group_index*100) +"',masslist:"+ str(list_of_affinities) +"});"
			longassjsstring+=jsstring

print(longassjsstring)

with open("pgrav_data.txt", "w+") as out_file:
    out_file.write(str(longassjsstring))
