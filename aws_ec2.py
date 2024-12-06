import panel as pn
import pandas as pd
import aws_query as ask  # Updated query module
import viz_wordfreqoveryears as countplot
import visz3 as viz3
import vizheatmap as heat
import plotly.graph_objects as go
from collections import Counter
from itertools import combinations
import networkx as nx
import io 
import boto3

# need upload that also requires a metadata declaration with the upload and then trigger the pipeline (make this the first tab)
# 2nd tab is the searchable part fo the db 
# 3rd tab is the network 
# on all tabs maybe have those price indicator widget thigns to show the total num of catalogs and total num of documents 



# Panel setup
pn.extension()
# Initialize S3 client
s3_client = boto3.client('s3')

# Define your S3 bucket name
bucket_name = "logbooks"

# FileInput widget
file_input = pn.widgets.FileInput(accept='.pdf', name="Upload PDF")
metadata_inputs = {
    "title": pn.widgets.TextInput(name="Title", placeholder="Enter title"),
    "subject": pn.widgets.TextInput(name="Subject", placeholder="Enter subject"),
    "description": pn.widgets.TextAreaInput(name="Description", placeholder="Enter description"),
    "creator": pn.widgets.TextInput(name="Creator", placeholder="Enter creator"),
    "date": pn.widgets.DatePicker(name="Date"),
    "rights": pn.widgets.TextAreaInput(name="Rights", placeholder="Enter rights information"),
    "format": pn.widgets.TextInput(name="Format", placeholder="Enter format"),
    "language": pn.widgets.TextInput(name="Language", placeholder="Enter language"),
    "type": pn.widgets.TextInput(name="Type", placeholder="Enter type"),
    "identifier": pn.widgets.TextInput(name="Identifier", placeholder="Enter identifier"),
}

# Button to trigger file upload
upload_button = pn.widgets.Button(name="Upload File", button_type="primary")

# Upload handler with metadata
def handle_upload(event):
    if file_input.value:
        file_content = file_input.value
        object_name = file_input.filename
        metadata = {key: widget.value for key, widget in metadata_inputs.items()}

        # Upload to S3
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=io.BytesIO(file_content),
                Metadata=metadata
            )
            print(f"File {object_name} uploaded successfully with metadata: {metadata}")
        except Exception as e:
            print(f"Error uploading file: {e}")

upload_button.on_click(handle_upload)

# Upload callback function
def upload_to_s3(event):
    if event.new:
        # Save the file content locally (optional)
        file_content = event.new
        object_name = file_input.filename

        # Define custom metadata (modify as needed or get from the user)
        metadata = {
            "title": "The Outlook on Mars",
            "subject": "Mars",
            "description": (
                "Percival Lowell's article 'Is There Life on Mars' in Outlook Magazine"),
            "creator": "Lowell, Percival",
            "date": "1907-02",
            "rights": "This object is property of the Lowell Observatory Archives. Any public use requires the written permission of the Lowell Observatory Archives. Contact us at archives@lowell.edu",
            "format": "Handwritten document, Typed document",
            "language": "English",
            "type": "Text",
            "identifier": "mars"
        }

        # Upload file to S3
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=io.BytesIO(file_content),
                Metadata=metadata
            )
            print(f"File {object_name} uploaded successfully to {bucket_name} with metadata.")
        except Exception as e:
            print(f"Error uploading file: {e}")

# Attach the callback to the FileInput widget
file_input.param.watch(upload_to_s3, 'value')

# Widgets
term_options = ["None"] + ask.fetch_all_terms()
term_selector = pn.widgets.Select(name="Exact match term search", options=term_options)
search_input = pn.widgets.TextInput(name="Partial match term search", placeholder="Enter term...")
# this one doesnt work cuz i dnot have the right query set up for it 
term_selector_freq = pn.widgets.MultiChoice(name="Select Terms", options=ask.fetch_all_terms())
# top_n_slider = pn.widgets.IntSlider(name="Top N Words Slider", start=0, end=50, step=1, value=10)

results_table = pn.widgets.Tabulator(name="Results", sizing_mode="stretch_both")
def create_interactive_bigrams():
    # Fetch terms per document from the database
    terms = ask.fetch_terms_per_doc()  # Use the updated query function without db_path

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

# Callbacks
def update_table(event):
    term = event.new
    results = ask.fetch_documents_by_term(term) if term else pd.DataFrame()
    results_table.value = results

# def update_countplot(terms_to_plot):
#     df = ask.get_terms_over_time()
#     return countplot.plot_term_frequency_by_year(df, terms_to_plot)

# def update_topn(top_n):
#     df = ask.get_terms_over_time()
#     return pn.pane.Matplotlib(viz3.plot_top_terms_over_time(df, top_n), dpi=144)

# plot_countplot = pn.bind(update_countplot, term_selector_freq)
# plot_topn = pn.bind(update_topn, top_n_slider)
def search_callback(event):
    term = event.new.strip() 
    if term:  # Avoid empty searches
        results = ask.fetch_documents_by_partial_term( term)
        results_table.value = results
    else:
        results_table.value = pd.DataFrame()  # Clear results if no term entered

# Attach callbacks
term_selector.param.watch(update_table, 'value')
# search_input.param.watch(lambda e: update_table(e), 'value')
search_input.param.watch(search_callback, 'value')
# Bind the graph to a callback for dynamic updates
bigram_network_plot = pn.bind(create_interactive_bigrams)
sidebar2 = pn.Column(
    pn.pane.Markdown("## Upload File with Metadata"),
    file_input,
    *metadata_inputs.values(),
    upload_button
)
layout = pn.template.FastListTemplate(
    title="Starchive",
    sidebar=[term_selector, search_input, term_selector_freq, sidebar2],
    main=[
        pn.Tabs(
            ("Search Results", results_table),
            # ("Countplot", plot_countplot),
            ("Interactive Network", bigram_network_plot)
            # ("Top N Words Frequency", plot_topn)

        )
    ],
    header_background="#800080"
)



pn.serve(layout)
