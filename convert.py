import sqlite3

def export_urls_to_txt(db_path, txt_file_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query all URLs from the database
    cursor.execute('SELECT url FROM urls')
    urls = cursor.fetchall()  # Fetch all results
    
    # Write URLs to a text file with UTF-8 encoding
    with open(txt_file_path, 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(url[0] + '\n')  # url[0] because fetchall returns a list of tuples
    
    # Close the database connection
    conn.close()
    print(f"Data has been exported to {txt_file_path}")

# Specify the paths
db_path = 'urls.db'  # Path to your SQLite database
txt_file_path = 'exported_urls.txt'  # Desired path for the text file

# Run the function to export data
export_urls_to_txt(db_path, txt_file_path)
