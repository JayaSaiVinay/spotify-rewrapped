use spotify;
CREATE TABLE if not exists listening_data (
    endTime DATETIME,
    artistName VARCHAR(255),
    trackName VARCHAR(255),
    msPlayed INT
);

-- Data Head 

select * from listening_data
limit 10;

-- Top Tracks by Play Count

SELECT trackName, COUNT(*) AS play_count
FROM listening_data
GROUP BY trackName
ORDER BY play_count DESC
LIMIT 10;

-- Top Tracks by Total Listening Time

SELECT trackName, SUM(msPlayed) / 60000 AS total_minutes
FROM listening_data
GROUP BY trackName
ORDER BY total_minutes DESC
LIMIT 10;


-- Top Artists by Play Count

select artistName, COUNT(*) as playCount
from listening_data
group by artistName
order by playCount desc
limit 10;

-- Top Artists by Total Listening Time

select artistName, SUM(msPlayed) / 60000 as totalTime
from listening_data
group by artistName
order by totalTime desc
limit 10;

-- Top Listening Months (Most Active Months)

select date_format(endTime, '%Y-%M') as month, sum(msPlayed) / 60000 as total_mins
from listening_data
group by month
order by total_mins desc
limit 10;

-- Listening Time Distribution by Period 

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


-- Top Tracks Removing Night Time

select trackName, artistName, COUNT(*) as playCount, SUM(msPlayed) / 60000 as totalMinutes
from listening_data
where hour(endTime) not between 0 and 5
group by trackName, artistName 
order by playCount desc
limit 10;