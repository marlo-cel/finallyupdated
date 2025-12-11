import sys
from pathlib import Path

# Add app directory to path
app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path))

from utils.csv_data_loader import CSVDataLoader

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║   CSV DATA IMPORT - Multi-Domain Intelligence Platform   ║
╚══════════════════════════════════════════════════════════╝
    """)

    loader = CSVDataLoader()
    loader.import_all()