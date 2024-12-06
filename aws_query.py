import pandas as pd
import pymysql
import json
import os 

# RDS Connection Function
def get_rds_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=3306
    )

def display_table(table_name):
    conn = get_rds_connection()
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def find_terms_in_multiple_documents(min_docs=2):
    conn = get_rds_connection()
    query = """
        SELECT t.term, COUNT(dt.document_id) AS document_count
        FROM Terms t
        JOIN DocumentTerms dt ON t.term_id = dt.term_id
        GROUP BY t.term_id, t.term
        HAVING document_count >= %s;
    """
    df = pd.read_sql_query(query, conn, params=(min_docs,))
    conn.close()
    return df

def fetch_documents_by_term(term):
    conn = get_rds_connection()
    query = """
        SELECT d.document_id, d.page_num, d.catalog_id, d.title, d.author, d.date, d.summary
        FROM Documents d
        JOIN DocumentTerms dt ON d.document_id = dt.document_id
        JOIN Terms t ON dt.term_id = t.term_id
        WHERE t.term = %s
    """
    df = pd.read_sql_query(query, conn, params=(term,))
    conn.close()
    return df

def fetch_all_terms():
    conn = get_rds_connection()
    query = """
        SELECT term FROM Terms 
        ORDER BY term ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df['term'].tolist()

def fetch_documents_by_partial_term(term):
    conn = get_rds_connection()
    query = """
        SELECT d.page_num, d.catalog_id, d.title, d.author, d.date, d.summary
        FROM Documents d
        JOIN DocumentTerms dt ON d.document_id = dt.document_id
        JOIN Terms t ON dt.term_id = t.term_id
        WHERE t.term LIKE %s OR d.author LIKE %s OR d.title LIKE %s OR d.summary LIKE %s
    """
    search_param = f"%{term}%"
    df = pd.read_sql_query(query, conn, params=(search_param, search_param, search_param, search_param))
    conn.close()
    return df

def fetch_types():
    conn = get_rds_connection()
    query = "SELECT format FROM Catalogs"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df['format'].tolist()

def fetch_terms_per_doc():
    conn = get_rds_connection()
    query = "SELECT astronomy_terms FROM Documents"
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['astronomy_terms'] = df['astronomy_terms'].apply(json.loads)
    return df['astronomy_terms'].tolist()

def get_terms_over_time():
    conn = get_rds_connection()
    query = "SELECT date, astronomy_terms FROM Documents"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
