import sqlite3
import json

def insert_document(db_path, json_data, catalog_metadata):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert catalog metadata
    catalog_id = catalog_metadata["Identifier"]
    cursor.execute(
        """
        INSERT OR IGNORE INTO Catalogs (catalog_id, title, subject, description, author, date, format, type, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            catalog_id,
            catalog_metadata.get("Title", ""),
            catalog_metadata.get("Subject", ""),
            catalog_metadata.get("Description", ""),
            catalog_metadata.get("Creator", ""),
            catalog_metadata.get("Date", ""),
            catalog_metadata.get("Format", ""),
            catalog_metadata.get("Type", ""),
            catalog_metadata.get("pdf_url", ""),
        )
    )

    terms_list_json = json.dumps(json_data["astronomy_terms"])
    # print(terms_list_json)
    # Insert document data
    cursor.execute(
        """
        INSERT OR IGNORE INTO Documents (page_num, catalog_id, author, title, date, summary, astronomy_terms)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            json_data["page_num"],
            catalog_id,
            json_data["metadata"]["author"],
            json_data["metadata"]["title"],
            json_data["metadata"]["date"],
            json_data["summary"],
            terms_list_json
        )
    )

    document_id = cursor.lastrowid  # Get the newly inserted document ID

    # Insert terms and build inverted index
    for term in json_data["astronomy_terms"]:
        # Insert term if it doesn't exist
        cursor.execute("INSERT OR IGNORE INTO Terms (term) VALUES (?)", (term,))
        cursor.execute("SELECT term_id FROM Terms WHERE term = ?", (term,))
        term_id = cursor.fetchone()[0]

        # Link term to document
        cursor.execute(
            "INSERT INTO DocumentTerms (term_id, document_id) VALUES (?, ?)",
            (term_id, document_id),
        )


    conn.commit()
    conn.close()
    print(f"Document '{json_data['metadata']['title']}' inserted successfully!")


# def delete_duplicates(db_path):
#     # this is for testing (will not need in finalized version)
#     query = """
#     DELETE FROM Documents
#     WHERE rowid NOT IN (
#         SELECT MIN(rowid)
#         FROM Documents
#         GROUP BY page_num, catalog_id
#     );
#     """
#     with sqlite3.connect(db_path) as conn:
#         cursor = conn.cursor()
#         # Enable foreign key support
#         cursor.execute("PRAGMA foreign_keys = ON;")
#         cursor.execute(query)
#         conn.commit()
#     print("Duplicate entries removed.")
def clear_db(db_path="starchive2.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.executescript("""
        DELETE FROM DocumentTerms;
        DELETE FROM Terms;
        DELETE FROM Documents;
        DELETE FROM Catalogs;
        VACUUM;  -- Optional: Reset auto-increment IDs
    """)
    
    conn.commit()
    conn.close()
    print("Database cleared successfully!")

