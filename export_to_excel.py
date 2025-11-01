#!/usr/bin/env python3
"""
Export database to Excel for backup/review
"""
import sqlite3
import pandas as pd
from datetime import datetime

DATABASE = 'auction.db'
EXCEL_FILE = 'auction_data.xlsx'

def export_to_excel():
    """Export all database tables to Excel"""
    conn = sqlite3.connect(DATABASE)
    
    # Read all tables
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        # Users
        try:
            df_users = pd.read_sql_query('SELECT * FROM users', conn)
            df_users = df_users.drop(columns=['password_hash'])  # Don't export passwords
            df_users.to_excel(writer, sheet_name='Users', index=False)
            print(f"✓ Exported {len(df_users)} users")
        except Exception as e:
            print(f"⚠ Error exporting users: {e}")
        
        # Teams
        try:
            df_teams = pd.read_sql_query('SELECT * FROM teams', conn)
            df_teams.to_excel(writer, sheet_name='Teams', index=False)
            print(f"✓ Exported {len(df_teams)} team entries")
        except Exception as e:
            print(f"⚠ Error exporting teams: {e}")
        
        # Bids
        try:
            df_bids = pd.read_sql_query('SELECT * FROM bids', conn)
            df_bids.to_excel(writer, sheet_name='Bids', index=False)
            print(f"✓ Exported {len(df_bids)} bids")
        except Exception as e:
            print(f"⚠ Error exporting bids: {e}")
        
        # Auction Log
        try:
            df_log = pd.read_sql_query('SELECT * FROM auction_log', conn)
            df_log.to_excel(writer, sheet_name='Auction_Log', index=False)
            print(f"✓ Exported {len(df_log)} auction log entries")
        except Exception as e:
            print(f"⚠ Error exporting auction log: {e}")
    
    conn.close()
    print(f"\n✅ Exported all data to {EXCEL_FILE}")

if __name__ == '__main__':
    export_to_excel()

