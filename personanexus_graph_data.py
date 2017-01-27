import networkx as nx
import matplotlib.pyplot as plt
import collections
import random
import graphviz as gv
import functools
from pymongo import MongoClient
client = MongoClient(host='mongodb://austinc:apobianco@ds037244.mongolab.com:37244/personanexus', port=37244)
db = client['personanexus']
collection = db['rawVoteData']

import MySQLdb
db=MySQLdb.connect(host="localhost", user="root", passwd="", db="test", port=3306)
mysqlcursor = db.cursor()

import operator

mysqlcursor.execute("""SELECT * FROM plsql;""")
allpersonas = mysqlcursor.fetchall()

mysqlcursor.execute("""SELECT * FROM pglsql;""")
allpersonagroups = mysqlcursor.fetchall()


#initialize dict that holds all personas
personadict = {}

#for each personaID
for persona in allpersonas:
    initialQueryPID = persona[0]
    #print("THIS PERSONA ID:"+str(initialQueryPID))

    #initialize dict that holds all ratios between persona and every other non-similar persona
    PIDdict = {}
    for persona2 in allpersonas:
        #print(persona2[0])
        secondPID = persona2[0]
        #check for similarity TO ELIMINATE SAME GROUP CONNECTIONS
        #if persona[0] != persona2[0] and persona[2] != persona2[2]:
        if persona[2] != persona2[2]:
            
            #find the yesvotes/totalvotes
            cursor = collection.find({"$and": [{"personacombo":initialQueryPID},{"personacombo":secondPID}] }, projection={'yesvotes':1,'totalvotes':1})
            try:
                if cursor.count()>0:
                    for document in cursor:
                    #make sure it contains some voting data and insert ratio into inner dictionary
                        if document['totalvotes'] > 0:
                            ratio = document['yesvotes']/document['totalvotes']
                            PIDdict[secondPID] = ratio-0.5
                else:
                    PIDdict[secondPID] = 0.0
                #print(PIDdict)
            except AttributeError:
                PIDdict[secondPID] = 0.0
             #maybe change to find_one to get rid of loop
                #print('totalvotes:'+str(document['totalvotes']))
        else: 
            PIDdict[secondPID] = 0.0
                

                
        #add inner dictionary for this persona into outer dictionary
        #USE persona[1] FOR PERSONA NAME, USE persona[0] FOR ACTUAL GRAPHING
        #$$$$personadict[persona[1]] = PIDdict
        
        personadict[persona[0]] = PIDdict

                #dict.items instead of dict.iteritems cause python 3
                #else: print(max(PIDdict.items(), key=operator.itemgetter(1))[0])

print(personadict)

with open("pnetdata.txt", "w+") as out_file:
    out_file.write(str(personadict))






personalist_bygroups = []

for group in allpersonagroups:
    print(group)
    grouplist=[]
    for persona in allpersonas:
        GID = group[0]
        #for each personaID in the group
        # print(GID)
        # print(persona)
        if GID == persona[2]:
            initialQueryPID = persona[0]
            #initialize dict that holds all ratios between persona and every other non-similar persona
            GIDlist = []
            for persona2 in allpersonas:
                #print(persona2[0])
                secondPID = persona2[0]
                if persona[2] != persona2[2]:
                    #find the yesvotes/totalvotes
                    cursor = collection.find({"$and": [{"personacombo":initialQueryPID},{"personacombo":secondPID}] }, projection={'yesvotes':1,'totalvotes':1})
                    try:
                        if cursor.count()>0:
                            for document in cursor:
                            #make sure it contains some voting data and insert ratio into inner dictionary
                                if document['totalvotes'] > 0:
                                    ratio = document['yesvotes']/document['totalvotes']
                                    GIDlist += [ratio-0.5]
                        else:
                            GIDlist += [0.0]
                    except AttributeError:
                        GIDlist += [0.0]
                else: 
                    GIDlist += [0.0]
                #print(GIDlist)

            grouplist += [GIDlist]
    personalist_bygroups += [grouplist]


print(personalist_bygroups)

with open("pnetdata_bygroups.txt", "w+") as out_file:
    out_file.write(str(personalist_bygroups))


#using personadict, take persona IDs from the same group and cluster into a polygon
#draw a line from each persona ID "vertex" to all the ones on other shapes (in other groups)
#make line vary in thickness based on how high the ratio is
#hide even line but the biggest for each connection to each group (so each persona has one line going to another group)

#G=nx.DiGraph()

personalabels=collections.OrderedDict()
for persona in allpersonas:
    personalabels[persona[0]] = persona[1]

# personanodes = [x for x in range(1,18)]

personanodes = []
templist=[]


next = None

for index, persona in enumerate(allpersonas):
    try:
        next = allpersonas[index + 1]
        if persona[2] == next[2]:
            templist += [persona[0]]
        else:
            templist += [persona[0]]
            personanodes += [templist]
            templist = []
    except IndexError:
        templist += [persona[0]]
        personanodes += [templist]
        break

print("node clusters: " + str(personanodes))


# G = gv.Graph(format='png')

#graph = functools.partial(gv.Graph, format='svg')
#digraph = functools.partial(gv.Digraph, format='svg')

#G=nx.Graph()

# allnodes = [node for nodecluster in personanodes for node in nodecluster]
# print(allnodes)

# colorcodes = []
# for nodecluster in personanodes:
#     colorcode = '#'
#     colorcode += ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
#     print(colorcode)
#     colorcodes += colorcodes
#     for i,nodenum in enumerate(nodecluster):
#         G.node(str(nodenum), fillcolor=colorcode, clusterrank=str(i))
#         #G.node[1]['fillcolor']= colorcode
#     #G.add_nodes_from(nodecluster, color=colorcode)
    




def weight_to_color(weight):
    color_base = '#0000'
    weight = int(255*weight)
    #print(weight)
    val = hex(weight)[2:] # returns something like '0x15', so we remove the '0x'
    #print(val)
    val = "0"+val if len(val)<2 else val # make sure 2 digits
    return color_base+val

    
# edges = []
# for persona in allpersonas:
#     for persona2 in allpersonas:
#         #tuple=(,)
#         personaID, persona2ID = persona[0], persona2[0]
#         tupleID=()
#         tupleID = (personaID,persona2ID)
#         if tupleID not in edges and persona[2] != persona2[2]:
#             #print(personaID, persona2ID)
#             tupleID = (personaID,persona2ID)
#             print(personadict[personaID])
#             try:
#                 weight=personadict[personaID][persona2ID]
#                 print(weight)
#                 #print(personadict[personaID][persona2ID])
#                 #G.add_edge(personaID, persona2ID, weight=personadict[personaID][persona2ID])  #NO GRAPHWIZ
#                 G.edge(str(personaID), str(persona2ID), color=weight_to_color(weight))   #GRAPHWIZ
#                 edges.append(tupleID)
#             except KeyError:
#                 #print("0.01")
#                 #G.add_edge(personaID, persona2ID, weight=0.01)  #NO GRAPHWIZ
#                 G.edge(str(personaID), str(persona2ID), color=weight_to_color(0.01))   #GRAPHWIZ
#                 edges.append(tupleID)

# # use one of the edge properties to control line thickness
# #strength = [ d['weight'] for (u,v,d) in G.edges(data=True)]   #NO GRAPHWIZ


# G.render('G')

# print("edges:")
# print(edges)

# print("Labels:")
# print(dict(personalabels))



#G=nx.path_graph(18)
#G.add_nodes_from(personanodes)
#G=nx.relabel_nodes(G,personalabels)

#G.add_edges_from(edges)
#print("Nodes of graph: ")
#print(G.nodes())
# print("Edges of graph: ")
# print(H.edges())

# pos = {1: (0,0), 2: (0,0), 3: (0,0), 4: (0,0), 5: (0,0), 6: (0,0), 7: (0,0), 8: (0,0), 9: (0,0), 10: (0,0), 11: (0,0), 12: (0,0), 13: (0,0), 14: (0,0), 15: (0,0), 16: (0,0), 17: (0,0), 18: (0,0)}
# 
# pos = {1: (1,1), 2: (1,1), 3: (1,1), 4: (1,1), 5: (1,1), 6: (1,3), 7: (1,3), 8: (4,4), 9: (4,4), 10: (4,4), 11: (4,4), 12: (4,4), 13: (4,1), 14: (4,1), 15: (4,1), 16: (4,1), 17: (5,6), 18: (5,6)}

# pos = {0: (1,1), 1: (1,1), 2: (1,1), 3: (1,1), 4: (1,1), 5: (1,3), 6: (1,3), 7: (4,4), 8: (4,4), 9: (4,4), 10: (4,4), 11: (4,4), 12: (4,1), 13: (4,1), 14: (4,1), 15: (4,1), 16: (5,6), 17: (5,6)}

#pos=nx.spring_layout(G)

#nx.draw_networkx_labels(G, pos, personalabels)
#nx.draw(G)

# nx.draw_networkx(G, pos=pos, node_color=['r','r','r','r','r', 'c','c', 'g','g','g','g','g', 'm','m','m','m', 'y','y'], edge_color=strength,width=4,edge_cmap=plt.cm.Blues,with_labels=False)


# A = nx.to_agraph(G) # uses pygraphviz
# 
# for i,color in enumerate(colorcodes):
#     thesenodes = [n for n,d in G.node.items() if d.get('color')==color]
#     A.add_subgraph(thesenodes, name = i, color=color)


# G.draw('colors.png')

# nx.random_layout(G, dim=2, center=None)


# plt.savefig("simple_path.png")
# plt.show()




















