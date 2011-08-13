#!/usr/bin/env python

# Copyright (c) 2010, Taher Haveliwala <oss@taherh.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * The names of project contributors may not be used to endorse or
#       promote products derived from this software without specific
#       prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
Sample usage as a script::

    $ python similarity.py http://www.stanford.edu/ http://www.berkeley.edu/ http://www.mit.edu/
    Comparing files ['http://www.stanford.edu/', 'http://www.berkeley.edu/', 'http://www.mit.edu/']
    sim(http://www.stanford.edu/,http://www.berkeley.edu/)=0.322771960247
    sim(http://www.stanford.edu/,http://www.mit.edu/)=0.142787018368
    sim(http://www.berkeley.edu/,http://www.mit.edu/)=0.248877629741

'''

from __future__ import (division, absolute_import, print_function,
    unicode_literals)

# boilerplate to allow running as script
if __name__ == "__main__" and __package__ is None:
    import sys, os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    import pysimsearch
    __package__ = str("pysimsearch")
    del sys, os
    
# external modules
import argparse

# our modules
from . import doc_reader
from .exceptions import *
from .term_vec import *


# --- top-level functions ---
def measure_similarity(file_a, file_b, sim_func = None):
    '''
    Returns the textual similarity of term_vec_a and term_vec_b using chosen
    similarity metric
    
    'sim_func' defaults to cosine_sim if not specified
    
    Consumes file_a and file_b
    '''
    if sim_func == None:
        sim_func = cosine_sim  # default to cosine_sim
    
    return sim_func(doc_reader.term_vec(file_a), doc_reader.term_vec(file_b))

def pairwise_compare_files(*named_files):
    '''
    Do a pairwise comparison of the 'named_files'and print their
    pairwise similarities
    '''
    similarities = []
    for i in range(0, len(named_files)):
        for j in range(i+1, len(named_files)):
            (fname_a, file_a) = named_files[i]
            (fname_b, file_b) = named_files[j]
            similarities.append((fname_a,
                                 fname_b,
                                 measure_similarity(file_a, file_b)))
    return similarities

def pairwise_compare_filenames(*filenames):
    '''
    Do a pairwise comparison of the documents specified by 'filenames'
    and return their pairwise similarities
    '''    
    similarities = []
    for i in range(0, len(filenames)):
        for j in range(i+1, len(filenames)):
            fname_a = filenames[i]
            fname_b = filenames[j]
            with doc_reader.get_text_file(fname_a) as file_a:
                with doc_reader.get_text_file(fname_b) as file_b:
                    similarities.append((fname_a,
                                         fname_b,
                                         measure_similarity(file_a, file_b)))
    return similarities
  
# --- Similarity measures ---
    
def cosine_sim(u, v):
    '''
    Returns the cosine similarity of u,v: <u,v>/(|u||v|)
    where |u| is the L2 norm
    '''
    return dot_product(u, v) / (l2_norm(u) * l2_norm(v))

def jaccard_sim(A, B):
    r'''
    Returns the Jaccard similarity of A,B: |A \cap B| / |A \cup B|
    We treat A and B as multi-sets (The Jaccard coefficient is technically
    meant for sets, although it is easily extended to multi-sets)
    '''
    return mag_intersect(A, B) / mag_union(A, B)


# --- main() ---

def main():
    '''Commandline interface for measure pairwise similarities of files'''
    parser = argparse.ArgumentParser(
        description='List pairwise similarities of input documents')
    parser.add_argument('doc', nargs='*',
                        help='a document in the comparison list')
    parser.add_argument('-l', '--list', nargs='?',
                        help='file containing list of documents to compare')

    args = parser.parse_args()

    doc_list = []
    if args.list != None:
        try:
            with open(args.list) as input_docnames_file:
                doc_list = [line.strip() for line in
                            input_docnames_file.readlines()]
        except IOError:
            print("Sorry, could not open " + args.list)

    doc_list.extend(args.doc)

    if len(doc_list) < 2:
        raise Error("Sorry, you must specify at least two documents "
                    "to compare.")  

    print('Comparing files {}'.format(str(doc_list)))
    similarities = pairwise_compare_filenames(*doc_list)
    for (fname_a, fname_b, sim) in similarities:
        print('sim({0},{1})={2}'.format(fname_a, fname_b, sim))


if __name__ == '__main__':
    main()
