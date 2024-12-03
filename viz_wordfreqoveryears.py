'''
CHOSE THIS ONE this is a bar plot with time and the frequency as y 
(same as visz3.py just different vis chosen)
'''
# '''this plot shows the evolution of preselected terms aka terms_to_plot param
# i will make another one showing the top n most frwquently used words over time'''
import query as ask 
import pandas as pd 
import pandas as pd
import matplotlib.pyplot as plt


def plot_terms_over_time(term_counts, terms_to_plot):
    # print(term_counts['year'].dtype)

    for term in terms_to_plot:
        subset = term_counts[term_counts['term'] == term]

        # if subset.empty:
        #     print(f"No data for term: {term}")
        #     continue

        print(f"Plotting data for {term}:\n{subset}")

        
        # plt.bar(subset['year'], subset['count'], label=term)
        plt.bar(subset['year'], subset['count'], label=term)

    plt.xlabel("Year")
    plt.ylabel("Frequency")
    plt.title("Term Frequency Over Time")
    plt.legend()
    plt.show()


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

import seaborn as sns
import matplotlib.pyplot as plt

def plot_term_frequency_by_year(df, terms_to_plot=None):
    # Filter for specific terms if provided
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

    if terms_to_plot:
        term_counts = term_counts[term_counts['term'].isin(terms_to_plot)]
    
    # Create a countplot
    plt.figure(figsize=(6, 5))
    sns.barplot(
        data=term_counts, 
        x='year', 
        y='count', 
        hue='term', 
        estimator=sum, 
        errorbar=None
    )

    plt.title("Term Frequency Over Years", fontsize=16)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel("Frequency", fontsize=14)
    plt.legend(title="Term", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    # plt.show()
    return plt.gcf()




# def main():
#     # Example Usage
#     df = ask.get_terms_over_time(db_path="starchive2.db")

#     # Process terms using the explode method
#     term_counts = process_terms_with_explode(df)
#     # print(term_counts)

#     # plot_terms_over_time(term_counts, terms_to_plot=["Andes", "canals", "Chile"])

#     # Example Usage:
#     # Assume term_counts is a DataFrame with 'year', 'term', and 'count' columns.
#     plot_term_frequency_by_year(term_counts, terms_to_plot=["Mars", "canals", "velocity"])


# main()
