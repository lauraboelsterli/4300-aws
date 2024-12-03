'''DOESNT WORK ATM this plot shows the evolution of preselected terms aka terms_to_plot param
i will make another one showing the top n most frwquently used words over time'''
import query as ask 
import pandas as pd 


def process_terms(df):
    # print(df)
    # df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Convert to datetime
    # print(df)

    # df = df.dropna(subset=['date'])  # Drop rows without a valid date
    # df['year'] = df['date'].dt.year
    # print(df)
    df['date'] = df['date'].astype(str)
    # Extract the first 4 characters as 'year'
    df['year'] = df['date'].str[:4]
    # Convert to integer if necessary
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    # print(df)

    # Expand terms and count frequencies
    all_terms = []
    for terms in df['astronomy_terms']:
        all_terms.extend(eval(terms))  # Convert string list to Python list
    # print(all_terms)



    print(f"Length of all_terms: {len(all_terms)}")
    repeated_years = df['year'].repeat(df['astronomy_terms'].str.len())
    print(f"Length of repeated_years: {len(repeated_years)}")

    #can ti do temr frequnecy per year and nly show the top 3 most popular ones 
    term_counts = pd.DataFrame({'term': all_terms, 'year': df['year'].repeat(df['astronomy_terms'].str.len())})
    # Ensure each term aligns with its year
    return term_counts.groupby(['year', 'term']).size().reset_index(name='count')



import matplotlib.pyplot as plt

def plot_terms_over_time(term_counts, terms_to_plot):
    for term in terms_to_plot:
        subset = term_counts[term_counts['term'] == term]
        plt.plot(subset['year'], subset['count'], label=term)

    plt.xlabel("Year")
    plt.ylabel("Frequency")
    plt.title("Term Frequency Over Time")
    plt.legend()
    plt.show()

# Usage
# df = get_terms_over_time("starchive2.db")
df = ask.get_terms_over_time(db_path="starchive2.db")
df['date'] = df['date'].astype(str)
# Extract the first 4 characters as 'year'
df['year'] = df['date'].str[:4]
# Convert to integer if necessary
df['year'] = pd.to_numeric(df['year'], errors='coerce')
# print(df)
term_counts = process_terms(df)

# make terms_to_plot the terms that came up the most or i can integrate this into the dashbaord and people can select from which ones 
# they wanna visualize (make dropdown from most popular words but give opp for any word to be chosen regardless of frequency)
plot_terms_over_time(term_counts, terms_to_plot=["Mars", "canals", "telescopes"])
