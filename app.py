import flask
import requests
from bs4 import BeautifulSoup
import networkx as nx
import json

app = flask.Flask(__name__, template_folder='templates')

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




@app.route('/', methods=['GET', 'POST'])
def main():
	if flask.request.method == 'GET':
		return(flask.render_template('main.html'))
	if flask.request.method == 'POST':
		tag_given = flask.request.form['Tag']
		with open('nodes.txt') as json_file:
			node_dict = json.load(json_file)
		node_list = []
		for node in node_dict:
			node_list.append(node['id'])
		if tag_given not in node_list:
			return flask.render_template('main.html',
                                     original_input={'Given tag':tag_given },
                                     result=['Error : Given tag not present'],
                                     )

		with open('edges.txt') as json_file:
			edge_list = json.load(json_file)

		top_related_tags_list =  related_tags(edge_list,tag_given)
		return flask.render_template('main.html',
                                     original_input={'Given tag':tag_given },
                                     result=top_related_tags_list,
                                     )
if __name__ == '__main__':
    app.run(debug = True)