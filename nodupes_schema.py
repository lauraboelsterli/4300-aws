import sqlite3
if __name__ == "__main__":
    # Connect to sqlite database (creates file if it doesn't exist)
    conn = sqlite3.connect("starchive2.db")
    cursor = conn.cursor()

    # Schema creation
    schema = """
    CREATE TABLE IF NOT EXISTS Documents (
        document_id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_num INTEGER NOT NULL, 
        catalog_id TEXT NOT NULL,                             
        author TEXT,
        title TEXT,
        date DATE,
        summary TEXT,
        astronomy_terms TEXT,
        FOREIGN KEY (catalog_id) REFERENCES Catalogs(catalog_id),
        UNIQUE(page_num, catalog_id) -- Prevent duplicate entries with the same page_num and catalog_id
    );

    CREATE TABLE IF NOT EXISTS Terms (
        term_id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT UNIQUE -- Prevent duplicate terms
    );

    CREATE TABLE IF NOT EXISTS DocumentTerms (
        term_id INTEGER NOT NULL,
        document_id INTEGER NOT NULL,
        FOREIGN KEY (term_id) REFERENCES Terms(term_id),
        FOREIGN KEY (document_id) REFERENCES Documents(document_id) ON DELETE CASCADE,
        UNIQUE(term_id, document_id) -- Prevent duplicate term-document relationships
    );

    CREATE TABLE IF NOT EXISTS Catalogs (
        catalog_id TEXT PRIMARY KEY, -- Prevent duplicate catalog entries
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
