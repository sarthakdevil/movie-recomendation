import pandas as pd
from sqlalchemy import create_engine

# Create the database engine
engine = create_engine('mysql+pymysql://root:password@localhost:3306/movies')

try:
    # Load CSV into the database
    df = pd.read_csv('cosine_similarity_matrix.csv')

    # Replace 'cosine_similarity' with your desired table name
    df.to_sql('cosine_similarity', con=engine, index=False, if_exists='replace')

    print("CSV data has been loaded into the database.")
except Exception as e:
    print("An error occurred:", e)
