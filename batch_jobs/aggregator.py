import psycopg2
import pandas as pd
from cassandra.cluster import Cluster
from datetime import datetime, timedelta
import time

PG_CONN_PARAMS = {
    "host": "postgres",
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}

CASSANDRA_CONTACT_POINTS = ['cassandra']
KEYSPACE = "wikipedia"

def fetch_data_from_postgres(time_start: datetime, time_end: datetime) -> pd.DataFrame:
    query = """
        SELECT domain, created_at, user_id, user_name, page_title, comment, user_is_bot
        FROM wiki_events
        WHERE created_at >= %s AND created_at < %s
    """
    with psycopg2.connect(**PG_CONN_PARAMS) as conn:
        df = pd.read_sql(query, conn, params=(time_start, time_end))
    return df

def write_domain_stats(session, df, time_start, time_end):
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.set_index('created_at')

    grouped = df.groupby([pd.Grouper(freq='H'), 'domain']).size().reset_index(name='page_count')

    for _, row in grouped.iterrows():
        ts = row['created_at'].to_pydatetime() if hasattr(row['created_at'], 'to_pydatetime') else row['created_at']
        
        session.execute("""
            INSERT INTO domain_stats_by_hour (time_start, domain, page_count)
            VALUES (%s, %s, %s)
        """, (ts, row['domain'], int(row['page_count'])))

def write_bot_stats(session, df, time_start, time_end):
    df['created_at'] = pd.to_datetime(df['created_at'])
    bot_df = df[df['user_is_bot'] == True]
    bot_df = bot_df.set_index('created_at')
    grouped = bot_df.groupby([pd.Grouper(freq='H'), 'domain']).size().reset_index(name='created_by_bots')
    
    for _, row in grouped.iterrows():
        ts = row['created_at'].to_pydatetime() if hasattr(row['created_at'], 'to_pydatetime') else row['created_at']
        session.execute("""
            INSERT INTO bot_stats_last_6h (time_start, domain, created_by_bots)
            VALUES (%s, %s, %s)
        """, (ts, row['domain'], int(row['created_by_bots'])))

def write_top_users(session, df, time_start, time_end):
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.set_index('created_at')
    
    grouped = df.groupby([pd.Grouper(freq='H'), 'user_id', 'user_name']).agg({
        'page_title': lambda x: list(x),
        'user_id': 'count'
    }).rename(columns={'user_id': 'page_count'}).reset_index()

    for hour in grouped['created_at'].drop_duplicates():
        hour_df = grouped[grouped['created_at'] == hour]
        top_users = hour_df.sort_values('page_count', ascending=False).head(20)

        for _, row in top_users.iterrows():
            ts = row['created_at'].to_pydatetime() if hasattr(row['created_at'], 'to_pydatetime') else row['created_at']
            session.execute("""
                INSERT INTO top_users_last_6h (time_start, user_id, user_name, page_count, page_titles)
                VALUES (%s, %s, %s, %s, %s)
            """, (ts, int(row['user_id']), row['user_name'], int(row['page_count']), row['page_title']))

def main():
    while True:
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        time_end = now - timedelta(hours=1)
        time_start = time_end - timedelta(hours=6)

        cluster = Cluster(CASSANDRA_CONTACT_POINTS)
        session = cluster.connect(KEYSPACE)

        for i in range(6):
            start = time_start + timedelta(hours=i)
            end = start + timedelta(hours=1)
            print(f"\n🕒 Aggregating: {start} — {end}")
            df = fetch_data_from_postgres(start, end)
            print(f"📥 Fetched {len(df)} rows")

            if df.empty:
                print("⚠️ No data to write")
                continue

            write_domain_stats(session, df, start, end)
            write_bot_stats(session, df, start, end)
            write_top_users(session, df, start, end)

        print(f"\n✅ Aggregation done at: {datetime.utcnow()}")
        next_hour = now + timedelta(hours=1)
        sleep_seconds = (next_hour - datetime.utcnow()).total_seconds()
        print(f"😴 Sleeping {sleep_seconds:.0f} seconds until {next_hour}")
        time.sleep(sleep_seconds)

if __name__ == "__main__":
    main()