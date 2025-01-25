import mysql.connector
from datetime import date
import random

# Database connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",       # Replace with your MySQL server host
        user="root",            # Replace with your MySQL username
        password="useradmin@100",        # Replace with your MySQL password
        database="bus"          # Replace with your MySQL database name
    )

# Count records in the tickets table
def get_total_records(cursor):
    cursor.execute("SELECT COUNT(*) FROM tickets")
    result = cursor.fetchone()  # Fetch the result to clear the cursor buffer
    return result[0] if result else 0

# Function to display the beautiful starting table
def display_startup_info(cursor):
    print("="*50)
    print("BUS RESERVATION SYSTEM".center(50, ' '))
    print("".center(50, ' '))
    print("HIMANSHI".center(50, ' '))
    print("AND".center(50, ' '))
    print("VANSHIKA".center(50, ' '))
    print("="*50)
    
    # Count total tickets from the database
    total_tickets = get_total_records(cursor)
    print(f"Total Tickets = {total_tickets}".center(50, ' '))
    print("="*50)
    
    input("Press any key to continue...")

# Manage Route Menu
def manage_route(cursor, conn):
    while True:
        print("======================== \n MANAGE ROUTE \n =======================".center(50, ' '))
        print("1. Add Route")
        print("2. Edit Route")
        print("3. Show Routes")
        print("4. Delete Route")
        print("5. Exit to Main Menu")
        print()

        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input! Please enter a number between 1 and 5.")
            input("Press any key to continue...")
            continue

        if choice == 1:
            add_route(cursor, conn)
        elif choice == 2:
            edit_route(cursor, conn)
        elif choice == 3:
            show_routes(cursor)
        elif choice == 4:
            delete_route(cursor, conn)
        elif choice == 5:
            break
        else:
            print("Invalid choice! Please try again.")
            input("Press any key to continue...")

# Manage Tickets Menu
def manage_tickets(cursor, conn):
    while True:
        print("MANAGE TICKETS".center(50, ' '))
        print("1. View All Tickets")
        print("2. Delete Ticket")
        print("3. Exit to Main Menu")
        print()

        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input! Please enter a number between 1 and 3.")
            input("Press any key to continue...")
            continue

        if choice == 1:
            view_all_tickets(cursor)
        elif choice == 2:
            delete_ticket(cursor, conn)
        elif choice == 3:
            break
        else:
            print("Invalid choice! Please try again.")
            input("Press any key to continue...")

# View All Tickets
def view_all_tickets(cursor):
    print("VIEW ALL TICKETS".center(50, ' '))
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()
    

    if not tickets:
        print("No tickets found!")
    else:
        print(f"{'PNR':<20}{'Route':<30}{'Passenger Names':<40}{'Fare':<10}")
        print("-" * 100)
        for ticket in tickets:
            print(f"{ticket[0]:<20}{ticket[1]:<30}{ticket[2]:<40}{ticket[7]:<10}")
    
    input("Press any key to return to the Manage Tickets menu...")

# Delete Ticket
def delete_ticket(cursor, conn):
    print("DELETE TICKET".center(50, ' '))
    pnr = input("Enter the PNR of the ticket you want to delete: ").strip()

    cursor.execute("SELECT * FROM tickets WHERE PNR = %s", (pnr,))
    ticket = cursor.fetchone()
    if not ticket:
        print(f"No ticket found with PNR {pnr}.")
        input("Press any key to return to the Manage Tickets menu...")
        return

    confirmation = input(f"Are you sure you want to delete the ticket with PNR '{pnr}'? (yes/no): ").strip().lower()
    if confirmation == "yes":
        cursor.execute("DELETE FROM tickets WHERE PNR = %s", (pnr,))
        conn.commit()
        print(f"Ticket with PNR '{pnr}' deleted successfully.")
    else:
        print("Deletion cancelled.")
    
    input("Press any key to return to the Manage Tickets menu...")

# Add Route Functionality
def add_route(cursor, conn):
    print("ADD ROUTE".center(50, ' '))
    route_name = input("Enter Route Name: ")
    try:
        fare = float(input("Enter Fare: "))
        seats = int(input("Enter Total Seats: "))

        # Insert into the route table
        cursor.execute("INSERT INTO route (ROUTE, FARE, SEATS) VALUES (%s, %s, %s)", (route_name, fare, seats))
        conn.commit()

        # Get the last inserted route_id
        cursor.execute("SELECT LAST_INSERT_ID()")
        route_id = cursor.fetchone()[0]

        # Insert into the availability table
        cursor.execute("INSERT INTO availability (route_id, date, seats, available_seats) VALUES (%s, CURDATE(), %s, %s)",
                       (route_id, seats, seats))
        conn.commit()

        print("Route added successfully!")
    except ValueError:
        print("Invalid fare or seat count entered! Please try again.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    input("Press any key to return to the Manage Route menu...")

# Edit Route Functionality
def edit_route(cursor, conn):
    print("EDIT ROUTE".center(50, ' '))
    show_routes(cursor)  # Display all routes first
    try:
        route_id = int(input("Enter Route ID to edit: "))
        cursor.execute("SELECT * FROM route WHERE ROUTE_ID = %s", (route_id,))
        route = cursor.fetchone()
        if not route:
            print("Route ID not found!")
            input("Press any key to return to the Manage Route menu...")
            return

        print(f"Current Route: {route[1]}, Current Fare: {route[2]}")
        new_route_name = input("Enter New Route Name (leave blank to keep current): ")
        new_fare = input("Enter New Fare (leave blank to keep current): ")

        if new_route_name == "":
            new_route_name = route[1]
        if new_fare == "":
            new_fare = route[2]
        else:
            new_fare = float(new_fare)

        cursor.execute("UPDATE route SET ROUTE = %s, FARE = %s WHERE ROUTE_ID = %s",
                       (new_route_name, new_fare, route_id))
        conn.commit()
        print("Route updated successfully!")
    except ValueError:
        print("Invalid input! Please try again.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    input("Press any key to return to the Manage Route menu...")

# Show Routes Functionality
def show_routes(cursor):
    print("SHOW ROUTES".center(50, ' '))
    
    # Get all routes from the route table
    cursor.execute("SELECT route_id, route, fare, seats FROM route")
    routes = cursor.fetchall()
    
    if not routes:
        print("No routes found!")
    else:
        print(f"{'Route ID':<10}{'Route':<30}{'Fare':<10}{'Seats':<10}")
        print("-" * 60)  # Adjusted separator for the new column width
        
        for route in routes:
            route_id = route[0]
            route_name = route[1]
            fare = route[2]
            seats = route[3]
            
            # Simply display the route info without showing available tickets
            print(f"{route_id:<10}{route_name:<30}{fare:<10}{seats:<10}")
    
    input("Press any key to return to the Manage Route menu...")


# Delete Route Functionality
def delete_route(cursor, conn):
    print("DELETE ROUTE".center(50, ' '))
    show_routes(cursor)  # Display all routes first
    try:
        route_id = int(input("Enter Route ID to delete: "))
        cursor.execute("SELECT * FROM route WHERE ROUTE_ID = %s", (route_id,))
        route = cursor.fetchone()
        if not route:
            print("Route ID not found!")
            input("Press any key to return to the Manage Route menu...")
            return

        confirmation = input(f"Are you sure you want to delete the route '{route[1]}'? (yes/no): ").strip().lower()
        if confirmation == "yes":
            cursor.execute("DELETE FROM route WHERE ROUTE_ID = %s", (route_id,))
            conn.commit()
            print("Route deleted successfully!")
        else:
            print("Deletion cancelled.")
    except ValueError:
        print("Invalid input! Please try again.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    input("Press any key to return to the Manage Route menu...")

# Generate a random PNR number
def generate_pnr():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))

# Book Ticket Functionality
def book_ticket(cursor, conn):
    print("BOOK TICKET".center(50, ' '))

    # Show available routes
    show_routes(cursor)

    try:
        route_id = int(input("Enter Route ID to book tickets: "))
        cursor.execute("SELECT * FROM route WHERE ROUTE_ID = %s", (route_id,))
        route = cursor.fetchone()
        
        if not route:
            print("Route ID not found!")
            input("Press any key to return to the menu...")
            return

        route_name = route[1]  # Route name
        fare = route[2]  # Fare
        total_seats = route[3]  # Total seats from the route table

        print(f"Selected Route: {route_name}, Fare per Passenger: {fare}, Total Seats: {total_seats}")

        # Ask for Date of Journey (DOJ)
        doj = input("Enter the Date of Journey (YYYY-MM-DD): ")
        try:
            # Validate DOJ format
            doj_date = date.fromisoformat(doj)  # Ensures the date is in YYYY-MM-DD format
        except ValueError:
            print("Invalid date format! Please use YYYY-MM-DD.")
            input("Press any key to return to the menu...")
            return

        # Check available seats for the selected route and date
        cursor.execute("SELECT available_seats FROM availability WHERE route_id = %s AND date = %s", 
                       (route_id, doj_date))
        availability = cursor.fetchone()

        if not availability:
            # If no availability record exists, assume all seats are available
            available_seats = total_seats
            print(f"No seat availability found for the selected route on {doj_date}. Assuming all {total_seats} seats are available.")
        else:
            available_seats = availability[0]

        # Show available seats
        print(f"Available seats on {doj_date}: {available_seats} seats")

        num_passengers = int(input("Enter the number of passengers (1-5): "))
        if num_passengers < 1 or num_passengers > 5:
            print("Invalid number of passengers! Please try again.")
            input("Press any key to return to the menu...")
            return

        # Check if there are enough available seats
        if num_passengers > available_seats:
            print(f"Not enough available seats. Only {available_seats} seats left.")
            input("Press any key to return to the menu...")
            return

        passengers = []
        for i in range(num_passengers):
            print(f"Enter details for Passenger {i + 1}")
            name = input("Name: ")
            age = int(input("Age: "))
            gender = input("Gender (M/F): ")
            mobile = input("Mobile Number: ")
            dob = date.today().strftime('%Y-%m-%d')
            passengers.append({
                "name": name, "age": age, "gender": gender,
                "dob": dob, "mobile": mobile
            })

        print(f"\nBooking {num_passengers} tickets for route '{route_name}'. Total Fare: {fare * num_passengers}")
        
        pnr = generate_pnr()

        # Insert the tickets into the tickets table
        for passenger in passengers:
            cursor.execute(
                "INSERT INTO tickets (PNR, ROUTE, NAME, AGE, GENDER, DOB, MOBILE, FARE, DOJ) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                (pnr, route_name, passenger["name"], passenger["age"], passenger["gender"], 
                 passenger["dob"], passenger["mobile"], fare, doj_date)
            )

        # Update the available_seats in the availability table after booking
        new_available_seats = available_seats - num_passengers

        # If there's no entry for this route and date in the availability table, add a new record
        if not availability:
            cursor.execute("INSERT INTO availability (route_id, date, seats, available_seats) "
                           "VALUES (%s, %s, %s, %s)",
                           (route_id, doj_date, total_seats, new_available_seats))
        else:
            # Otherwise, update the existing record
            cursor.execute("UPDATE availability SET available_seats = %s WHERE route_id = %s AND date = %s", 
                           (new_available_seats, route_id, doj_date))

        # Commit the changes
        conn.commit()

        print(f"Tickets successfully booked! PNR: {pnr}")
        
    except ValueError:
        print("Invalid input! Please try again.")
    input("Press any key to return to the menu...")



# Seat Availability Check
def seat_availability(cursor):
    print("SEAT AVAILABILITY".center(50, ' '))
    
    # Show available routes
    show_routes(cursor)

    try:
        route_id = int(input("Enter Route ID to check availability: "))
        cursor.execute("SELECT * FROM route WHERE ROUTE_ID = %s", (route_id,))
        route = cursor.fetchone()
        if not route:
            print("Route ID not found!")
            input("Press any key to return to the menu...")
            return

        route_name = route[1]  # Assuming the first row is the selected route

        # Ask for Date of Journey (DOJ)
        doj = input("Enter the Date of Journey (YYYY-MM-DD): ")
        try:
            # Validate DOJ format
            doj_date = date.fromisoformat(doj)  # Ensures the date is in YYYY-MM-DD format
        except ValueError:
            print("Invalid date format! Please use YYYY-MM-DD.")
            input("Press any key to return to the menu...")
            return

        # Get available seats for the selected route and date
        cursor.execute("SELECT available_seats FROM availability WHERE route_id = %s AND date = %s", (route_id, doj_date))
        availability = cursor.fetchone()

        if not availability:
            print(f"No seat availability found for the selected route on {doj_date}.")
        else:
            available_seats = availability[0]
            print(f"Available Seats for Route '{route_name}' on {doj_date}: {available_seats}")

    except ValueError:
        print("Invalid input! Please try again.")
    input("Press any key to return to the menu...")

# Main Menu
def main():
    conn = connect_db()
    cursor = conn.cursor()

    display_startup_info(cursor)

    while True:
        print("======================")
        print("1. Manage Route")
        print("2. Manage Tickets")
        print("3. Book Ticket")
        print("4. Seat Availability")
        print("5. Exit")
        print("======================")
        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input! Please try again.")
            continue

        if choice == 1:
            manage_route(cursor, conn)
        elif choice == 2:
            manage_tickets(cursor, conn)
        elif choice == 3:
            book_ticket(cursor, conn)
        elif choice == 4:
            seat_availability(cursor)
        elif choice == 5:
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please try again.")
            input("Press any key to continue...")

    conn.close()

if __name__ == "__main__":
    main()
