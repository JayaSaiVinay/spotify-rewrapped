import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to MySQL Server

conn = mysql.connector.connect(
    host="localhost",
    user="root",  # Change this to your MySQL username
    password="root",  # Change this to your MySQL password
    database="spotify_db"  # Change this to your database name
)

# Create a cursor object
cursor = conn.cursor()

# Example Query: Fetching top 10 most played songs
query = """
SELECT track_name, COUNT(*) as play_count 
FROM spotify_history 
GROUP BY track_name 
ORDER BY play_count DESC 
LIMIT 10;
"""
cursor.execute(query)

# Load data into a Pandas DataFrame
data = pd.DataFrame(cursor.fetchall(), columns=['Track', 'Play Count'])

# Close the connection
cursor.close()
conn.close()

# Plot the data
plt.figure(figsize=(10, 5))
sns.barplot(x='Play Count', y='Track', data=data, palette='viridis')
plt.xlabel("Number of Plays")
plt.ylabel("Song")
plt.title("Top 10 Most Played Songs")
plt.show()
