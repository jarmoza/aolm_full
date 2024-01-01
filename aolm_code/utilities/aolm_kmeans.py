# Author: Jonathan Armoza
# Creation date: November 7, 2019
# Purpose: Object for K-means clustering and cluster silhouette analysis
# 		   for 'Art of Literary Modeling'

# Based on sample code from https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html

# Scikit-Learn K-means and Cluster silhouette scoring
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.feature_selection import SelectFromModel

# Plotting cluster silhouette scoring
import matplotlib.pyplot as plot
plot.style.use("seaborn-whitegrid")
import matplotlib.cm as cm
import numpy


class AOLM_KMeans:

	def __init__(self, p_data=None, p_data_name=""):

		self.m_data = p_data
		self.m_data_name = p_data_name

		# Default values for unset fields
		self.m_cluster_count = 1
		self.m_random_seed = 10
		self.m_clusterer = None
		self.m_cluster_labels = None


	# Properties 


	@property
	def clusterer(self):
		return self.m_clusterer

	@property
	def cluster_labels(self):
		return self.m_cluster_labels
	
	@property
	def data(self):
		return self.m_data
	@data.setter
	def data(self, p_data):
		self.m_data = p_data

	@property
	def data_name(self):
		return self.m_data_name
	

	@property
	def silhouette_avg(self):
		return self.m_silhouette_avg
	
	@property
	def sample_silhouette_values(self):
		return self.m_sample_silhouette_values
	

	# Primary methods

	def compute_clusters(self, p_cluster_count, p_random_seed=10):

		# Save cluster count as most recent used
		self.m_cluster_count = p_cluster_count

		# Save random seed as record of clustering
		self.m_random_seed = p_random_seed

		# Initialize the clusterer with m_cluster_count value and a random generator 
		# seed of m_random_seed for reproducibility.
		self.m_clusterer = KMeans(n_clusters=self.m_cluster_count, random_state=self.m_random_seed)
		self.m_cluster_labels = self.m_clusterer.fit_predict(self.m_data)

	def compute_silhouettes(self):

	    # The silhouette_score gives the average value for all the samples.
	    # This gives a perspective into the density and separation of the formed clusters.
	    self.m_silhouette_avg = silhouette_score(self.m_data, self.m_cluster_labels)

	    # Compute the silhouette scores for each sample
	    self.m_sample_silhouette_values = silhouette_samples(self.m_data, self.m_cluster_labels)

	def plot(self, p_show=True, p_labels=True):

	    # Create a subplot with 1 row and 2 columns
	    figure, (subplot1, subplot2) = plot.subplots(1, 2)
	    figure.set_size_inches(18, 7)

	    # The 1st subplot is the silhouette plot.
	    # The silhouette coefficient can range from -1, 1
	    subplot1.set_xlim([-1, 1])
	    # The (m_cluster_count + 1) * 10 is for inserting blank space between silhouette
	    # plots of individual clusters, to demarcate them clearly.
	    subplot1.set_ylim([0, len(self.m_data) + (self.m_cluster_count + 1) * 10])

	    y_lower = 10
	    for i in range(self.m_cluster_count):

	        # Aggregate the silhouette scores for samples belonging to cluster i, and sort them
	        ith_cluster_silhouette_values = \
	            self.m_sample_silhouette_values[self.m_cluster_labels == i]

	        ith_cluster_silhouette_values.sort()

	        size_cluster_i = ith_cluster_silhouette_values.shape[0]
	        y_upper = y_lower + size_cluster_i

	        color = cm.nipy_spectral(float(i) / self.m_cluster_count)
	        subplot1.fill_betweenx(numpy.arange(y_lower, y_upper),
	                          0, ith_cluster_silhouette_values,
	                          facecolor=color, edgecolor=color, alpha=0.7)

	        # Label the silhouette plots with their cluster numbers at the middle
	        if p_labels:
	        	subplot1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

	        # Compute the new y_lower for next plot
	        y_lower = y_upper + 10  # 10 for the 0 samples

	    # Silhouette score subplot title and axes labels
	    subplot1.set_title("Silhouette Plot for the Clusters")
	    subplot1.set_xlabel("silhouette coefficient values")
	    subplot1.set_ylabel("cluster label")

	    # The vertical line for average silhouette score of all the values
	    subplot1.axvline(x=self.m_silhouette_avg, color="red", linestyle="--")

	    subplot1.set_yticks([])  # Clear the yaxis labels / ticks
	    subplot1.set_xticks([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])

	    # Second plot showing the actual clusters formed
	    # NOTE: Needs to do a dimension reduction technique prior to this step in order to determine most significant
	    # dimensions (below defaulted to 0 and 1 in self.m_data[:,] - code example presumed a 2D data set)
	    # J. Armoza - 11/9/2019
	    colors = cm.nipy_spectral(self.m_cluster_labels.astype(float) / self.m_cluster_count)
	    subplot2.scatter(self.m_data[:, 0], self.m_data[:, 1], marker=".", s=30, lw=0, alpha=0.7,
	                     c=colors, edgecolor="k")

	    # Labeling the clusters
	    centers = self.m_clusterer.cluster_centers_
	    # Draw white circles at cluster centers
	    subplot2.scatter(centers[:, 0], centers[:, 1], marker="o",
	                     c="white", alpha=1, s=200, edgecolor="k")

	    for i, c in enumerate(centers):
	        subplot2.scatter(c[0], c[1], marker="$%d$" % i, alpha=1,
	                         s=50, edgecolor="k")

	    # Cluster subplot title and axes labels
	    subplot2.set_title("Visualization of the Clustered Data")
	    subplot2.set_xlabel("feature space for the 1st feature")
	    subplot2.set_ylabel("feature space for the 2nd feature")

	    # Overall plot title
	    plot.suptitle("Silhouette Analysis for K-Means Clustering on " + \
	    			  "{0} with {1} Clusters".format(self.m_data_name, self.m_cluster_count),
	    			  fontsize=14, fontweight="bold")

	    if p_show:
	    	plot.show()         


	# Static methods

	@staticmethod
	def compute_cluster_range():

		pass

	@staticmethod
	def plot_cluster_range():

		pass

	@staticmethod
	def plot_bar(p_values, p_bins):

		plot.bar(p_bins, p_values)
		plot.show()		

	@staticmethod
	def plot_silhouette_avg(p_x, p_y, p_x_label="", p_y_label="", p_title=""):

		# 1. Set up the figure and axes
		figure, axes = plot.subplots()
		axes.plot(p_x, p_y)

		# 2. Set styles
		axes.set(xlabel=p_x_label, ylabel=p_y_label, title=p_title)
		axes.grid()

		# Plot the graph
		# figure.savefig("test.png")
		plot.show()		




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
