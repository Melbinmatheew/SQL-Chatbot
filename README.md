# Database Explorer Chatbot

## Overview
This Streamlit application provides an interactive interface for exploring and querying a SQLite database (Chinook) using natural language. It features a chatbot powered by Google's Generative AI (Gemini) to convert English questions into SQL queries.

## Features
1. **Database Information**: View and edit general information about the database structure.
2. **Entity-Relationship Diagram**: Visualize the relationships between different tables in the database.
3. **Database Explorer**: Browse available tables, view their schemas, and preview data.
4. **SQL Query Chatbot**: Generate SQL queries from natural language questions and execute them.
5. **Query History**: Keep track of previously executed queries.

## Installation

### Prerequisites
- Python 3.7+
- pip

### Steps
1. Clone the repository:
   ```
   git clone https://github.com/your-username/database-explorer-chatbot.git
   cd database-explorer-chatbot
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the project root and add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

4. Ensure you have the Chinook SQLite database file (`Chinook_Sqlite.sqlite`) in the project directory.

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Use the sidebar to navigate between different sections of the app:
   - Database Information
   - Database Explorer
   - SQL Query Chatbot

4. In the SQL Query Chatbot section:
   - Enter your question in natural language or write an SQL query.
   - Use example queries from the sidebar for quick starts.
   - Edit generated SQL if needed and execute queries.
   - View and download query results.

## Dependencies
- streamlit
- pandas
- sqlite3
- google-generativeai
- python-dotenv
- graphviz

## Database Schema
The app uses the Chinook database, which represents a digital media store. Key tables include:
- Artist
- Album
- Track
- Customer
- Invoice
- Employee

Refer to the Entity-Relationship Diagram in the app for a visual representation of table relationships.

## Customization
- To use a different database, replace `Chinook_Sqlite.sqlite` with your database file and update the schema information in the `prompt` variable.
- Modify the `get_gemini_response` function to use a different AI model if needed.

## Troubleshooting
- If you encounter issues with API key authentication, ensure your `.env` file is correctly set up and the `GOOGLE_API_KEY` is valid.
- For database-related errors, verify that the `Chinook_Sqlite.sqlite` file is present and accessible.

## Contributing
Contributions to improve the app are welcome. Please fork the repository and submit a pull request with your changes.


## Acknowledgements
- Chinook Database: [https://github.com/lerocha/chinook-database](https://github.com/lerocha/chinook-database)
- Google Generative AI: [https://ai.google.dev/](https://ai.google.dev/)
- Streamlit: [https://streamlit.io/](https://streamlit.io/)
