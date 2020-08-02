import requests
from bs4 import BeautifulSoup
import networkx as nx
import json

pages = 100
cleaned_tags_list = []
tag = 'android' #given tag 

def scrape_tags(url, cleaned_tags_list):
    '''
    function to scrape from stackoverflow and separate tags from rest of data
    url : url of the stackoverflow page to be scraped using stackexchange api
    cleaned_tags_list : list where the final version of tags are to be stored 
    
    '''
    req = requests.get(url)  
    html_doc = req.text 
    soup = BeautifulSoup(html_doc, 'lxml')
    paragraph = soup.find_all('p')       #finding the content within all of the paragraph 
    string = str(paragraph)               #converting it to string to work with
    tag_split = string.split('tags')    
    tag_list = []                  #list to store the tags
    for i in range(1,len(tag_split)):
        tags = tag_split[i].split('owner')[0][2:-2]
        tag_list.append(tags)
    clean_tags(tag_list, cleaned_tags_list)
    
def clean_tags(tags_list, cleaned_tags_list):
    '''
    function to clean the tags 
    tags_list : contains the uncleaned version of tags
    cleaned_tags_list : list where the final version of tags are to be stored 
    
    '''
    for tags in tag_list:
        tags = tags.split(',')
        temp_list = [] #a temporary list to store cleaned tags
        for tag in tags:
            temp_list.append(tag.replace('"','').replace('[','').replace(']',''))
        cleaned_tags_list.append(temp_list)
        

#scrapping stackoverflow and seprating tags         
for page in range(1,101):
    url = 'https://api.stackexchange.com/2.2/questions?page='+str(page)+'&pagesize=100&order=desc&sort=activity&site=stackoverflow'
    scrape_tags(url, cleaned_tags_list)

#creating a weighted graph using the tags     
tag_graph = nx.Graph()
for tag_list in cleaned_tags_list:
    #if there is only one tag in the list add it to the node if it is not already present
    if len(tag_list) == 1: 
        if tag_list[0] not in list(tag_graph.nodes()):
                tag_graph.add_node(tag_list[0])
    else:    
        while(len(tag_list)>1):
            tag = tag_list.pop(0) #taking a tag
            if tag not in list(tag_graph.nodes()): #checking if the tag is already present in the graph
                tag_graph.add_node(tag) #adding the tag as a node
            for temp_tag in tag_list:   #taking the remaining tags 
                if (tag, temp_tag) not in tag_graph.edges([tag]): #checking if there is already a edge present between the two tags
                    tag_graph.add_edge(tag,temp_tag,weight=1) #adding an edge initialized with weight 1
                else: #if there is already an edge present
                    tag_graph[tag][temp_tag]['weight'] += 1 #increamenting the weight
        if tag_list[0] not in list(tag_graph.nodes()): #adding the last node in the current list to the graph if already not present
                tag_graph.add_node(tag_list[0])


#uncomment this to get related tags  directly using the graph 
# max_related_tags =10 #number of related tags to return
# edges_from_tag = [x[1] for x in list(tag_graph.edges(tag))] #list of all the tags which have an edge to the given tag
# weights = [(edge_tag , tag_graph[tag][edge_tag]['weight']) for edge_tag in edges_from_tag] #getting the weights for each tag pair
# sorted_weight_tag = sorted(weights , key = lambda x:x[1] , reverse = True) #sorting the weights in decreasing order
# top_related_tags = [x[0] for x in sorted_weight_tag] #getting the realted tags based on the weights
# print(top_related_tags[:max_related_tags])

#storing the graph in a dictonary to reuse the graph
serialized_graph = nx.readwrite.json_graph.node_link_data(tag_graph)

#nodes is a list of all the nodes in the graph
nodes = serialized_graph['nodes']

#edges is a list of all the edges in the graph
edges  = serialized_graph['links']

#storing the nodes in a text file
with open('nodes.txt', 'w') as outfile:
    json.dump(edges, outfile)

#storing the edges in a text file
with open('edges.txt', 'w') as outfile:
    json.dump(edges, outfile)

#function used in app.py to get related tags
def related_tags(edges_list, tag):
    '''
    function to get related tags
    edges_list : contains all the edges from the graph
    tag : given tag
    '''
    max_related_tags = 10
    tag_weight = []
    for edge in edges_list:
        if edge['source'] == tag:
            temp = []
            temp.append(edge['target'])
            temp.append(edge['weight'])
            tag_weight.append(temp)
        elif edge['target'] == tag:
            temp = []
            temp.append(edge['source'])
            temp.append(edge['weight'])
            tag_weight.append(temp)    
    sorted_weight_tag = sorted(tag_weight , key = lambda x:x[1] , reverse = True) #sorting the weights in decreasing order
    top_related_tags_list = [x[0] for x in sorted_weight_tag] #getting the realted tags based on the weights
    if len(top_related_tags_list) < max_related_tags:
        return top_related_tags_list
    else:
        return top_related_tags_list[:max_related_tags]
