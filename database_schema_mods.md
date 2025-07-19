# Database Schema Modifications

## Initial Schema

### Table: workorders
- id: integer, primary key
- filename: string, name of uploaded file
- upload_date: datetime, when file was uploaded
- status: string, status of workorder (e.g., uploaded, processing, done)
- original_file_path: string, path to uploaded file

### Table: leads
- id: integer, primary key
- workorder_id: integer, foreign key to workorders.id
- data: JSON, all lead attributes as key-value pairs 

## Added field to Lead model
- **raw_webpage_text** (`Text`, nullable): Stores the raw text extracted from the lead's company website (scraped or found via TavilySearch API).

This field is used to store the text content of the company website for each lead, either scraped directly if a website is provided, or found via TavilySearch API if not. 

- **buyer_persona** (`Text`, nullable): Stores the generated buyer persona string for the lead, created using the company webpage text and OpenAI GPT-4o-mini. 

- **buyer_persona_embedding** (`Text`, nullable): Stores the vector embedding (as a JSON string) of the generated buyer persona for the lead, created using OpenAI's embedding model and stored for use with sqlite-vec. 

- **cluster_id** (`Integer`, nullable): Stores the cluster ID assigned to the lead by the clustering algorithm (HDBSCAN). -1 means noise/outlier. 

- **company_name** (`String`, nullable): Stores the company name for the lead, extracted from the data JSON (using 'Company' or similar key). 

- **display_order** (`Integer`, nullable): Stores the persistent display order of the lead within a workorder for reranking. 

- **status** (`String`, nullable): Stores the current status of the lead (unchecked, converted, failed, in-progress). Used for tracking lead processing state and enabling reranking based on user feedback. 