# homework 4
# goal: ranked retrieval, PageRank, crawling
# exports:
#   student - a populated and instantiated cs547.Student object
#   PageRankIndex - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents and providing a
#     ranked result set

# ########################################
# first, create a student object
# ########################################

import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import numpy as np
import cs547

MY_NAME = "Ankit Gole"
MY_ANUM  = 901029661 # put your UID here
MY_EMAIL = "aggole@wpi.edu"

# the COLLABORATORS list contains tuples of 2 items, the name of the helper
# and their contribution to your homework
COLLABORATORS = [
    ]

# Set the I_AGREE_HONOR_CODE to True if you agree with the following statement
# "An Aggie does not lie, cheat or steal, or tolerate those who do."
I_AGREE_HONOR_CODE = True

# this defines the student object
student = cs547.Student(
    MY_NAME,
    MY_ANUM,
    MY_EMAIL,
    COLLABORATORS,
    I_AGREE_HONOR_CODE
    )


# ########################################
# now, write some code
# ########################################
 # you will want this for parsing html documents


# our index class definition will hold all logic necessary to create and search
# an index created from a web directory
#
# NOTE - if you would like to subclass your original Index class from homework
# 1 or 2, feel free, but it's not required.  The grading criteria will be to
# call the index_url(...) and ranked_search(...) functions and to examine their
# output.  The index_url(...) function will also be examined to ensure you are
# building the index sanely.

class PageRankIndex(object):
    def __init__(self):
        # you'll want to create something here to hold your index, and other
        # necessary data members
        self.index = {}
        self.webgraph = {}
        self.pageranks = {}
        self.urls = []
        self.max_depth = 4

    pass

    # index_url( url )
    # purpose: crawl through a web directory of html files and generate an
    #   index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: use BeautifulSoup and urllib
    # parameters:
    #   url - a string containing a url to begin indexing at
    def index_url(self, url,depth=0):
        if depth > self.max_depth:
            return 0

        try:
            response = urllib.request.urlopen(url)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return 0
        html_content = response.read().decode('utf-8')
        soup = BeautifulSoup(html_content,'html.parser')

        page_text = soup.get_text()
        tokens = self.tokenize(page_text)
        #print(tokens)

        if url not in self.urls:
            self.urls.append(url)

        for token in tokens:
            if token not in self.index:
                self.index[token] = []
            if url not in self.index[token]:
                self.index[token].append(url)

        #print(self.index)

        self.webgraph[url] = []
        for a in soup.find_all('a',href=True):
            link = urljoin(url,a['href'])
            if link not in self.webgraph[url]:
                self.webgraph[url].append(link)
                self.index_url(link,depth+1)
        #print(depth)

        if depth == 0:
            #print('Depth is Zero')
            self.compute_page_rank()

        return len(self.urls)

    # tokenize( text )
    # purpose: convert a string of terms into a list of terms
    # preconditions: none
    # returns: list of terms contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):

        clean_string = re.sub('[^a-z0-9]', ' ', text.lower())
        tokens = clean_string.split()
        return tokens

    # ranked_search( text )
    # purpose: searches for the terms in "text" in our index and returns
    #   AND results for highest 10 ranked results
    # preconditions: .index_url(...) has been called on our corpus
    # returns: list of tuples of (url,PageRank) containing relevant
    #   search results
    # parameters:
    #   text - a string of query terms

    def compute_page_rank(self, damping_factor=0.9, max_iter = 100,tol=1e-6):
        N = len(self.urls)
        M = np.zeros((N,N))
        pagerank = np.ones(N)/N
        teleport = np.ones(N)/N

        index_url = list(self.urls)
        url_index = {url: i for i, url in enumerate(index_url)}  # Mapping from URL to index

        # Populate the adjacency matrix M
        for url, links in self.webgraph.items():
            if links:
                for link in links:
                    if link in url_index:  # Ensure the link is in the indexed URLs
                        M[url_index[link], url_index[url]] = 1  # Invert indexing to build the correct transition matrix

        # Normalize the columns of M to ensure that each column sums to 1
        for j in range(N):
            if np.sum(M[:, j]) > 0:
                M[:, j] /= np.sum(M[:, j])
            else:
                M[:, j] = 1 / N  # Handle dangling nodes (no outgoing links)
        #print(M)
        # Power iteration method to compute PageRank
        for i in range(max_iter):
            new_rank = damping_factor * M @ pagerank + (1 - damping_factor) * teleport
            if np.linalg.norm(new_rank - pagerank, 1) < tol:  # Check for convergence
                break
            pagerank = new_rank

        self.pageranks = {index_url[i]: pagerank[i] for i in range(N)}

    def ranked_search(self, text):
        tokens = self.tokenize(text)
        results = {}

        for token in tokens:
            if token in self.index:
                for url in self.index[token]:
                    if url not in results:
                        results[url] = 0
                    results[url] += self.pageranks.get(url, 0)

        ranked_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

        return ranked_results[:10]


# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):
    print(student)
    index = PageRankIndex()
    url = 'http://web.cs.wpi.edu/~kmlee/cs547/new10/index.html'
    num_files = index.index_url(url)
    #print(num_files)

    search_queries = (
       'palatial', 'college ', 'palatial college', 'college supermarket', 'famous aggie supermarket'
        )
    for q in search_queries:
        results = index.ranked_search(q)
        print("searching: %s -- results: %s" % (q, results))


# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)
