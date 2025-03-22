from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    return mysql.connector.connect(host='localhost', user='root', passwd='root', database='spotify')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and (file.filename.endswith('.csv') or file.filename.endswith('.json')):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file.filename.endswith('.json'):
                try:
                    df = pd.read_json(file_path)
                except Exception as e:
                    return f"Error reading JSON file: {e}", 400
            
            df.columns = df.columns.str.strip()
            
            mydb = get_db_connection()
            mycursor = mydb.cursor()
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS listening_data (
                endTime DATETIME,
                artistName VARCHAR(255),
                trackName VARCHAR(255),
                msPlayed INT
            )
            """
            mycursor.execute(create_table_sql)
            mydb.commit()
            
            mycursor.execute("DELETE FROM listening_data")
            mydb.commit()
            
            for _, row in df.iterrows():
                sql = "INSERT INTO listening_data (endTime, artistName, trackName, msPlayed) VALUES (%s, %s, %s, %s)"
                val = (row['endTime'], row['artistName'], row['trackName'], row['msPlayed'])
                mycursor.execute(sql, val)
            
            mydb.commit()
            mycursor.close()
            mydb.close()
            
            return redirect(url_for('insights'))
        else:
            return "Please upload a CSV or JSON file.", 400
    return render_template('upload.html')

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/top_tracks')
def top_tracks():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    sql = """
    SELECT trackName, artistName, SUM(msPlayed) / 60000 AS totalMinutes
    FROM listening_data
    GROUP BY artistName, trackName
    ORDER BY totalMinutes DESC
    LIMIT 10;
    """
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return render_template('top_tracks.html', top_tracks=result)

@app.route('/top_tracks_removing_night')
def top_tracks_removing_night():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    sql = """
    SELECT trackName, artistName, SUM(msPlayed) / 60000 AS totalMinutes
    FROM listening_data
    WHERE HOUR(endTime) NOT BETWEEN 0 AND 5
    GROUP BY artistName, trackName
    ORDER BY totalMinutes DESC
    LIMIT 10;
    """
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return render_template('top_tracks_removing_night.html', top_tracks=result)

@app.route('/top_tracks_by_count')
def top_tracks_by_count():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    sql = """
    SELECT trackName, artistName, COUNT(*) AS play_count
    FROM listening_data
    GROUP BY trackName, artistName
    ORDER BY play_count DESC
    LIMIT 10;
    """
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return render_template('top_tracks_by_count.html', tracks=result)


@app.route('/top_artists_by_time')
def top_artists_by_time():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    sql = """
    SELECT artistName, SUM(msPlayed) / 60000 AS totalTime
    FROM listening_data
    GROUP BY artistName
    ORDER BY totalTime DESC
    LIMIT 10;
    """
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return render_template('top_artists_by_time.html', top_artists=result)

@app.route('/top_artists_by_count')
def top_artists_by_count():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    sql = """
    SELECT artistName, COUNT(*) AS play_count
    FROM listening_data
    GROUP BY artistName
    ORDER BY play_count DESC
    LIMIT 10;
    """
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return render_template('top_artists_by_count.html', top_artists=result)


@app.route('/top_months')
def top_months():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    sql = """
    SELECT DATE_FORMAT(endTime, '%Y-%m') AS month, SUM(msPlayed) / 60000 AS total_minutes
    FROM listening_data
    GROUP BY month
    ORDER BY total_minutes DESC
    LIMIT 10;
    """
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return render_template('top_months.html', months=result)

@app.route('/listening_time_distribution')
def listening_time_distribution():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    sql = """
    SELECT 
        CASE 
            WHEN HOUR(endTime) BETWEEN 5 AND 11 THEN 'Morning'
            WHEN HOUR(endTime) BETWEEN 12 AND 17 THEN 'Afternoon'
            WHEN HOUR(endTime) BETWEEN 18 AND 23 THEN 'Evening'
            ELSE 'Night'
        END AS time_period,
        SUM(msPlayed) / 60000 AS total_minutes
    FROM listening_data
    GROUP BY time_period
    ORDER BY total_minutes DESC;
    """
    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return render_template('listening_time_distribution.html', time_distribution=result)  


if __name__ == '__main__':
    app.run(debug=True)
