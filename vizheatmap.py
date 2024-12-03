import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import query as ask 

def process_terms_with_explode(df):
    # Extract year from the date
    df['date'] = df['date'].astype(str)
    df['year'] = df['date'].str[:4]
    df['year'] = pd.to_numeric(df['year'], errors='coerce')

    # Ensure astronomy_terms column is a proper list
    df['astronomy_terms'] = df['astronomy_terms'].apply(eval)  # Convert stringified lists to Python lists
    print(df['astronomy_terms'])

    # Explode the terms column
    exploded_df = df.explode('astronomy_terms')
    print(exploded_df)

    # Rename columns for clarity
    exploded_df.rename(columns={'astronomy_terms': 'term'}, inplace=True)

    # Group by year and term, and count occurrences
    term_counts = exploded_df.groupby(['year', 'term']).size().reset_index(name='count')
    return term_counts
    # print(term_counts)
def plot_cooccurrence_heatmap(term_counts):
    cooccurrence = term_counts.pivot_table(index='term', columns='year', values='count', aggfunc='sum').fillna(0)
    sns.heatmap(cooccurrence, cmap="Blues", linewidths=0.5)
    plt.title("Term Co-occurrence Heatmap")
    plt.show()

from scipy.cluster.hierarchy import linkage, dendrogram
import seaborn as sns

def plot_clustered_heatmap(df):
    # print(term_counts)
    df['date'] = df['date'].astype(str)
    df['year'] = df['date'].str[:4]
    df['year'] = pd.to_numeric(df['year'], errors='coerce')

    # Ensure astronomy_terms column is a proper list
    df['astronomy_terms'] = df['astronomy_terms'].apply(eval)  # Convert stringified lists to Python lists
    print(df['astronomy_terms'])

    # Explode the terms column
    exploded_df = df.explode('astronomy_terms')
    # print(exploded_df)

    # Rename columns for clarity
    exploded_df.rename(columns={'astronomy_terms': 'term'}, inplace=True)

    # Group by year and term, and count occurrences
    term_counts = exploded_df.groupby(['year', 'term']).size().reset_index(name='count')

    cooccurrence = term_counts.pivot_table(index='term', columns='year', values='count', aggfunc='sum').fillna(0)
    # print(cooccurrence)
    sns.clustermap(
        cooccurrence,
        method="ward",
        cmap="Blues",
        linewidths=0.5,
        figsize=(6, 5),
    )
    plt.title("Clustered Term Co-occurrence Heatmap")
    # plt.show()
    return plt.gcf()

def plot_top_terms_heatmap(df, top_n=10):
    df['date'] = df['date'].astype(str)
    df['year'] = df['date'].str[:4]
    df['year'] = pd.to_numeric(df['year'], errors='coerce')

    def safe_eval(value):
        if isinstance(value, str):
            try:
                return eval(value)
            except Exception as e:
                print(f"Failed to evaluate: {value}. Error: {e}")
                return []
        return value if isinstance(value, list) else []

    # Ensure astronomy_terms column is a proper list
    df['astronomy_terms'] = df['astronomy_terms'].apply(safe_eval)  # Convert stringified lists to Python lists
    # print(df['astronomy_terms'])

    # Explode the terms column
    exploded_df = df.explode('astronomy_terms')
    # print(exploded_df)

    # Rename columns for clarity
    exploded_df.rename(columns={'astronomy_terms': 'term'}, inplace=True)

    # Group by year and term, and count occurrences
    term_counts = exploded_df.groupby(['year', 'term']).size().reset_index(name='count')
    top_terms = term_counts.groupby('term')['count'].sum().nlargest(top_n).index
    filtered_counts = term_counts[term_counts['term'].isin(top_terms)]
    cooccurrence = filtered_counts.pivot_table(index='term', columns='year', values='count', aggfunc='sum').fillna(0)
    sns.heatmap(cooccurrence, cmap="Blues", linewidths=0.5)
    plt.title(f"Top {top_n} Term Co-occurrence Heatmap")
    # plt.show()
    return plt.gcf()

def plot_annotated_heatmap(term_counts, annotations):
    cooccurrence = term_counts.pivot_table(index='term', columns='year', values='count', aggfunc='sum').fillna(0)
    plt.figure(figsize=(5, 6))
    sns.heatmap(cooccurrence, cmap="Blues", linewidths=0.5, annot=False)
    plt.title("Annotated Term Co-occurrence Heatmap")

    # Add annotations
    for (term, year), annotation in annotations.items():
        if term in cooccurrence.index and year in cooccurrence.columns:
            plt.text(
                x=cooccurrence.columns.get_loc(year),
                y=cooccurrence.index.get_loc(term),
                s=annotation,
                color="red",
                ha="center",
                va="center",
            )

    plt.show()






# def main():
#     df = ask.get_terms_over_time(db_path="starchive2.db")
#     term_counts = process_terms_with_explode(df)  
#     # Example Usage
#     # plot_cooccurrence_heatmap(term_counts)
#     # Call this function in main()
#     # plot_clustered_heatmap(term_counts)
#     # Call this function in main()
#     plot_top_terms_heatmap(df, top_n=10)
#     # Call this function in main()
#     # Example annotation data: {(term, year): "Event"}
#     # annotations = {
#     #     ("Mars", 1907): "Major observation",
#     #     ("canals", 1908): "Publication on canals",
#     # }
#     # plot_annotated_heatmap(term_counts, annotations)
# main()
