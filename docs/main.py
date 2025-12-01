import sys
from data.db import initialize_database
from services.user_service import register_user_db, authenticate_user_db
from data import incidents, tickets, datasets, users as users_module

def pause():
    input("\nPress Enter to continue...")

def show_main_menu():
    print("\n=== Week 8 Lab - Mini Data Pipeline & CRUD ===")
    print("[1] Initialize / migrate database (create tables)")
    print("[2] Register (DB)")
    print("[3] Login (DB)")
    print("[4] Manage incidents")
    print("[5] Manage IT tickets")
    print("[6] Manage datasets metadata")
    print("[7] List users")
    print("[0] Exit")

def incidents_menu():
    while True:
        print("\n--- Incidents ---")
        print("[1] Create incident")
        print("[2] List all incidents")
        print("[3] Search incidents")
        print("[4] Update incident")
        print("[5] Delete incident")
        print("[0] Back")
        c = input("Choice: ").strip()
        if c == "1":
            title = input("Title: ")
            desc = input("Description: ")
            severity = input("Severity: ")
            date = input("Date reported (YYYY-MM-DD): ")
            reporter = input("Reporter ID (blank for none): ") or None
            incidents.create_incident(title, desc, severity, date, reporter)
            print("Created.")
        elif c == "2":
            for r in incidents.get_all_incidents():
                print(dict(r))
        elif c == "3":
            kw = input("Keyword: ")
            for r in incidents.search_incidents(kw):
                print(dict(r))
        elif c == "4":
            iid = input("Incident ID: ")
            field = input("Field to update (title/description/severity/date_reported/reported_by): ")
            val = input("New value: ")
            incidents.update_incident(iid, **{field: val})
            print("Updated.")
        elif c == "5":
            iid = input("Incident ID: ")
            incidents.delete_incident(iid)
            print("Deleted.")
        elif c == "0":
            break
        else:
            print("Invalid.")

def tickets_menu():
    while True:
        print("\n--- IT Tickets ---")
        print("[1] Create ticket")
        print("[2] List tickets")
        print("[3] Update ticket")
        print("[4] Delete ticket")
        print("[0] Back")
        c = input("Choice: ").strip()
        if c == "1":
            issue = input("Issue: ")
            status = input("Status: ")
            priority = input("Priority: ")
            opened_by = input("Opened by (user id or blank): ") or None
            tickets.create_ticket(issue, status, priority, opened_by)
            print("Created.")
        elif c == "2":
            for r in tickets.list_tickets():
                print(dict(r))
        elif c == "3":
            tid = input("Ticket ID: ")
            field = input("Field to update (issue/status/priority/opened_by): ")
            val = input("New value: ")
            tickets.update_ticket(tid, **{field: val})
            print("Updated.")
        elif c == "4":
            tid = input("Ticket ID: ")
            tickets.delete_ticket(tid)
            print("Deleted.")
        elif c == "0":
            break
        else:
            print("Invalid.")

def datasets_menu():
    while True:
        print("\n--- Datasets ---")
        print("[1] Add dataset")
        print("[2] List datasets")
        print("[3] Update dataset")
        print("[4] Delete dataset")
        print("[0] Back")
        c = input("Choice: ").strip()
        if c == "1":
            name = input("Name: ")
            desc = input("Description: ")
            rows = input("Rows (number): ")
            owner = input("Owner ID (user): ") or None
            datasets.add_dataset(name, desc, int(rows or 0), owner)
            print("Added.")
        elif c == "2":
            for r in datasets.list_datasets():
                print(dict(r))
        elif c == "3":
            did = input("Dataset ID: ")
            field = input("Field to update (name/description/rows/owner): ")
            val = input("New value: ")
            datasets.update_dataset(did, **{field: (int(val) if field == "rows" else val)})
            print("Updated.")
        elif c == "4":
            did = input("Dataset ID: ")
            datasets.delete_dataset(did)
            print("Deleted.")
        elif c == "0":
            break
        else:
            print("Invalid.")

def main():
    while True:
        show_main_menu()
        choice = input("Option: ").strip()
        if choice == "1":
            initialize_database()
            print("Database initialized (tables created).")
            pause()
        elif choice == "2":
            uname = input("New username: ").strip()
            pwd = input("Password: ").strip()
            ok, result = register_user_db(uname, pwd)
            if ok:
                print(f"Registered user id {result}.")
            else:
                print("Error:", result)
            pause()
        elif choice == "3":
            uname = input("Username: ").strip()
            pwd = input("Password: ").strip()
            ok, data = authenticate_user_db(uname, pwd)
            if ok:
                print("Login successful. Welcome:", data["username"])
            else:
                print("Login failed:", data)
            pause()
        elif choice == "4":
            incidents_menu()
        elif choice == "5":
            tickets_menu()
        elif choice == "6":
            datasets_menu()
        elif choice == "7":
            for r in users_module.list_users():
                print(dict(r))
            pause()
        elif choice == "0":
            print("Exiting.")
            sys.exit(0)
        else:
            print("Invalid.")

if __name__ == "__main__":
    main()
