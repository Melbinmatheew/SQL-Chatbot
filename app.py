import streamlit as st
import os
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai
import re
import pandas as pd
import graphviz

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get Gemini response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt + "\n\nQuestion: " + question)
    return response.text

# Function to clean the SQL query
def clean_sql_query(query):
    cleaned_query = re.sub(r'```sql|```', '', query).strip()
    cleaned_query = re.sub(r'^SQL:\s*', '', cleaned_query, flags=re.IGNORECASE)
    return cleaned_query

# Function to execute SQL query and return results as a DataFrame
def execute_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        if df.empty:
            st.warning("The query returned no results.")
        return df
    except sqlite3.Error as e:
        st.error(f"An error occurred while executing the query: {e}")
        st.error(f"The problematic SQL was: {sql}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

# Function to get table names from the database
def get_table_names(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return [table[0] for table in tables]

# Function to get table schema
def get_table_schema(db, table_name):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()
    conn.close()
    return schema

# Function to get table data
def get_table_data(db, table_name, limit=100):
    conn = sqlite3.connect(db)
    query = f"SELECT * FROM {table_name} LIMIT {limit}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Define the prompt for Gemini AI
prompt = """
You are an expert in converting English questions to SQL queries!
The SQL database has the following schema:
      CREATE TABLE `Album`
   (
      `AlbumId` INT NOT NULL,
      `Title` NVARCHAR(160) NOT NULL,
      `ArtistId` INT NOT NULL,
      CONSTRAINT `PK_Album` PRIMARY KEY  (`AlbumId`)
   );

   CREATE TABLE `Artist`
   (
      `ArtistId` INT NOT NULL,
      `Name` NVARCHAR(120),
      CONSTRAINT `PK_Artist` PRIMARY KEY  (`ArtistId`)
   );

   CREATE TABLE `Customer`
   (
      `CustomerId` INT NOT NULL,
      `FirstName` NVARCHAR(40) NOT NULL,
      `LastName` NVARCHAR(20) NOT NULL,
      `Company` NVARCHAR(80),
      `Address` NVARCHAR(70),
      `City` NVARCHAR(40),
      `State` NVARCHAR(40),
      `Country` NVARCHAR(40),
      `PostalCode` NVARCHAR(10),
      `Phone` NVARCHAR(24),
      `Fax` NVARCHAR(24),
      `Email` NVARCHAR(60) NOT NULL,
      `SupportRepId` INT,
      CONSTRAINT `PK_Customer` PRIMARY KEY  (`CustomerId`)
   );

   CREATE TABLE `Employee`
   (
      `EmployeeId` INT NOT NULL,
      `LastName` NVARCHAR(20) NOT NULL,
      `FirstName` NVARCHAR(20) NOT NULL,
      `Title` NVARCHAR(30),
      `ReportsTo` INT,
      `BirthDate` DATETIME,
      `HireDate` DATETIME,
      `Address` NVARCHAR(70),
      `City` NVARCHAR(40),
      `State` NVARCHAR(40),
      `Country` NVARCHAR(40),
      `PostalCode` NVARCHAR(10),
      `Phone` NVARCHAR(24),
      `Fax` NVARCHAR(24),
      `Email` NVARCHAR(60),
      CONSTRAINT `PK_Employee` PRIMARY KEY  (`EmployeeId`)
   );

   CREATE TABLE `Genre`
   (
      `GenreId` INT NOT NULL,
      `Name` NVARCHAR(120),
      CONSTRAINT `PK_Genre` PRIMARY KEY  (`GenreId`)
   );

   CREATE TABLE `Invoice`
   (
      `InvoiceId` INT NOT NULL,
      `CustomerId` INT NOT NULL,
      `InvoiceDate` DATETIME NOT NULL,
      `BillingAddress` NVARCHAR(70),
      `BillingCity` NVARCHAR(40),
      `BillingState` NVARCHAR(40),
      `BillingCountry` NVARCHAR(40),
      `BillingPostalCode` NVARCHAR(10),
      `Total` NUMERIC(10,2) NOT NULL,
      CONSTRAINT `PK_Invoice` PRIMARY KEY  (`InvoiceId`)
   );

   CREATE TABLE `InvoiceLine`
   (
      `InvoiceLineId` INT NOT NULL,
      `InvoiceId` INT NOT NULL,
      `TrackId` INT NOT NULL,
      `UnitPrice` NUMERIC(10,2) NOT NULL,
      `Quantity` INT NOT NULL,
      CONSTRAINT `PK_InvoiceLine` PRIMARY KEY  (`InvoiceLineId`)
   );

   CREATE TABLE `MediaType`
   (
      `MediaTypeId` INT NOT NULL,
      `Name` NVARCHAR(120),
      CONSTRAINT `PK_MediaType` PRIMARY KEY  (`MediaTypeId`)
   );

   CREATE TABLE `Playlist`
   (
      `PlaylistId` INT NOT NULL,
      `Name` NVARCHAR(120),
      CONSTRAINT `PK_Playlist` PRIMARY KEY  (`PlaylistId`)
   );

   CREATE TABLE `PlaylistTrack`
   (
      `PlaylistId` INT NOT NULL,
      `TrackId` INT NOT NULL,
      CONSTRAINT `PK_PlaylistTrack` PRIMARY KEY  (`PlaylistId`, `TrackId`)
   );

   CREATE TABLE `Track`
   (
      `TrackId` INT NOT NULL,
      `Name` NVARCHAR(200) NOT NULL,
      `AlbumId` INT,
      `MediaTypeId` INT NOT NULL,
      `GenreId` INT,
      `Composer` NVARCHAR(220),
      `Milliseconds` INT NOT NULL,
      `Bytes` INT,
      `UnitPrice` NUMERIC(10,2) NOT NULL,
      CONSTRAINT `PK_Track` PRIMARY KEY  (`TrackId`)
   );



   /*******************************************************************************
      Create Primary Key Unique Indexes
   ********************************************************************************/

   /*******************************************************************************
      Create Foreign Keys
   ********************************************************************************/
   ALTER TABLE `Album` ADD CONSTRAINT `FK_AlbumArtistId`
      FOREIGN KEY (`ArtistId`) REFERENCES `Artist` (`ArtistId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_AlbumArtistId` ON `Album` (`ArtistId`);

   ALTER TABLE `Customer` ADD CONSTRAINT `FK_CustomerSupportRepId`
      FOREIGN KEY (`SupportRepId`) REFERENCES `Employee` (`EmployeeId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_CustomerSupportRepId` ON `Customer` (`SupportRepId`);

   ALTER TABLE `Employee` ADD CONSTRAINT `FK_EmployeeReportsTo`
      FOREIGN KEY (`ReportsTo`) REFERENCES `Employee` (`EmployeeId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_EmployeeReportsTo` ON `Employee` (`ReportsTo`);

   ALTER TABLE `Invoice` ADD CONSTRAINT `FK_InvoiceCustomerId`
      FOREIGN KEY (`CustomerId`) REFERENCES `Customer` (`CustomerId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_InvoiceCustomerId` ON `Invoice` (`CustomerId`);

   ALTER TABLE `InvoiceLine` ADD CONSTRAINT `FK_InvoiceLineInvoiceId`
      FOREIGN KEY (`InvoiceId`) REFERENCES `Invoice` (`InvoiceId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_InvoiceLineInvoiceId` ON `InvoiceLine` (`InvoiceId`);

   ALTER TABLE `InvoiceLine` ADD CONSTRAINT `FK_InvoiceLineTrackId`
      FOREIGN KEY (`TrackId`) REFERENCES `Track` (`TrackId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_InvoiceLineTrackId` ON `InvoiceLine` (`TrackId`);

   ALTER TABLE `PlaylistTrack` ADD CONSTRAINT `FK_PlaylistTrackPlaylistId`
      FOREIGN KEY (`PlaylistId`) REFERENCES `Playlist` (`PlaylistId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_PlaylistTrackPlaylistId` ON `PlaylistTrack` (`PlaylistId`);

   ALTER TABLE `PlaylistTrack` ADD CONSTRAINT `FK_PlaylistTrackTrackId`
      FOREIGN KEY (`TrackId`) REFERENCES `Track` (`TrackId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_PlaylistTrackTrackId` ON `PlaylistTrack` (`TrackId`);

   ALTER TABLE `Track` ADD CONSTRAINT `FK_TrackAlbumId`
      FOREIGN KEY (`AlbumId`) REFERENCES `Album` (`AlbumId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_TrackAlbumId` ON `Track` (`AlbumId`);

   ALTER TABLE `Track` ADD CONSTRAINT `FK_TrackGenreId`
      FOREIGN KEY (`GenreId`) REFERENCES `Genre` (`GenreId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_TrackGenreId` ON `Track` (`GenreId`);

   ALTER TABLE `Track` ADD CONSTRAINT `FK_TrackMediaTypeId`
      FOREIGN KEY (`MediaTypeId`) REFERENCES `MediaType` (`MediaTypeId`) ON DELETE NO ACTION ON UPDATE NO ACTION;

   CREATE INDEX `IFK_TrackMediaTypeId` ON `Track` (`MediaTypeId`);
  Example 1: List all the albums and their associated artist names.
   SQL: SELECT Album.Title, Artist.Name FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId;

   Example 2: Find all customers who have made an invoice and show their full name along with the total invoice amount.
   SQL: SELECT Customer.FirstName, Customer.LastName, Invoice.Total FROM Customer JOIN Invoice ON Customer.CustomerId = Invoice.CustomerId;

   Example 3: Display the employees who report to other employees along with their supervisors' names.
   SQL: SELECT e1.FirstName AS EmployeeFirstName, e1.LastName AS EmployeeLastName, e2.FirstName AS SupervisorFirstName, e2.LastName AS SupervisorLastName FROM Employee e1 JOIN Employee e2 ON e1.ReportsTo = e2.EmployeeId;

  Please provide the SQL query for the following question. Return only the SQL query without any additional text or formatting:
"""

# Streamlit app layout
st.set_page_config(page_title="Chinook Database Explorer & Chatbot", layout="wide")

# Custom CSS for dark theme
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #121212;
    }
    
    /* Secondary background */
    .stSidebar, .stTextInput, .stTextArea, .stSelectbox, .stDataFrame {
        background-color: #1E1E1E !important;
    }
    
    /* Text color */
    body, p, .stMarkdown, .stSelectbox, .stTextInput, .stTextArea {
        color: #E0E0E0 !important;
    }
    
    /* Accent colors */
    .stButton>button, .stDownloadButton>button {
        background-color: #1A73E8 !important;
        color: white !important;
    }
    
    /* Borders and dividers */
    .stSidebar, .stTextInput, .stTextArea, .stSelectbox {
        border-color: #333333 !important;
    }
    
    /* Error states */
    .stAlert {
        background-color: #EA4335 !important;
        color: white !important;
    }
    
    /* Interactive elements */
    .stSelectbox:hover, .stTextInput:hover, .stTextArea:hover {
        border-color: #1A73E8 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        color: #E0E0E0 !important;
    }
    .dataframe th {
        background-color: #1A73E8 !important;
        color: white !important;
    }
    .dataframe td {
        background-color: #222222 !important;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: #1E1E1E !important;
        color: #E0E0E0 !important;
    }
    </style>
""", unsafe_allow_html=True)


# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Database Information", "Database Explorer", "SQL Query Chatbot"])

# Main content area
if page == "Database Information":
    st.title("Database Information")
    
    # Load or initialize the database information
    if 'db_info' not in st.session_state:
        st.session_state.db_info = """
        The Chinook database represents a digital media store, including tables for artists, albums, media tracks, invoices, and customers. 
        
        Key tables include:
        - Artist: Contains artist information
        - Album: Stores album details
        - Track: Includes information about individual songs
        - Customer: Contains customer data
        - Invoice: Stores sales information
        
        Below, you can find an Entity-Relationship Diagram (ERD) showing the relationships between tables.
        """

    # Editable text area for database information
    st.session_state.db_info = st.text_area(
        "Database Information:",
        st.session_state.db_info,
        height=300
    )
    
    st.info("Any changes you make to the text above are automatically saved.")

    # Entity-Relationship Diagram using graphviz
    st.subheader("Entity-Relationship Diagram")
    
    graph = graphviz.Digraph()
    graph.attr(rankdir='LR')

    # Add nodes
    tables = ["Artist", "Album", "Track", "MediaType", "Genre", "Playlist", "Customer", "Invoice", "InvoiceLine", "Employee"]
    for table in tables:
        graph.node(table)

    # Add edges
    graph.edge("Artist", "Album", "creates")
    graph.edge("Album", "Track", "contains")
    graph.edge("Track", "MediaType", "has")
    graph.edge("Track", "Genre", "belongs to")
    graph.edge("Playlist", "Track", "includes")
    graph.edge("Customer", "Invoice", "places")
    graph.edge("Invoice", "InvoiceLine", "contains")
    graph.edge("Track", "InvoiceLine", "appears in")
    graph.edge("Employee", "Customer", "supports")

    st.graphviz_chart(graph)
    
    st.write("""
    This diagram shows the relationships between the main tables in the Chinook database:
    - An Artist creates multiple Albums
    - An Album contains multiple Tracks
    - A Track has one MediaType and belongs to one Genre
    - A Track can be in multiple Playlists, and a Playlist can have multiple Tracks
    - A Customer places multiple Invoices
    - An Invoice contains multiple InvoiceLines
    - A Track appears in multiple InvoiceLines
    - An Employee supports multiple Customers
    """)

elif page == "Database Explorer":
    st.title("Database Explorer")

    # Show available tables in the sidebar
    st.sidebar.header("Table Selection")
    tables = get_table_names("Chinook_Sqlite.sqlite")
    selected_table = st.sidebar.selectbox("Select a table to view its schema and data", tables)

    if selected_table:
        # Display schema
        st.subheader(f"Schema for {selected_table}")
        schema = get_table_schema("Chinook_Sqlite.sqlite", selected_table)
        schema_df = pd.DataFrame(schema, columns=["Column ID", "Column Name", "Data Type", "Nullable", "Default Value", "Primary Key"])
        st.dataframe(schema_df)
        
        # Display table data
        st.subheader(f"Data Preview for {selected_table}")
        table_data = get_table_data("Chinook_Sqlite.sqlite", selected_table)
        st.dataframe(table_data)

elif page == "SQL Query Chatbot":
    st.title("SQL Query Chatbot")

    # Example queries in the sidebar
    st.sidebar.subheader("Example Queries")
    example_queries = {
        "List all albums with their artists": "SELECT Album.Title, Artist.Name FROM Album JOIN Artist ON Album.ArtistId = Artist.ArtistId LIMIT 10",
        "Top 5 genres by number of tracks": "SELECT Genre.Name, COUNT(*) as TrackCount FROM Track JOIN Genre ON Track.GenreId = Genre.GenreId GROUP BY Genre.GenreId ORDER BY TrackCount DESC LIMIT 5",
        "Total sales by country": "SELECT BillingCountry, SUM(Total) as TotalSales FROM Invoice GROUP BY BillingCountry ORDER BY TotalSales DESC",
        "Customers who spent more than $40": "SELECT Customer.FirstName, Customer.LastName, SUM(Invoice.Total) as TotalSpent FROM Customer JOIN Invoice ON Customer.CustomerId = Invoice.CustomerId GROUP BY Customer.CustomerId HAVING TotalSpent > 40 ORDER BY TotalSpent DESC",
        "Tracks longer than 5 minutes": "SELECT Name, Milliseconds/60000.0 as Minutes FROM Track WHERE Milliseconds > 300000 ORDER BY Milliseconds DESC LIMIT 10"
    }

    selected_example = st.sidebar.selectbox("Select an example query:", list(example_queries.keys()))
    st.sidebar.code(example_queries[selected_example], language='sql')
    
    if st.sidebar.button("Use Selected Example"):
        st.session_state.current_sql = example_queries[selected_example]
        st.session_state.history.append((selected_example, example_queries[selected_example]))

    # Main area for chatbot interaction
    st.subheader("Enter Your Query")
    question = st.text_input("Enter your question about the Chinook database or write an SQL query:")

    if 'history' not in st.session_state:
        st.session_state.history = []

    if st.button("Generate SQL"):
        if question:
            # Generate SQL query
            generated_sql = get_gemini_response(question, prompt)
            cleaned_sql = clean_sql_query(generated_sql)
            st.session_state.current_sql = cleaned_sql
            st.session_state.history.append((question, cleaned_sql))
        else:
            st.warning("Please enter a question or select an example query.")

    # SQL query editor and Execute button
    if 'current_sql' in st.session_state:
        st.subheader("SQL Query:")
        sql_editor = st.text_area("Edit SQL if needed:", value=st.session_state.current_sql, height=150)

        if st.button("Execute SQL"):
            results_df = execute_sql_query(sql_editor, "Chinook_Sqlite.sqlite")
            if not results_df.empty:
                st.subheader("Query Results:")
                st.write(f"Number of rows returned: {len(results_df)}")

                # Full-screen result display
                st.dataframe(results_df, use_container_width=True)

                # Download button for CSV
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                )

    # Display query history
    st.subheader("Query History")
    for i, (q, sql) in enumerate(st.session_state.history):
        with st.expander(f"Query {i+1}: {q}"):
            st.code(sql, language="sql")

# About section in sidebar
st.sidebar.header("About")
st.sidebar.info("This app allows you to view database information and relationships, explore the Chinook database tables, and use a chatbot to generate SQL queries.")
