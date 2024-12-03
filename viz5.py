
# '''CHOSE THIS ONE this is scatter plot of freq for user selected words '''
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import query as ask 

# # def process_terms_with_explode(df):
# #     # Extract year from the date
# #     df['date'] = df['date'].astype(str)
# #     df['year'] = df['date'].str[:4]
# #     df['year'] = pd.to_numeric(df['year'], errors='coerce')

# #     # Ensure astronomy_terms column is a proper list
# #     df['astronomy_terms'] = df['astronomy_terms'].apply(eval)  # Convert stringified lists to Python lists
# #     print(df['astronomy_terms'])

# #     # Explode the terms column
# #     exploded_df = df.explode('astronomy_terms')
# #     print(exploded_df)

# #     # Rename columns for clarity
# #     exploded_df.rename(columns={'astronomy_terms': 'term'}, inplace=True)

# #     # Group by year and term, and count occurrences
# #     term_counts = exploded_df.groupby(['year', 'term']).size().reset_index(name='count')
# #     print(term_counts)

# #     return term_counts

# def plot_selected_terms_over_time(df, selected_terms):
#     df['date'] = df['date'].astype(str)
#     df['year'] = df['date'].str[:4]
#     df['year'] = pd.to_numeric(df['year'], errors='coerce')

#     # Ensure astronomy_terms column is a proper list
#     df['astronomy_terms'] = df['astronomy_terms'].apply(eval)  # Convert stringified lists to Python lists
#     # print(df['astronomy_terms'])

#     # Explode the terms column
#     exploded_df = df.explode('astronomy_terms')
#     # print(exploded_df)

#     # Rename columns for clarity
#     exploded_df.rename(columns={'astronomy_terms': 'term'}, inplace=True)

#     # Group by year and term, and count occurrences
#     term_counts = exploded_df.groupby(['year', 'term']).size().reset_index(name='count')
#     # print(term_counts)
#     # Filter the data for the selected terms
#     filtered_counts = term_counts[term_counts['term'].isin(selected_terms)]

#     # Plot each selected term
#     for term in selected_terms:
#         subset = filtered_counts[filtered_counts['term'] == term]
        
#         # Check if data exists for the term
#         if subset.empty:
#             print(f"No data available for term: {term}")
#             continue

#         # Plot the data
#         plt.plot(subset['year'], subset['count'], label=term, marker='o', linestyle='-')

#     # Plot settings
#     plt.xlabel("Year")
#     plt.ylabel("Frequency")
#     plt.title("Selected Terms Usage Over Time")
#     plt.legend()
#     plt.grid(True)
#     plt.show()

# # Example Usage
# # df = ask.get_terms_over_time(db_path="starchive2.db")
# # # term_counts = process_terms_with_explode(df)  

# # # List of terms to analyze
# # selected_terms = ["Mars", "canals", "telescopes"]

# # # Generate the plot
# # plot_selected_terms_over_time(df, selected_terms)
import matplotlib.pyplot as plt
import pandas as pd
import query as ask

def plot_selected_terms_over_time(selected_terms):
    df = ask.get_terms_over_time(db_path="starchive2.db")
    df['date'] = df['date'].astype(str)
    df['year'] = df['date'].str[:4]
    df['year'] = pd.to_numeric(df['year'], errors='coerce')

    # Ensure astronomy_terms column is a proper list
    df['astronomy_terms'] = df['astronomy_terms'].apply(eval)  # Convert stringified lists to Python lists

    # Explode the terms column
    exploded_df = df.explode('astronomy_terms')

    # Rename columns for clarity
    exploded_df.rename(columns={'astronomy_terms': 'term'}, inplace=True)

    # Group by year and term, and count occurrences
    term_counts = exploded_df.groupby(['year', 'term']).size().reset_index(name='count')

    # Filter the data for the selected terms
    filtered_counts = term_counts[term_counts['term'].isin(selected_terms)]

    # Create a figure
    fig, ax = plt.subplots(figsize=(6, 5))

    # Plot each selected term
    for term in selected_terms:
        subset = filtered_counts[filtered_counts['term'] == term]
        
        # Check if data exists for the term
        if subset.empty:
            print(f"No data available for term: {term}")
            continue

        # Plot the data
        ax.plot(subset['year'], subset['count'], label=term, marker='o', linestyle='-')

    # Plot settings
    ax.set_xlabel("Year")
    ax.set_ylabel("Frequency")
    ax.set_title("Selected Terms Usage Over Time")
    ax.legend()
    ax.grid(True)

    # Return the figure object for Panel
    return fig

# Example Usage
# def get_plot(selected_terms):
#     df = ask.get_terms_over_time(db_path="starchive2.db")
#     return plot_selected_terms_over_time(df, selected_terms)

# def get_plot(selected_terms):
#     # Example: Create a Matplotlib plot for the selected terms
#     plt.figure(figsize=(10, 6))
#     for term in selected_terms:
#         # Assume some data processing logic here to get term frequency over time
#         data = ask.get_term_data(term)  # Modify this to match your actual data-fetching logic
#         plt.plot(data['year'], data['count'], label=term)
#     plt.xlabel("Year")
#     plt.ylabel("Frequency")
#     plt.legend()
#     plt.title("Term Frequency Over Time")
#     return plt.gcf()  # Return the Matplotlib figure

