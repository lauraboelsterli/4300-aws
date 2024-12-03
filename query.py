'''
include quering by catalog format (fix webscrape first to include the right one) fo analysis and better visualizaitons
when i fo this i also want to do the filtering before i send a prompt to openai api so that diff params are given and different info is 
looked for in addition to summary and astronomy terms like ra, declination, etc 
'''
import sqlite3
import pandas as pd
import json

def display_table(db_path, table_name):
    conn = sqlite3.connect(db_path)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def find_terms_in_multiple_documents(db_path, min_docs=2):
    conn = sqlite3.connect(db_path)
    query = """
        SELECT t.term, COUNT(dt.document_id) AS document_count
        FROM Terms t
        JOIN DocumentTerms dt ON t.term_id = dt.term_id
        GROUP BY t.term_id, t.term
        HAVING document_count >= ?;
    """
    df = pd.read_sql_query(query, conn, params=(min_docs,))
    conn.close()
    return df


def fetch_documents_by_term(db_path, term):
    # fix this its fetching dupes 
    conn = sqlite3.connect(db_path)
    query = """
    SELECT d.document_id, d.page_num, d.catalog_id, d.title, d.author, d.date, d.summary
    FROM Documents d
    JOIN DocumentTerms dt ON d.document_id = dt.document_id
    JOIN Terms t ON dt.term_id = t.term_id
    WHERE t.term = ?
    """
    df = pd.read_sql_query(query, conn, params=(term,))
    conn.close()
    return df

# Function to fetch all terms
def fetch_all_terms(db_path):
    conn = sqlite3.connect(db_path)
    query = """
    SELECT term FROM Terms 
    ORDER BY term ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df['term'].tolist()

def fetch_documents_by_partial_term(db_path, term):
    conn = sqlite3.connect(db_path)
    query = """
    SELECT d.page_num, d.catalog_id, d.title, d.author, d.date, d.summary
    FROM Documents d
    JOIN DocumentTerms dt ON d.document_id = dt.document_id
    JOIN Terms t ON dt.term_id = t.term_id
    WHERE t.term LIKE ? OR d.author LIKE ? OR d.title LIKE ? OR d.summary LIKE ?
    """
    # Add wildcards around the search term for partial matching
    # df = pd.read_sql_query(query, conn, params=(f"%{term}%",))
    search_param = f"%{term}%"
    df = pd.read_sql_query(query, conn, params=(search_param, search_param, search_param, search_param))
    conn.close()
    return df


def fetch_types(db_path):
    # i could use this query to classifiy which passages i will do full text extraction with 
    # or just make visualization for everything bt glass plate envelopes and glass plates 
    conn = sqlite3.connect(db_path)
    query = "SELECT format FROM Catalogs"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df['format'].tolist()



# fetch by type of documents for the analysis and make that a widget 
# time analysis of main themes 
# line plot of terms 
# sumamry vecotr embeddings and networks 



# this is for visualizing the bigram
def fetch_terms_per_doc(db_path):
    conn = sqlite3.connect(db_path)
    query = "SELECT astronomy_terms FROM Documents"
    df = pd.read_sql_query(query, conn)
    conn.close()
    # return df['astronomy_terms'].tolist()
    # Deserialize JSON strings into Python lists
    df['astronomy_terms'] = df['astronomy_terms'].apply(json.loads)
    # print(df)
    return df['astronomy_terms'].tolist()  # Return as a list of lists
    # return df 

# this is for visualizing as well 
def get_terms_over_time(db_path):
    conn = sqlite3.connect(db_path)
    query = "SELECT date, astronomy_terms FROM Documents"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df



# def main():
#     print(fetch_terms_per_doc(db_path="starchive2.db"))
#     # db_path="starchive2.db"
#     # print(display_table(db_path, table_name="Documents"))
#     # conn = sqlite3.connect(db_path)
#     # df = pd.read_sql_query("SELECT document_id, astronomy_terms FROM Documents", conn)
#     # print(df)
#     # conn.close()
# main()

# def main():
#     db_path = "starchive.db"
#     tables = ["Documents", "Catalogs", "Terms", "DocumentTerms"]

#     # for table in tables:
#         # print(f"Table: {table}")
#         # df = display_table(db_path, table)
#         # print(df)
#         # print("\n")

#     # terms_in_multiple_docs = find_terms_in_multiple_documents(db_path, min_docs=2)
#     # print(terms_in_multiple_docs)

#     print(fetch_types(db_path))

#     # process the ten catalogs  after i set everything up in ood 

# if __name__ == "__main__":
#     main()
