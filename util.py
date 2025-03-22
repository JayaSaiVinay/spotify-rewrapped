import pandas as pd 

df = pd.read_json('Merged_StreamingHistory.json') 
df.to_csv('Merged_StreamingHistory.csv', index=False)