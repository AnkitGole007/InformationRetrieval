# homework 1
# goal: tokenize, index, boolean query
# exports: 
#   student - a populated and instantiated ir4320.Student object
#   Index - a class which encapsulates the necessary logic for
#     indexing and searching a corpus of text documents


# ########################################
# first, create a student object
# ########################################

import cs547
import PorterStemmer

import glob
import os
import re
from nltk.tokenize import word_tokenize

MY_NAME = "Ankit Gole"
MY_ANUM  = 901029661 # put your WPI numerical ID here
MY_EMAIL = "aggole@wpi.edu"

# the COLLABORATORS list contains tuples of 2 items, the name of the helper
# and their contribution to your homework
COLLABORATORS = [ 
    ('Shreya Boyane', 'helped me in the logic for inverted index'),
    ]

# Set the I_AGREE_HONOR_CODE to True if you agree with the following statement
# "I do not lie, cheat or steal, or tolerate those who do."
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

# our index class definition will hold all logic necessary to create and search
# an index created from a directory of text files 
class Index(object):
    def __init__(self):
        # _inverted_index contains terms as keys, with the values as a list of
        # document indexes containing that term
        self._inverted_index = {}
        # _documents contains file names of documents
        self._documents = []
        # example:
        #   given the following documents:
        #     doc1 = "the dog ran"
        #     doc2 = "the cat slept"
        #   _documents = ['doc1', 'doc2']
        #   _inverted_index = {
        #      'the': [0,1],
        #      'dog': [0],
        #      'ran': [0],
        #      'cat': [1],
        #      'slept': [1]
        #      }


    # index_dir( base_path )
    # purpose: crawl through a nested directory of text files and generate an
    #   inverted index of the contents
    # preconditions: none
    # returns: num of documents indexed
    # hint: glob.glob()
    # parameters:
    #   base_path - a string containing a relative or direct path to a
    #     directory of text files to be indexed
    def index_dir(self, base_path):
        num_files_indexed = 0

        for file in glob.glob(os.path.join(base_path,'*')):
            file_name = os.path.basename(file)
            self._documents.append(file_name)

            # Storing tokens for each file in every loop
            file_tokens_list = []

            # Iterating over every file and adding the tokens in the file_tokens_list
            with open(file,'r',encoding='utf-8') as data:
                for text in data:
                    if text.strip():
                        file_token = self.tokenize(text)
                        file_tokens_list.extend(file_token)

            # Calling the Stemming function
            stem_tokens = self.stemming(file_tokens_list)

            # Implementing the Inverted index logic after getting the Stemmed Tokens
            for index in stem_tokens:
                if index not in self._inverted_index:
                    self._inverted_index[index] = set()

                self._inverted_index[index].add(len(self._documents)-1)

            # Increment value of indexed file count after every loop
            num_files_indexed += 1

        return num_files_indexed

    # tokenize( text )
    # purpose: convert a string of terms into a list of tokens.        
    # convert the string of terms in text to lower case and replace each character in text, 
    # which is not an English alphabet (a-z) and a numerical digit (0-9), with whitespace.
    # preconditions: none
    # returns: list of tokens contained within the text
    # parameters:
    #   text - a string of terms
    def tokenize(self, text):
        tokens = []

        # Using Regex library as token delimiters
        filter_text = re.sub(r'[^a-zA-Z0-9]', ' ', text)

        split_words = word_tokenize(filter_text)

        # Converting the tokens in lower case
        tokens = [word.lower() for word in split_words]

        return tokens

    # purpose: convert a string of terms into a list of tokens.        
    # convert a list of tokens to a list of stemmed tokens,     
    # preconditions: tokenize a string of terms
    # returns: list of stemmed tokens
    # parameters:
    #   tokens - a list of tokens
    def stemming(self, tokens):
        stemmed_tokens = []

        # Calling the PorterStemmer Class and using the main function, stem
        stemmed_tokens = [PorterStemmer.PorterStemmer().stem(p=s_word,i=0,j=len(s_word)-1) for s_word in tokens]

        return stemmed_tokens
    
    # boolean_search( text )
    # purpose: searches for the terms in "text" in our corpus using logical OR or logical AND. 
    # If "text" contains only single term, search it from the inverted index. If "text" contains three terms including "or" or "and", 
    # do OR or AND search depending on the second term ("or" or "and") in the "text".  
    # preconditions: _inverted_index and _documents have been populated from
    #   the corpus.
    # returns: list of document names containing relevant search results
    # parameters:
    #   text - a string of terms
    def boolean_search(self, text):
        results = []
        tokens = self.tokenize(text)
        s_tokens = self.stemming(tokens)

        # If the query consists of only 1 word
        if len(s_tokens) == 1:
            token = s_tokens[0]
            if token in self._inverted_index:
                results = [self._documents[doc_id] for doc_id in self._inverted_index[token]]
            else:
                return []
        # If query consists of multiple words and using OR / AND operations
        elif len(s_tokens) == 3 and s_tokens[1].lower() in {'or','and'}:
            term1,operator,term2 = s_tokens[0],s_tokens[1].lower(),s_tokens[2]

            t1 = self._inverted_index.get(term1,set())
            t2 = self._inverted_index.get(term2,set())

            if operator == 'or':
                result_doc_id = t1.union(t2)
            elif operator == 'and':
                result_doc_id = t1.intersection(t2)
            else:
                return []

            results = [self._documents[doc_id] for doc_id in result_doc_id]

        return results
    

# now, we'll define our main function which actually starts the indexer and
# does a few queries
def main(args):
    print(student)
    index = Index()
    print("starting indexer")
    num_files = index.index_dir(base_path='data/')
    print("indexed %d files" % num_files)
    for term in ('football', 'mike', 'sherman', 'mike OR sherman', 'mike AND sherman'):
        results = index.boolean_search(term)
        print("searching: %s -- results: %s" % (term, ", ".join(results)))

# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)

