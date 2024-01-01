# Author: Jonathan Armoza
# Creation date: November 7, 2019
# Purpose: Basic k-means clustering of a sub-corpus of Dickinson works and 
#		   cluster silhouette analysis to determine the ideal 'k' (# of clusters)

# Based on sample code from https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html

# Results: December 6 2019
# Silhouette averages: [['10', '20', '30', '40', '50', '60', '70', '80', '90', '100'], 
# [-0.11374733236410478, 0.04283633839921078, 0.03812123751301266, 0.054766875884586744, -0.15948265839704626, 0.037725340483895635, -0.14020624731373976, 0.0015470892480297347, -0.0915948975263426, 0.024669807505612533]]

# NEXT THOUGHT: Increment cluster count by 1 to have a more continous plot of silhouette averages

# NEXT NEXT THOUGH: Use Burrow's Delta in the model

# File system functionality
import glob
import os

# Frequency vector trimming
from statistics import stdev
from statistics import mean
from math import ceil

import my_logging # Debug log messages and pretty debug printing of loops
from my_logging import logging
from my_logging import tqdm
debug = logging.debug
# logging.disable(logging.DEBUG) # Comment out to enable debug messages

# Disables matplotlib debug logging
mpl_logger = logging.getLogger("matplotlib")
mpl_logger.setLevel(logging.WARNING)

# ndarray data type
import numpy

# tf-idf sparse matrix construction
from sklearn.feature_extraction.text import TfidfTransformer

# KMeans, silhouette, and plotting for 'Art of Literary Modeling' scripts
from aolm_kmeans import AOLM_KMeans

# DickinsonPoem object
from dickinson_poem import DickinsonPoem

# Path to all Dickinson sub-corpora
corpora_paths = {

	"franklin": "{0}{1}output{1}franklin_a{1}".format(os.getcwd(), os.sep)
}
corpora_descriptions = {
	
	"debug": "500 works from 'Poems of Emily Dickinson', ed. R.W. Franklin",
	"franklin": "1789 works from 'Poems of Emily Dickinson', ed. R.W. Franklin"
}

def debug_set_and_proposal(p_poems):
	return [25, 50, 75, 100], p_poems[0:500]

def debug_ideal_set_and_proposal(p_poems):
	return [40], p_poems

def fascicles_set_and_proposal(p_poems):
	return [10, 20, 30, 40, 50, 60, 70, 80, 90, 100], p_poems

def increment_by_one_set_and_proposal(p_poems):
	return list(range(2, 101)), p_poems

def increment_by_one_till_20_proposal(p_poems):
	return list(range(21, 41)), p_poems


def get_all_poems(p_path):

	# 1. Get all TEI filenames
	debug("Gathering filenames....")
	filepaths = [tei_filepath for tei_filepath in glob.glob(p_path + "*")]
	
	# 2. Build poem objects
	poems = []
	debug("Building {0} poems in memory....".format(len(filepaths)))	
	for tei_filepath in tqdm(filepaths):
		poems.append(DickinsonPoem(tei_filepath))

	return poems

def get_tfidf_matrix(p_bow_vectors):

	# See https://scikit-learn.org/stable/modules/feature_extraction.html

	# 1. Build list of simple vectors for tf-idf transformer

	# a. Get an alphabetically-ordered list of all words
	all_words = [word_tuple[0] for word_tuple in p_bow_vectors[0]]
	all_words.sort()

	# b. Build a list of counts for each vector
	count_vectors = []
	for bv in p_bow_vectors:
		bv_dict = { word_tuple[0]: word_tuple[1] for word_tuple in bv }
		new_cv = []
		for word in all_words:
			new_cv.append(bv_dict[word] if word in bv_dict else 0)
		count_vectors.append(new_cv)

	# 2. Create the tf-idf transformer and fit a new sparse matrix by tf-idf
	transformer = TfidfTransformer(smooth_idf=True)
	tfidf = transformer.fit_transform(count_vectors)

	return tfidf.toarray()

def trim_least_popular_words(p_bow_vectors, p_corpora_name, p_standard_deviations=1):

	# 1. Add up word totals
	debug("Calculating word frequency totals....")
	all_words_vector = { word_tuple[0]: 0 for word_tuple in p_bow_vectors[0] }
	for bow_vector in tqdm(p_bow_vectors):
		for word_tuple in bow_vector:
			all_words_vector[word_tuple[0]] += word_tuple[1]

	# 2. Calculate the word frequency from which to trim higher (less frequent) frequencies
	collection_tail_cutoff = mean(all_words_vector.values())
	collection_tail_cutoff += (p_standard_deviations * stdev(all_words_vector.values()))
	collection_tail_cutoff = ceil(collection_tail_cutoff)

	# 3. Sort words by frequency ascending
	debug("Sorting words by frequency....")
	all_words_freq_list = [(word, all_words_vector[word]) for word in all_words_vector]
	all_words_freq_list = sorted(all_words_freq_list, key=lambda x: x[1], reverse=True)
	all_words_freq_list_subset = []
	for word_tuple in all_words_freq_list:
		if 1 <= int(word_tuple[1]) <= collection_tail_cutoff:
			all_words_freq_list_subset.append(word_tuple)

	# # DEBUG - Plot histogram of frequencies
	# freq_dict = {}
	# for vector in p_bow_vectors:
	# 	for word_tuple in vector:
	# 		if 1 <= word_tuple[1] <= collection_tail_cutoff:
	# 			str_freq = str(word_tuple[1])
	# 			if str_freq not in freq_dict:
	# 				freq_dict[str_freq] = 0
	# 			freq_dict[str_freq] += 1
	# freq_dict = { key: freq_dict[key] for key in freq_dict if int(key) >= collection_mean }
	# debug(freq_dict)
	# results = list(zip(*freq_dict.items()))
	# # AOLM_KMeans.plot_bar(results[1], [int(r) for r in results[0]])
	# bin_range = numpy.arange(len(results[0]))
	# AOLM_KMeans.plot_bar(results[1], numpy.array(bin_range[1:]))

	# 4. Output to file
	output_filepath = "{0}{1}output{1}top_words{1}dickinson_{2}_corpus_top_{3}_words.csv".format(
		os.getcwd(), os.sep, p_corpora_name, len(all_words_freq_list_subset))
	debug("Outputting word frequency totals to {0}".format(output_filepath))
	with open(output_filepath, "w") as output_file:
		output_file.write("token,count\n")
		for word_tuple in tqdm(all_words_freq_list_subset):
			output_file.write("{0},{1}\n".format(word_tuple[0], word_tuple[1]))

	# 5. Construct new bow vectors based on trimmed list and return
	debug("Creating trimmed BOW vectors for top {0} words....".format(collection_tail_cutoff))
	new_bow_vectors = []
	for bow_vector in tqdm(p_bow_vectors):

		# a. Create a new bow vector for each poem consisting only of the top N words
		# and their per poem frequency
		new_vector = []
		bow_vector_dict = DickinsonPoem.bow_vector_from_bow_tuple_list(bow_vector)
		for word_tuple in all_words_freq_list_subset:
			new_vector.append([word_tuple[0], bow_vector_dict[word_tuple[0]]])

		# b. Sort each new vector by token
		new_vector = sorted(new_vector, key=lambda x: x[0])

		# c. Add the new bow vector to the trimmed list
		new_bow_vectors.append(new_vector)

	# print("============= BEGIN NEW BOW VECTOR =============")
	# print("NEW BOW VECTOR: {0}".format(new_bow_vectors[0]))
	# print("============= NEW BOW VECTOR END =============")

	return new_bow_vectors


def main():

	# 1. Get all Franklin poems
	debug("Getting poems....")
	corpora_name = "franklin"
	poems = get_all_poems(corpora_paths[corpora_name])

	# For debug purposes
	show_cluster_silhouette_labels = False
	# cluster_range, poems = debug_set_and_proposal(poems)
	# corpora_name = "debug"
	# cluster_range, poems = fascicles_set_and_proposal(poems)
	# corpora_name = "franklin"
	# cluster_range, poems = debug_ideal_set_and_proposal(poems)
	# corpora_name = "franklin"
	# cluster_range, poems = increment_by_one_set_and_proposal(poems)
	# corpora_name = "franklin"
	cluster_range, poems = increment_by_one_till_20_proposal(poems)
	corpora_name = "franklin"

	# 2. Compute bag of words vectors for each poem with respect to the collection
	debug("Computing bag of words vectors for all poems....")
	collection_bow_vectors = DickinsonPoem.bow_vectors_for_collection(poems)
	debug("Built list of {0} vectors of size {1}".format(len(collection_bow_vectors),
		len(collection_bow_vectors[0])))

	# a. Get a tf-idf matrix weighted away from most frequent terms
	# and toward unique ones
	debug("Creating sparse tf-idf matrix....")
	collection_skl_vectors = get_tfidf_matrix(collection_bow_vectors)

	# a. Trim off less popular words from vectors
	# collection_bow_vectors = trim_least_popular_words(collection_bow_vectors, corpora_name)

	# b. Convert bag of words vectors into numpy 2D ndarray
	# collection_skl_vectors = []
	# for vector in collection_bow_vectors:
	# 	collection_skl_vectors.append([word_tuple[1] for word_tuple in vector])
	# collection_skl_vectors = numpy.array(collection_skl_vectors)

	# 3. Compute clusters, silhouette scoring, and plot results
	debug("Computing clusters and silhouette scores for poems...")
	debug("Proposed cluster counts: {0}".format(cluster_range))
	silhouette_averages = [[],[]]
	silhouette_values = None
	for index in tqdm(range(len(cluster_range))):

		# a. Get an AOLM KMeans object
		kmeans = AOLM_KMeans(p_data=collection_skl_vectors,
							 p_data_name="{0} Emily Dickinson Poems from Franklin (2005)".format(len(poems)))

		# b. Compute clusters for the proposed K
		debug("Computing {0} clusters....".format(cluster_range[index]))
		kmeans.compute_clusters(cluster_range[index])

		# c. Compute the silhouette scores for the clusters
		debug("Computing silhouette scores....")
		kmeans.compute_silhouettes()
		debug("For {0} clusters, the average silhouette_score is: {1}".format(cluster_range[index],
			  		  kmeans.silhouette_avg))

		# d. Results are stored in two index-corresponding lists for future use
		silhouette_averages[0].append(str(cluster_range[index]))
		silhouette_averages[1].append(kmeans.silhouette_avg)

		# e. Save silhouette samples
		silhouette_values = kmeans.sample_silhouette_values

		# d. Plot the silhouette scores if all proposed clustering in the range has been computed
		# if len(cluster_range) - 1 == index:
		# 	debug("Plotting clusters in range {0} and silhouette scoring....".format(cluster_range))
		# kmeans.plot(p_show=(len(cluster_range) - 1 == index), p_labels=show_cluster_silhouette_labels)

	debug("Silhouette averages: {0}".format(silhouette_averages))
	AOLM_KMeans.plot_silhouette_avg(silhouette_averages[0],
									silhouette_averages[1],
									p_x_label="# of clusters", p_y_label="avg. distance from cluster center [-1,1]",
									p_title="Cluster Silhouettes for {0}".format(corpora_descriptions[corpora_name]))
	debug("Silhouette values: {0}".format(silhouette_values))


if "__main__" == __name__:
	main()

# Silhouette averages for clustering 2-100 for all Franklin Dickinson poems
# [['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99'], [0.25970768530036786, 0.23122432732000409, 0.17533155743154494, 0.2985153862108263, 0.03036999531024929, 0.09519867410773498, 0.13930606193249562, 0.018355358024758232, -0.11374733236410478, 0.08618937741306813, -0.12087813154702781, 0.0037221800558822453, 0.037277415188894804, 0.07399291049936702, -0.01556132989984339, 0.036376289681786834, -0.11871823776924657, -0.0794529609515209, 0.04283633839921078, 0.03746287106828372, -0.027482408994862182, -0.07868462694615638, 0.07856147715066471, -0.12123652908803693, -0.06148396765512319, -0.05513412544563201, 0.009750285218535883, 0.006221074599807021, 0.03812123751301266, -0.04169719365644167, -0.022548116341248453, -0.032509714435754435, 0.014026322666353333, 0.06679151663846515, -0.04137315738894273, 0.02033000098860571, 0.10359733643136985, -0.14197414412360243, 0.054766875884586744, 0.03738930347951878, -0.1912192185056771, -0.0009522402598574985, 0.04685962205841711, -0.036498558675688395, -0.08911038089401611, -0.07496257919706911, -0.0048307610443298855, 0.0878221329479227, -0.15948265839704626, -0.04376653428266033, -0.05503785736375669, -0.1595590094388004, 0.016363083188228458, -0.01454606569991477, 0.045958425058980616, -0.04961194153010782, 0.02363886576484678, -0.02321839472311393, 0.037725340483895635, 0.050110584452997244, -0.044091259873539186, -0.1621744440196456, 0.09848774373030919, -0.009032372797986184, -0.010466381079235518, 0.018397390589537554, -0.13594873114309755, 0.05449777081381862, -0.14020624731373976, -0.0752134308085563, 0.025957733305123555, -0.007074209748090163, -0.1532025932192897, -0.18200714648867353, -0.0005079277817516465, -0.010190582873633768, 0.06998176539851159, 0.001334990287095847, 0.0015470892480297347, -0.10078149672804458, 0.04407132674533249, 0.014038510407220336, -0.09128556122908871, -0.08516911749163729, -0.08478800363716842, -0.07125727804239569, 0.021547046025195627, 0.06345873902669172, -0.0915948975263426, -0.1387738935546896, -0.0562418557227869, 0.03422785969528971, -0.17964994467446524, -0.01401112742518377, 0.0635124261608846, 0.027309019935965493, -0.03944637831591521, -0.005589944859729828]]

# ================================================================================


# from sklearn.datasets import make_blobs
# from sklearn.cluster import KMeans
# from sklearn.metrics import silhouette_samples, silhouette_score

# import matplotlib.pyplot as plt
# import matplotlib.cm as cm
# import numpy as np

# print(__doc__)

# # Generating the sample data from make_blobs
# # This particular setting has one distinct cluster and 3 clusters placed close
# # together.
# X, y = make_blobs(n_samples=500,
#                   n_features=2,
#                   centers=4,
#                   cluster_std=1,
#                   center_box=(-10.0, 10.0),
#                   shuffle=True,
#                   random_state=1)  # For reproducibility

# range_n_clusters = [2, 3, 4, 5, 6]

# for n_clusters in range_n_clusters:
#     # Create a subplot with 1 row and 2 columns
#     fig, (ax1, ax2) = plt.subplots(1, 2)
#     fig.set_size_inches(18, 7)

#     # The 1st subplot is the silhouette plot
#     # The silhouette coefficient can range from -1, 1 but in this example all
#     # lie within [-0.1, 1]
#     ax1.set_xlim([-0.1, 1])
#     # The (n_clusters+1)*10 is for inserting blank space between silhouette
#     # plots of individual clusters, to demarcate them clearly.
#     ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

#     # Initialize the clusterer with n_clusters value and a random generator
#     # seed of 10 for reproducibility.
#     clusterer = KMeans(n_clusters=n_clusters, random_state=10)
#     cluster_labels = clusterer.fit_predict(X)

#     # The silhouette_score gives the average value for all the samples.
#     # This gives a perspective into the density and separation of the formed
#     # clusters
#     silhouette_avg = silhouette_score(X, cluster_labels)
#     print("For n_clusters =", n_clusters,
#           "The average silhouette_score is :", silhouette_avg)

#     # Compute the silhouette scores for each sample
#     sample_silhouette_values = silhouette_samples(X, cluster_labels)

#     y_lower = 10
#     for i in range(n_clusters):
#         # Aggregate the silhouette scores for samples belonging to
#         # cluster i, and sort them
#         ith_cluster_silhouette_values = \
#             sample_silhouette_values[cluster_labels == i]

#         ith_cluster_silhouette_values.sort()

#         size_cluster_i = ith_cluster_silhouette_values.shape[0]
#         y_upper = y_lower + size_cluster_i

#         color = cm.nipy_spectral(float(i) / n_clusters)
#         ax1.fill_betweenx(np.arange(y_lower, y_upper),
#                           0, ith_cluster_silhouette_values,
#                           facecolor=color, edgecolor=color, alpha=0.7)

#         # Label the silhouette plots with their cluster numbers at the middle
#         ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

#         # Compute the new y_lower for next plot
#         y_lower = y_upper + 10  # 10 for the 0 samples

#     ax1.set_title("The silhouette plot for the various clusters.")
#     ax1.set_xlabel("The silhouette coefficient values")
#     ax1.set_ylabel("Cluster label")

#     # The vertical line for average silhouette score of all the values
#     ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

#     ax1.set_yticks([])  # Clear the yaxis labels / ticks
#     ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

#     # 2nd Plot showing the actual clusters formed
#     colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
#     ax2.scatter(X[:, 0], X[:, 1], marker='.', s=30, lw=0, alpha=0.7,
#                 c=colors, edgecolor='k')

#     # Labeling the clusters
#     centers = clusterer.cluster_centers_
#     # Draw white circles at cluster centers
#     ax2.scatter(centers[:, 0], centers[:, 1], marker='o',
#                 c="white", alpha=1, s=200, edgecolor='k')

#     for i, c in enumerate(centers):
#         ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1,
#                     s=50, edgecolor='k')

#     ax2.set_title("The visualization of the clustered data.")
#     ax2.set_xlabel("Feature space for the 1st feature")
#     ax2.set_ylabel("Feature space for the 2nd feature")

#     plt.suptitle(("Silhouette analysis for KMeans clustering on sample data "
#                   "with n_clusters = %d" % n_clusters),
#                  fontsize=14, fontweight='bold')

# plt.show()