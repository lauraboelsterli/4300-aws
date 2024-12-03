'''CHOSE THIS ONE this is a scattter plot wiht word freq and time on x of the top_n words '''
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
    print(term_counts)

    return term_counts

def plot_top_terms_over_time(df, top_n=10):
    df['date'] = df['date'].astype(str)
    df['year'] = df['date'].str[:4]
    df['year'] = pd.to_numeric(df['year'], errors='coerce')

    # Ensure astronomy_terms column is a proper list
    df['astronomy_terms'] = df['astronomy_terms'].apply(eval)  # Convert stringified lists to Python lists
    # print(df['astronomy_terms'])

    # Explode the terms column
    exploded_df = df.explode('astronomy_terms')
    # print(exploded_df)

    # Rename columns for clarity
    exploded_df.rename(columns={'astronomy_terms': 'term'}, inplace=True)

    # Group by year and term, and count occurrences
    term_counts = exploded_df.groupby(['year', 'term']).size().reset_index(name='count')
    # Aggregate total counts for each term
    total_counts = term_counts.groupby('term')['count'].sum().reset_index()
    
    # Get the top N terms
    top_terms = total_counts.nlargest(top_n, 'count')['term']
    # print(f"Top {top_n} terms: {top_terms.tolist()}")
    
    # Filter term_counts to include only top N terms
    filtered_counts = term_counts[term_counts['term'].isin(top_terms)]

    # Plot each term
    for term in top_terms:
        subset = filtered_counts[filtered_counts['term'] == term]
        plt.plot(subset['year'], subset['count'], label=term, marker='o', linestyle='-')

    # Plot settings
    plt.xlabel("Year")
    plt.ylabel("Frequency")
    plt.title(f"Top {top_n} Terms Frequency Over Time")
    plt.legend()
    plt.grid(True)
    # plt.show()
    return plt.gcf()

# # Example Usage
# df = ask.get_terms_over_time(db_path="starchive2.db")
# term_counts = process_terms_with_explode(df)  # Ensure 'term_counts' contains ['year', 'term', 'count']

# plot_top_terms_over_time(term_counts, top_n=10)
