import sqlite3
if __name__ == "__main__":
    # Connect to sqlite database (creates file if it doesn't exist)
    conn = sqlite3.connect("starchive.db")
    cursor = conn.cursor()

    # schema creation
    schema = """
    CREATE TABLE IF NOT EXISTS Documents (
        document_id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_num INTEGER, 
        catalog_id TEXT,                             
        author TEXT,
        title TEXT,
        date DATE,
        summary TEXT,
        FOREIGN KEY (catalog_id) REFERENCES Catalogs(catalog_id)
    );

    CREATE TABLE IF NOT EXISTS Terms (
        term_id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS DocumentTerms (
        term_id INTEGER,
        document_id INTEGER,
        FOREIGN KEY (term_id) REFERENCES Terms(term_id),
        FOREIGN KEY (document_id) REFERENCES Documents(document_id)
    );

    CREATE TABLE IF NOT EXISTS Catalogs (
        catalog_id TEXT PRIMARY KEY,
        title TEXT,
        subject TEXT,
        description TEXT,
        author TEXT, 
        date DATE,
        format TEXT, 
        type TEXT,
        url TEXT
    );
    """

    cursor.executescript(schema)
    conn.commit()
    conn.close()

    print("Database and tables created successfully!")
