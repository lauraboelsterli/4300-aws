import panel as pn
# import query as query
# from data_pipeline import query
import pandas as pd 
import visualizations as viz 
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from itertools import combinations
import query as ask 
import plotly.graph_objects as go
import viz5 as viz5
import viz_wordfreqoveryears as countplot
import visz3 as viz3
import vizheatmap as heat

# Loads javascript dependencies and configures Panel (required)
pn.extension()

# Set up database path
db_path = "starchive.db"

# Dropdown widget for selecting a term
# term_selector = pn.widgets.Select(name="Select an Astronomimcal Term", options=query.fetch_all_terms(db_path))
term_options = ["None"] + ask.fetch_all_terms(db_path)
term_selector = pn.widgets.Select(name="Exact match term search (note the search widgets are not conn. to each other atm)", options=term_options)


# Table for displaying document results
results_table = pn.widgets.Tabulator(name="Results", sizing_mode="stretch_both")

search_input = pn.widgets.TextInput(name="partial match term search", placeholder="Enter term to search...")

term_selector_freq = pn.widgets.MultiChoice(
    name="Select Terms",
    value=["Mars", "canals", "gravity"],
    # there smth wrong with giving a list to this 
    options=ask.fetch_all_terms("starchive2.db")
)

top_n_slider = pn.widgets.IntSlider(name='Top n word fre Slider', start=0, end=50, step=1, value=10)
top_n_slider2 = pn.widgets.IntSlider(name='Top n word for other Slider', start=0, end=50, step=1, value=10)


def update_plot(selected_terms):
    # Generate the plot for the selected terms
    return pn.pane.Matplotlib(viz5.plot_selected_terms_over_time(selected_terms))
# Attach callback to the widget
plot_pane = pn.bind(update_plot, term_selector_freq)

def update_countplot(terms_to_plot):
    df = ask.get_terms_over_time(db_path="starchive2.db")
    # Generate the plot for the selected terms
    return countplot.plot_term_frequency_by_year(df, terms_to_plot)
# Attach callback to the widget
plot_countplot = pn.bind(update_countplot, term_selector_freq)


def update_topn(top_n):
    df = ask.get_terms_over_time(db_path="starchive2.db")
    # Generate the plot for the selected terms
    # return viz3.plot_top_terms_over_time(df, top_n)
    return pn.pane.Matplotlib(viz3.plot_top_terms_over_time(df, top_n), dpi=144)
# Attach callback to the widget
plot_topn = pn.bind(update_topn, top_n_slider)

# def update_topn_heat(top_n):
#     df = ask.get_terms_over_time(db_path="starchive2.db")
#     # Generate the plot for the selected terms
#     # return viz3.plot_top_terms_over_time(df, top_n)
#     return pn.pane.Matplotlib(heat.plot_top_terms_heatmap(df, top_n))
# Attach callback to the widget
# topn_heat = pn.bind(update_topn_heat, top_n_slider2)
# topn_heat = update_topn_heat(top_n=10)

topn_heat = heat.plot_top_terms_heatmap(df= ask.get_terms_over_time(db_path="starchive2.db"), top_n=10)

heatmap_cluster = heat.plot_clustered_heatmap(df = ask.get_terms_over_time(db_path="starchive2.db"))



def create_interactive_bigrams():
    # Example: Replace this with actual data from your database
    terms = ask.fetch_terms_per_doc(db_path='starchive2.db')  # Replace with your actual function

    # Step 1: Create bigram pairs
    bigrams = []
    for term_list in terms:
        bigrams.extend(combinations(term_list, 2))

    # Step 2: Count bigram frequencies
    bigram_counts = Counter(bigrams)

    # Step 3: Build the NetworkX graph
    G = nx.Graph()
    for (term1, term2), weight in bigram_counts.items():
        G.add_edge(term1, term2, weight=weight)

    # Step 4: Convert NetworkX graph to Plotly format
    pos = nx.spring_layout(G)  # Generate positions for nodes
    edge_x = []
    edge_y = []
    edge_weights = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_weights.append(edge[2]['weight'])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node}<br>Frequency: {G.degree[node]}")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            size=10,
            color='skyblue',
            line=dict(width=1, color='darkblue')
        )
    )

    # Step 5: Create Plotly figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Interactive Bigram Network',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False)
                    ))

    return fig
bigram_network_plot = create_interactive_bigrams()

# exact matches 
# Callback to update the table when a term is selected
def update_table(event):
    term = event.new  # Get selected term
    results = ask.fetch_documents_by_term(db_path, term)
    results_table.value = results

# Attach callback to the widget
term_selector.param.watch(update_table, 'value')


# partial matches 
# Callback for search input
def search_callback(event):
    term = event.new.strip() 
    if term:  # Avoid empty searches
        results = ask.fetch_documents_by_partial_term(db_path, term)
        results_table.value = results
    else:
        results_table.value = pd.DataFrame()  # Clear results if no term entered

search_input.param.watch(search_callback, 'value')



layout = pn.template.FastListTemplate(
    title="Starchive",
    sidebar=[
        term_selector,search_input, term_selector_freq, top_n_slider
    ],
    theme_toggle=False,
    main=[
                pn.Tabs(
        ("Search the Lowell Archive", results_table),
        ("Countplot", plot_countplot),
        ("Interactive network", bigram_network_plot), 
        ("Scatter of term freq", plot_pane), 
        ("Top n words freq", plot_topn), 
        ("Clustered heatmap", heatmap_cluster),
        ("Top N heatmap", topn_heat)
        )
    ],
    header_background='#800080'

)

pn.serve(layout)


