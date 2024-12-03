'''
CHOSE THIS ONE - this is a network, maybe ill make it interactive and add name of words and the weight (freq count) on hover'''
'''
make this interactive, and on hover show the lables of the words and maybe only show some words??
the first counts cocurrences overall the second one shows cocurrences within documents 
wait after reviewing the counter dictionaries, the vizs are actually the same 
'''
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from itertools import combinations
import query as ask 
import plotly.graph_objects as go


def create_term_relationshipbigram(db_path='starchive2.db'):

    # Example: Extracted terms from documents
    terms = ask.fetch_terms_per_doc(db_path)

    # Step 1: Create bigram pairs
    bigrams = []
    for term_list in terms:
        bigrams.extend(combinations(term_list, 2))
    # print(bigrams)

    # Step 2: Count bigram frequencies
    bigram_counts = Counter(bigrams)
    # print(bigram_counts)

    # Step 3: Create a NetworkX graph
    G = nx.Graph()
    for (term1, term2), weight in bigram_counts.items():
        G.add_edge(term1, term2, weight=weight)

    # Step 4: Visualize
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=0.3)  # Force-directed layout
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="skyblue")
    nx.draw_networkx_edges(G, pos, width=[G[u][v]['weight'] for u, v in G.edges()])
    nx.draw_networkx_labels(G, pos, font_size=8)
    plt.title("Bigram Network of Astronomy Terms")
    # plt.show()
    return plt.gcf()

def main():
    create_term_relationshipbigram()

main()


# import networkx as nx
# import matplotlib.pyplot as plt
# from collections import Counter
# from itertools import combinations
# import query as ask 

# def create_document_level_cooccurrence_graph():
#     # Example: Fetch terms grouped by documents
#     terms_per_document = ask.fetch_terms_per_doc(db_path='starchive2.db')
#     # print(terms_per_document)

#     # Step 1: Initialize a Counter for term co-occurrences
#     cooccurrence_counts = Counter()

#     # Step 2: Count co-occurrences within each document
#     for term_list in terms_per_document:
#         # Create all unique pairs of terms in the same document
#         cooccurrence_counts.update(combinations(term_list, 2))
#     print(cooccurrence_counts)
#     # Step 3: Create a NetworkX graph
#     G = nx.Graph()
#     for (term1, term2), weight in cooccurrence_counts.items():
#         G.add_edge(term1, term2, weight=weight)  # Use co-occurrence count as edge weight

#     # Step 4: Visualize the graph
#     plt.figure(figsize=(12, 10))
#     pos = nx.spring_layout(G, k=0.3)  # Force-directed layout
#     # Draw nodes
#     nx.draw_networkx_nodes(G, pos, node_size=700, node_color="skyblue")
#     # Draw edges with weights affecting thickness
#     nx.draw_networkx_edges(G, pos, width=[G[u][v]['weight'] for u, v in G.edges()])
#     # Draw labels
#     nx.draw_networkx_labels(G, pos, font_size=8)
#     plt.title("Document-Level Term Co-occurrence Network")
#     plt.show()

# def main():
#     create_document_level_cooccurrence_graph()

# main()
