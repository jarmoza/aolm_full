import json
import os

import plotly.plotly as py
import plotly.graph_objs as go

def main():

	# Open file
	with open(os.getcwd() + "/volumes_by_date.json", "rU") as input_file:
		json_data = json.loads(input_file.read())

	# Sort data for graphing
	graph_data = []
	for year in json_data:
		graph_data.append((year, json_data[year]))
	graph_data = sorted(graph_data, key=lambda x:x[0], reverse=False)

	# Create plot format object
	data = [go.Bar( \
			x=[year_tuple[0] for year_tuple in graph_data], \
			y=[year_tuple[1] for year_tuple in graph_data]) \
			]

	# Plot data
	py.plot(data, filename="hathi_subset_books_by_year")

if "__main__" == __name__:
	main()