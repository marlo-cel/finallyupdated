import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.db import get_connection, initialize_database


class CSVDataLoader:
    """Loads CSV data into the database."""

    def __init__(self, data_dir: str = "DATA"):
        """Initialize with data directory path."""
        # Get project root (2 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        self.data_dir = project_root / data_dir

        if not self.data_dir.exists():
            print(f"⚠️  Warning: Data directory not found: {self.data_dir}")
            print(f"   Current working directory: {Path.cwd()}")

    def load_csv_file(self, filename: str) -> List[Dict[str, Any]]:
        """Load a CSV file and return rows as dictionaries."""
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        rows = []
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                rows.append(row)

        print(f"✅ Loaded {len(rows)} rows from {filename}")
        return rows

    def import_cyber_incidents(self) -> int:
        """Import cyber incidents from CSV into database."""
        print("\n=== Importing Cyber Incidents ===")

        try:
            rows = self.load_csv_file('cyber_incidents.csv')

            with get_connection() as conn:
                # Clear existing data (optional - remove if you want to keep existing)
                conn.execute("DELETE FROM cyber_incidents")

                imported = 0
                for row in rows:
                    try:
                        # Parse timestamp
                        timestamp = row.get('timestamp', '')
                        # Handle both formats
                        try:
                            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                        except ValueError:
                            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

                        # Use description as title (CSV has description field)
                        title = row.get('description', 'Untitled Incident')

                        conn.execute("""
                            INSERT INTO cyber_incidents 
                            (title, description, severity, date_reported, reported_by)
                            VALUES (?, ?, ?, ?, NULL)
                        """, (
                            title,
                            title,  # Use same for description
                            row.get('severity', 'Medium'),
                            dt.isoformat()
                        ))

                        imported += 1
                        if imported % 20 == 0:
                            print(f"   Imported {imported} incidents...")

                    except Exception as e:
                        print(f"   ⚠️  Skipped row: {e}")
                        continue

                conn.commit()
                print(f"✅ Successfully imported {imported} cyber incidents")
                return imported

        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return 0
        except Exception as e:
            print(f"❌ Error importing incidents: {e}")
            return 0

    def import_datasets(self) -> int:
        """Import datasets metadata from CSV into database."""
        print("\n=== Importing Datasets ===")

        try:
            rows = self.load_csv_file('datasets_metadata.csv')

            with get_connection() as conn:
                # Clear existing data
                conn.execute("DELETE FROM datasets_metadata")

                imported = 0
                for row in rows:
                    try:
                        conn.execute("""
                            INSERT INTO datasets_metadata 
                            (name, description, rows, owner)
                            VALUES (?, ?, ?, NULL)
                        """, (
                            row.get('name', 'Unnamed Dataset'),
                            f"Uploaded by {row.get('uploaded_by', 'unknown')}",
                            int(row.get('rows', 0)),
                        ))

                        imported += 1

                    except Exception as e:
                        print(f"   ⚠️  Skipped row: {e}")
                        continue

                conn.commit()
                print(f"✅ Successfully imported {imported} datasets")
                return imported

        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return 0
        except Exception as e:
            print(f"❌ Error importing datasets: {e}")
            return 0

    def import_it_tickets(self) -> int:
        """Import IT tickets from CSV into database."""
        print("\n=== Importing IT Tickets ===")

        try:
            rows = self.load_csv_file('it_tickets.csv')

            with get_connection() as conn:
                # Clear existing data
                conn.execute("DELETE FROM it_tickets")

                imported = 0
                for row in rows:
                    try:
                        conn.execute("""
                            INSERT INTO it_tickets 
                            (issue, status, priority, opened_by)
                            VALUES (?, ?, ?, NULL)
                        """, (
                            row.get('description', 'No description'),
                            row.get('status', 'Open'),
                            row.get('priority', 'Medium')
                        ))

                        imported += 1
                        if imported % 20 == 0:
                            print(f"   Imported {imported} tickets...")

                    except Exception as e:
                        print(f"   ⚠️  Skipped row: {e}")
                        continue

                conn.commit()
                print(f"✅ Successfully imported {imported} IT tickets")
                return imported

        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return 0
        except Exception as e:
            print(f"❌ Error importing tickets: {e}")
            return 0

    def verify_import(self):
        """Verify imported data counts."""
        print("\n=== Verifying Import ===")

        with get_connection() as conn:
            incidents = conn.execute("SELECT COUNT(*) as count FROM cyber_incidents").fetchone()['count']
            datasets = conn.execute("SELECT COUNT(*) as count FROM datasets_metadata").fetchone()['count']
            tickets = conn.execute("SELECT COUNT(*) as count FROM it_tickets").fetchone()['count']

            print(f"📊 Database Contents:")
            print(f"   - Cyber Incidents: {incidents}")
            print(f"   - Datasets: {datasets}")
            print(f"   - IT Tickets: {tickets}")
            print(f"   - Total Records: {incidents + datasets + tickets}")

    def import_all(self):
        """Import all CSV data."""
        print("=" * 60)
        print("CSV DATA IMPORT TOOL")
        print("Multi-Domain Intelligence Platform")
        print("=" * 60)

        # Initialize database
        print("\n🔧 Initializing database...")
        initialize_database()
        print("✅ Database initialized")

        # Import all data
        incidents_count = self.import_cyber_incidents()
        datasets_count = self.import_datasets()
        tickets_count = self.import_it_tickets()

        # Verify
        self.verify_import()

        # Summary
        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        print(f"✅ Cyber Incidents: {incidents_count}")
        print(f"✅ Datasets: {datasets_count}")
        print(f"✅ IT Tickets: {tickets_count}")
        print(f"📊 Total: {incidents_count + datasets_count + tickets_count}")
        print("=" * 60)

        if incidents_count > 0 or datasets_count > 0 or tickets_count > 0:
            print("\n🎉 Import complete! Your dashboards now have data.")
            print("💡 Run: streamlit run app.py")
        else:
            print("\n⚠️  No data was imported. Check that CSV files exist in DATA/ directory.")


def main():
    """Main entry point for CSV import."""
    loader = CSVDataLoader()

    try:
        loader.import_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()