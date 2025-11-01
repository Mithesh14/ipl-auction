import pandas as pd
import random
import math
import os

# === CONFIGURATION ===
EXCEL_FILE = 'Auction.xlsx'        # Your Excel file
SHEET_NAME = 0                     # or 'Sheet1'
CLEAR_BETWEEN_SECTIONS = True      # Set False to keep all previous sections too

# Column order (must match Excel)
COLUMNS = [
    'Indian Bat', 'Foreign Bat', 'Indian AR', 'Foreign AR',
    'Indian Pace', 'Foreign Pace', 'Indian spin', 'Foreign spin', 'Wicketkeepers'
]

# === LOAD & CLEAN DATA ===
print("Loading Excel file...")
df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

data = {}
for col in COLUMNS:
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found! Check: {col}")
    
    players = df[col].dropna().astype(str).tolist()
    players = [p.strip() for p in players if p.strip() and p.strip().lower() != 'nan']
    data[col] = players

print(f"Loaded {len(COLUMNS)} categories.\n")

# === SHUFFLE & SPLIT EACH COLUMN INTO 2 SETS ===
splits = {}
for col, players in data.items():
    random.shuffle(players)
    n = len(players)
    mid = (n + 1) // 2
    splits[col] = {
        'set1': players[:mid],
        'set2': players[mid:]
    }
    print(f"{col}: {n} → Set 1: {len(splits[col]['set1'])}, Set 2: {len(splits[col]['set2'])}")

print("\n" + "="*80)
print("IPL MEGA AUCTION - PLAYER DISPLAY (Names Stay On Screen)")
print("\nPress ENTER to reveal next player. Names will accumulate in each section.\n\n")
print("="*80 + "\n")

input("Press ENTER to start the auction...\n")

# === DISPLAY: ONE PLAYER AT A TIME, KEEP ON SCREEN ===
for set_num in [1, 2]:
    set_key = f'set{set_num}'

    for col_idx, col in enumerate(COLUMNS):
        players = splits[col][set_key]
        if not players:
            continue

        # === SECTION HEADER ===
        if CLEAR_BETWEEN_SECTIONS:
            os.system('cls' if os.name == 'nt' else 'clear')

        print(f"\n{'='*25} {col.upper()} - SET {set_num} {'='*25}")
        print(f"Total Players in this Set: {len(players)}\n")
        input("Press ENTER to start revealing players one by one...\n\n")

        # === DISPLAY PLAYERS ONE BY ONE (NO CLEAR) ===
        for i, player in enumerate(players, 1):
            print(f"{i:2d}. {player}")
            
            # Wait for Enter BEFORE showing next
            if i < len(players):
                input(f"\n--> Press ENTER for player {i+1}...\n")
            else:
                input(f"\nSection Complete! Press ENTER to go to next section...\n\n")

        # Optional: small separator
        print("\n" + "-"*60)
        if col_idx < len(COLUMNS) - 1 or set_num == 1:
            input("Press ENTER to continue to next section...\n\n")

# === FINAL MESSAGE ===
os.system('cls' if os.name == 'nt' else 'clear')
print("\n" + "="*60)
print("AUCTION DISPLAY COMPLETED!")
print("All players have been revealed.")
print("="*60)
input("\nPress ENTER to exit...")