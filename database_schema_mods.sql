-- Table: workorders
CREATE TABLE workorders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'uploaded',
    original_file_path TEXT NOT NULL
);

-- Table: leads
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workorder_id INTEGER,
    data JSON NOT NULL,
    FOREIGN KEY(workorder_id) REFERENCES workorders(id)
);

-- Add raw_webpage_text column to leads table
ALTER TABLE leads ADD COLUMN raw_webpage_text TEXT;

-- Add buyer_persona column to leads table
ALTER TABLE leads ADD COLUMN buyer_persona TEXT;

-- Add buyer_persona_embedding column as EMBEDDING type (1536 is the dimension for text-embedding-3-small)
ALTER TABLE leads ADD COLUMN buyer_persona_embedding EMBEDDING(1536);

-- Add cluster_id column to leads table
ALTER TABLE leads ADD COLUMN cluster_id INTEGER;

-- Add company_name column to leads table
ALTER TABLE leads ADD COLUMN company_name TEXT;

-- Add display_order column to leads table
ALTER TABLE leads ADD COLUMN display_order INTEGER;

-- Add status column to leads table for tracking lead processing state
ALTER TABLE leads ADD COLUMN status TEXT DEFAULT 'unchecked';