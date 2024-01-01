# Code from https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html
# "Selecting the number of clusters with silhouette analysis on KMeans clustering"
# Taken on August 10, 2021

from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_samples, silhouette_score

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

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


# Imports

# Built-ins

from collections import Counter
import glob
from math import log10
import os
import string

# Third party

from gensim.models import Word2Vec
import numpy as np


# Globals

data_path = "{0}{1}output{1}twain_autobio{1}".format(os.getcwd(), os.sep)
split_chars = ".?!,:;‚—"
split_chars_ord = [160, 8211, 8216, 8220]
split_chars_ord.extend([ord(ch) for ch in split_chars])
remove_chars_ord = [8221, 9671, 91]
ignore_word_chars_ord = [9674]
substitution_chars_ord = [8214, 124, 8201]
text_count = 0

def contains_non_alpha(p_string):
    return any([not is_alpha(ch) for ch in p_string])
def is_alpha(p_char):
    return p_char.isalpha() and (ord(p_char) >= ord("a") and ord(p_char) <= ord("z"))

def clean_word(p_word):

    # 1. Lowercase and strip the word of immediate outside whitespace
    new_word = p_word.lower().strip()

    # 2. Whittle down the word until it begins and ends with an alphabetic character
    start_alpha = 0
    for index in range(len(new_word)):
        if not is_alpha(new_word[index]):
            start_alpha += 1
            continue
        break
    end_alpha = len(new_word) - 1
    for index in range(len(new_word) - 1, -1, -1):
        if not is_alpha(new_word[index]):
            end_alpha -= 1
            continue
        break
    new_word = new_word[start_alpha:end_alpha + 1]

    # 3. Remove characters from middle of word (special case only)
    for rch in remove_chars_ord:
        if chr(rch) in new_word:
            new_word = new_word.replace(chr(rch), "")

    # 4. Replace characters in middle of word (special case only)
    for sch in substitution_chars_ord:
        if chr(sch) in new_word:
            new_word = new_word.replace(chr(sch), "-")

    # 5. Strip any remaining whitespace
    return new_word.strip()

def filter_nonwords_split(p_string):

    new_parts_list = []
    schar = None

    # 1. Attempt to find first split character
    for ch in p_string:
        if ord(ch) in split_chars_ord:
            schar = ch
            break

    # A. Short-circuit return condition (no split string)
    if None == schar:
        return [p_string]

    # 2. Perform the initial split
    parts = p_string.split(schar)

    # 3. Iterate through each part looking for successive splits
    for p in parts:
        new_parts_list.extend(filter_nonwords_split(p))

    return new_parts_list

def filter_nonwords(p_word_list):

    new_word_list = []

    # 1. Create a new word list based on the following criteria
    for word in p_word_list:

        # Flag to turn off appending after filter conditions have been examined
        ignore_add = False

        # A. Ignore words with digits in them
        if any(ch.isdigit() or ord(ch) in ignore_word_chars_ord for ch in word):
            continue
        # B. Ignore words with just punctuation in them
        elif not any(ch.isalpha() for ch in word):
            continue
        # C. Ignore all one character words except 'a' and 'i'
        elif 1 == len(word) and 'a' != word and 'i' != word:
            continue

        # D. Handle words with punctuation in the middle
        elif any((ch in string.punctuation) or (ord(ch) in split_chars_ord) for ch in word):

            # I. Look for splittable words
            parts_list = filter_nonwords_split(word)

            if 1 == len(parts_list):
                new_word_list.append(clean_word(word))
                continue

            # II. Filter out non-words in parts list
            for part in parts_list:

                # a. Ignore words with digits in them
                if any(nch.isdigit() or ord(nch) in ignore_word_chars_ord for nch in part):
                    continue
                # b. Ignore words with just punctuation in them
                elif not any(nch.isalpha() for nch in part):
                    continue
                # c. Ignore all one character words except 'a' and 'i'
                elif 1 == len(part) and 'a' != part and 'i' != part:
                    continue

                # d. Add each part to the word list as a separate word
                # if contains_non_alpha(part):
                #     print(part)
                new_word_list.append(clean_word(part))

            continue

        if not ignore_add:
            new_word_list.append(clean_word(word))

    return new_word_list

def plot_kmeans_and_silhouette(p_tf_idf_vectors):

    # Do principle component analysis on vectors
    pca = PCA(n_components=2).fit_transform(p_tf_idf_vectors.todense())

    # range_n_clusters = [20, 30, 40, 50, 60]
    range_n_clusters = [3, 6, 9, 12, 15]
    for n_clusters in range_n_clusters:

        # Create a subplot with 1 row and 2 columns
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.set_size_inches(18, 7)

        # The 1st subplot is the silhouette plot
        # The silhouette coefficient can range from -1, 1 but in this example all
        # lie within [-0.1, 1]
        ax1.set_xlim([-0.1, 1])
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        ax1.set_ylim([0, len(pca) + (n_clusters + 1) * 10])

        # Initialize the clusterer with n_clusters value and a random generator
        # seed of 10 for reproducibility.
        # clusterer = AgglomerativeClustering(n_clusters=n_clusters)
        clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        cluster_labels = clusterer.fit_predict(pca)

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed
        # clusters
        silhouette_avg = silhouette_score(pca, cluster_labels)
        print("For n_clusters =", n_clusters,
            "The average silhouette_score is :", silhouette_avg)

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(pca, cluster_labels)

        y_lower = 10
        for i in range(n_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = \
                sample_silhouette_values[cluster_labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(i) / n_clusters)
            ax1.fill_betweenx(np.arange(y_lower, y_upper),
                            0, ith_cluster_silhouette_values,
                            facecolor=color, edgecolor=color, alpha=0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax1.set_title("The silhouette plot for the various clusters.")
        ax1.set_xlabel("The silhouette coefficient values")
        ax1.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax1.set_yticks([])  # Clear the yaxis labels / ticks
        ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

        # 2nd Plot showing the actual clusters formed
        colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
        ax2.scatter([pca[:, 0]], [pca[:, 1]], marker='.', s=30, lw=0, alpha=0.7,
                    c=colors, edgecolor='k')

        # Labeling the clusters
        centers = clusterer.cluster_centers_
        # Draw white circles at cluster centers
        ax2.scatter(centers[:, 0], centers[:, 1], marker='o',
                    c="white", alpha=1, s=200, edgecolor='k')

        for i, c in enumerate(centers):
            ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1,
                        s=50, edgecolor='k')

        ax2.set_title("The visualization of the clustered data.")
        ax2.set_xlabel("Feature space for the 1st feature")
        ax2.set_ylabel("Feature space for the 2nd feature")

        plt.suptitle(("Silhouette analysis for KMeans clustering on sample data "
                    "with n_clusters = %d" % n_clusters),
                    fontsize=14, fontweight='bold')

    plt.show()    

def plot_tsne_pca(data, labels):

    max_label = max(labels)
    max_items = np.random.choice(range(data.shape[0]), size=text_count, replace=False)
    
    pca = PCA(n_components=2).fit_transform(data[max_items,:].todense())
    tsne = TSNE().fit_transform(PCA(n_components=50).fit_transform(data[max_items,:].todense()))
    
    
    idx = np.random.choice(range(pca.shape[0]), size=text_count, replace=False)
    label_subset = labels[max_items]
    label_subset = [cm.hsv(i/max_label) for i in label_subset[idx]]
    
    f, ax = plt.subplots(1, 2, figsize=(14, 6))
    
    ax[0].scatter(pca[idx, 0], pca[idx, 1], c=label_subset)
    ax[0].set_title('PCA Cluster Plot')
    
    ax[1].scatter(tsne[idx, 0], tsne[idx, 1], c=label_subset)
    ax[1].set_title('TSNE Cluster Plot')
#Objects

# Object that holds Twain text
class TwainText(object):

    def __init__(self, p_filepath):

        # 0. Save path to text file
        self.m_filepath = p_filepath
        self.m_id = os.path.basename(self.m_filepath)

        # 1. Convert the file's contents into a list of words
        self.m_words = None
        with open(p_filepath, "r") as txt_file:
            contents = txt_file.read()
            self.m_words = contents.split(" ")
            self.m_words = [clean_word(word) for word in self.m_words]
            self.m_words = filter_nonwords(self.m_words)

        # 2. Calculate term frequencies for this text
        self.m_term_freqs = dict(Counter(self.m_words))

    def __str__(self):
        return " ".join(self.words)

    @property
    def id(self):
        return self.m_id
    @property
    def filepath(self):
        return self.m_filepath
    @property
    def term_frequencies(self):
        return self.m_term_freqs
    @property
    def word_count(self):
        return len(self.m_words)
    @property
    def words(self):
        return self.m_words


class TwainCollection(object):

    @property
    def text_count(self):
        return len(self.m_texts)
    @property
    def tf_idf_matrix(self):
        return self.m_tf_idf_vectors

    def __init__(self, p_texts, p_precalc_tfidf=True):

        # 0. Save reference to the texts
        self.m_texts = p_texts

        # 1. Create an id map of texts in the collection
        self.m_text_id_map = { text.id: text for text in self.m_texts }

        # 2. Determine the collection vocabulary and sort it alphabetically
        self.m_vocab = sorted(list(set([word for text in self.m_texts for word in text.words ])))

        # 3. Produce a matrix of tf-idf vectors for each text in the collection
        if p_precalc_tfidf:
            self.__calculate_tf_idf()

    def __calculate_tf_idf(self):

        # 1. Get the term frequencies for each word in the collection vocabulary in each text
        self.m_document_tfs = { text.id: text.term_frequencies for text in self.m_texts }

        # 2. Calculate the document frequency for each word in the vocabulary
        self.m_document_freqs = { word: 0 for word in self.m_vocab }
        for text in self.m_texts:
            for word in self.m_document_freqs:
                if self.m_document_tfs[text.id].get(word, 0) > 0:
                    self.m_document_freqs[word] += 1

        # 3. Calculate the inverse document frequency for each word in the vocabulary
        self.m_idfs = { word: log10(self.text_count/(self.m_document_freqs[word] + 1)) for word in self.m_vocab }

        # 4. Calculate the tf-idf score for each word in each text and construct tf-idf vector for each text
        self.m_tf_idfs = { text.id: { word: text.term_frequencies.get(word, 0) * self.m_idfs.get(word, 0) for word in self.m_vocab } for text in self.m_texts }
        # for text_id in self.m_tf_idfs:
        #     print("==========================================")
        #     print(text_id)
        #     print(", ".join([str(val) for val in self.m_tf_idfs[text_id].values() if 0 != val]))
        #     print("==========================================")
            

        # 5. Create vectors for all tf-idf scores for each text in the collection

        # A. Save a list index for each text to ensure ordered storage of tf-idf vectors
        self.m_tf_idf_vector_index = { self.m_texts[index].id: index for index in range(len(self.m_texts)) }
        self.m_tf_idf_vector_index_rev = { str(index): self.m_texts[index].id for index in range(len(self.m_texts)) }

        # B. Create a tf-idf vector for each text
        self.m_tf_idf_vectors = []
        for id in self.m_tf_idf_vector_index:

            # I. Get a reference to the text
            text = self.m_text_id_map[id]

            # II. Create a list of tf-idf scores for this text
            # NOTE: This also ensures consistent ordering of words in tf-idf vector
            tf_idf_scores = [ self.m_tf_idfs[id][word] for word in self.m_vocab ]

            # C. Save the vector
            # NOTE: Text order established by m_tf_idf_vector_index is preserved here
            self.m_tf_idf_vectors.append(tf_idf_scores)

        # 6. Save tf-idf vectors for words in this text into one matrix
        self.m_tf_idf_vectors = np.array(self.m_tf_idf_vectors)

    def tf_idf_to_csv(self, p_output_filepath):

        # 1. Write out the tf-idf matrix to a csv file
        with open(p_output_filepath, "w") as output_csv:

            # A. Write out header text_id followed by collection vocabulary alphabetically ordered
            header = "text_id," + ",".join(self.m_vocab) + "\n"
            output_csv.write(header)

            # B. Write out the tf-idf score for each word in the collection vocabulary for each text
            for str_index in self.m_tf_idf_vector_index_rev:

                index = int(str_index)
                text_id = self.m_tf_idf_vector_index_rev[str_index]
                text_line = "{0},{1}\n".format(text_id, ",".join([ str(item) for item in self.m_tf_idf_vectors[index] ]))
                output_csv.write(text_line)

    def vocab_to_csv(self, p_output_filepath):

        no_ch_list = []
        ord_ch_map = {}

        # 1. Write out the collection vocabulary to a csv file
        with open(p_output_filepath, "w") as output_csv:
            for word in self.m_vocab:
                if any([not is_alpha(ch) for ch in word]):
                    for ch in word:
                        if not is_alpha(ch):
                            if ch not in ord_ch_map:
                                ord_ch_map[ch] = [word]
                            else:
                                ord_ch_map[ch].append(word)
                    # print(word)
                output_csv.write(word + "\n")

        with open(os.path.dirname(p_output_filepath) + os.sep + "twain_autobio_ord_list.csv", "w") as output_csv:
            for ch in ord_ch_map:
                output_csv.write("{0},{1}\n".format(ord(ch), ",".join(ord_ch_map[ch])))
        # no_ch_list = list(set(no_ch_list))
        # for ch in no_ch_list:
        #     print(ord(ch))



def main():

    # test_word = "about‚Äîi"
    # print("‚" in test_word)
    # print(filter_nonwords([test_word]))

    # print(clean_word("=-three"))
    # if True:
    #     return

    # 1. Get word lists for each Twain text in the projects output folder
    print("Reading in Twain texts...")
    twain_texts = [TwainText(filepath) for filepath in glob.glob(data_path + "*")]
    twain_texts_txt = [str(text) for text in twain_texts]
    text_count = len(twain_texts)


    # if True:
    #     return

    # 2. Set up a collection of these texts and calculate tf-idf vectors for each
    print("Calculating tf-idf scores for the collection...")
    # twain_collection = TwainCollection(twain_texts)
    # twain_collection = TwainCollection(twain_texts, False)

    # twain_collection.tf_idf_to_csv("{0}{1}output{1}twain_autobio_tfidf.csv".format(os.getcwd(), os.sep))
    # twain_collection.vocab_to_csv("{0}{1}output{1}twain_autobio_vocab.csv".format(os.getcwd(), os.sep))

    vectorizer = TfidfVectorizer()
    twain_corpus_tf_idf = vectorizer.fit_transform(twain_texts_txt)
    # twain_corpus_tf_idf = twain_corpus_tf_idf.todense()


    # 3. Cluster tf-idf vectors of the text collection
    print("Clustering and plotting...")

    plot_kmeans_and_silhouette(twain_corpus_tf_idf)

    # clusters = KMeans(n_clusters=20, random_state=10).fit_predict(twain_corpus_tf_idf)
    # plot_tsne_pca(twain_corpus_tf_idf, list(range(20)))




    if True:
        return

    # 2. Cluster tf-idf vectors of the text collection
    print("Clustering and plotting...")
    range_n_clusters = [2, 3, 4, 5, 6]
    for n_clusters in range_n_clusters:

        # A. Cluster
        clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        cluster_labels = clusterer.fit_predict(twain_collection.tf_idf_matrix)    

        # B. Plot
        colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
        plt.scatter(twain_collection.tf_idf_matrix[:, 0],
                    twain_collection.tf_idf_matrix[:, 1],
                    marker='.', s=30, lw=0, alpha=0.7, c=colors, edgecolor='k')
        plt.show()

    # # 2. Create a word2vec model with each text's words as a word vector
    # model = Word2Vec(twain_texts, min_count=1)
    # # 3. Cluster the text word vectors in the model
    # A. Save a reference to the word vectors


if "__main__" == __name__:
    main()


