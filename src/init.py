import sqlite3
import uuid
import random
from datetime import datetime, timedelta
import os
from config import SQL_SCHEMAS

# --- SQL Schema Definition ---
# noqa: F811
SQL = f"""
DROP TABLE IF EXISTS resource_utilization;
DROP TABLE IF EXISTS api_requests;
DROP TABLE IF EXISTS system_performance;
DROP TABLE IF EXISTS application_errors;
DROP TABLE IF EXISTS user_sessions;

{SQL_SCHEMAS}
"""

# --- Configuration ---
DB_FILE = "monitoring_data.db"
NUM_ROWS = 100
NUM_UNIQUE_USERS = 25
NUM_UNIQUE_SERVERS = 5

# --- Sample Data Lists ---
BROWSERS = ["Chrome", "Firefox", "Safari", "Edge", "Opera", "Brave"]
DEVICES = ["Desktop", "Mobile", "Tablet", "Unknown"]
SESSION_STATUSES = ["active", "ended", "expired"]
ERROR_CODES = ["E500", "E404", "E403", "DB101", "NET005", "AUTH001", "VAL002"]
SEVERITY_LEVELS = ["info", "warning", "error", "critical"]
MODULES = [
    "AuthService",
    "ProductCatalog",
    "OrderProcessing",
    "PaymentGateway",
    "UserManagement",
    "Reporting",
]
METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
ENDPOINTS = [
    "/api/users",
    "/api/products",
    "/api/orders",
    "/auth/login",
    "/auth/refresh",
    "/api/payments",
    "/api/reports",
]
RESOURCE_TYPES = [
    "CPU",
    "Memory",
    "Disk I/O",
    "Network Bandwidth",
    "Database Connections",
]
RESOURCE_STATUSES = ["ok", "warning", "critical", "unknown"]


# --- Helper Functions ---
def create_connection(db_file):
    """create a database connection to the SQLite database specified by db_file"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"SQLite connection established to {db_file}")
        # Enable foreign key constraint enforcement
        conn.execute("PRAGMA foreign_keys = ON;")
        print("Foreign key enforcement enabled.")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn


def create_tables(conn, schemas):
    """create tables from the create table statements"""
    try:
        cursor = conn.cursor()
        # Use executescript to handle multiple statements separated by ';'
        cursor.executescript(schemas)
        conn.commit()
        print("Tables created successfully (or already exist).")
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")


def generate_random_timestamp(days_past=30):
    """Generate a random timestamp within the last 'days_past' days."""
    now = datetime.now()
    delta_seconds = random.uniform(0, days_past * 24 * 60 * 60)
    return now - timedelta(seconds=delta_seconds)


# --- Data Generation Functions ---


def generate_user_sessions(n, num_users):
    """Generate n user session records."""
    data = []
    user_ids = [str(uuid.uuid4()) for _ in range(num_users)]
    session_ids = []  # Keep track of generated session IDs

    for _ in range(n):
        session_id = str(uuid.uuid4())
        user_id = random.choice(user_ids)
        start_time = generate_random_timestamp()
        status = random.choice(SESSION_STATUSES)
        end_time = None
        if status != "active":
            # Ensure end_time is after start_time
            end_time = start_time + timedelta(minutes=random.uniform(5, 240))

        ip = f"{random.randint(1, 254)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        browser = random.choice(BROWSERS)
        device = random.choice(DEVICES)

        data.append(
            (session_id, user_id, start_time, end_time, ip, browser, device, status)
        )
        session_ids.append(session_id)  # Store the generated ID

    return data, user_ids, session_ids  # Return generated user and session IDs too


def generate_application_errors(n, existing_session_ids, existing_user_ids):
    """Generate n application error records, referencing existing sessions/users."""
    data = []
    if not existing_session_ids:
        print("Warning: Cannot generate application errors without existing sessions.")
        return data

    for _ in range(n):
        error_id = str(uuid.uuid4())
        timestamp = generate_random_timestamp()
        error_code = random.choice(ERROR_CODES)
        severity = random.choice(SEVERITY_LEVELS)
        module = random.choice(MODULES)
        message = (
            f"Error {error_code} encountered in {module} with severity {severity}."
        )
        # Allow some errors to not be associated with a specific user/session
        user_id = random.choice(
            existing_user_ids + [None] * (len(existing_user_ids) // 4)
        )  # ~20% chance of None
        session_id = random.choice(
            existing_session_ids
        )  # Errors must have a session in this design

        data.append(
            (
                error_id,
                timestamp,
                error_code,
                message,
                severity,
                module,
                user_id,
                session_id,
            )
        )
    return data


def generate_system_performance(n, num_servers):
    """Generate n system performance records."""
    data = []
    server_ids = [f"server-{i:02d}-{str(uuid.uuid4())[:4]}" for i in range(num_servers)]

    for _ in range(n):
        metric_id = str(uuid.uuid4())
        timestamp = generate_random_timestamp()
        cpu = round(random.uniform(1.0, 99.0), 2)
        mem = round(random.uniform(10.0, 95.0), 2)
        disk = round(random.uniform(5.0, 90.0), 2)
        resp_time = round(random.uniform(50.0, 1500.0), 3)  # ms
        connections = random.randint(5, 1000)
        server_id = random.choice(server_ids)

        data.append(
            (metric_id, timestamp, cpu, mem, disk, resp_time, connections, server_id)
        )
    return data, server_ids  # Return server IDs for use elsewhere


def generate_api_requests(n, existing_session_ids, existing_user_ids):
    """Generate n API request records."""
    data = []
    if not existing_session_ids:
        print("Warning: Cannot generate API requests without existing sessions.")
        return data

    for _ in range(n):
        request_id = str(uuid.uuid4())
        timestamp = generate_random_timestamp()
        endpoint = random.choice(ENDPOINTS)
        if "{id}" in endpoint:  # Basic placeholder replacement
            endpoint = endpoint.replace("{id}", str(random.randint(1, 1000)))
        elif endpoint.endswith("s"):  # Add ID to plural endpoints sometimes
            if random.random() > 0.5:
                endpoint += f"/{str(uuid.uuid4())[:8]}"

        method = random.choice(METHODS)
        resp_code = random.choices(
            [200, 201, 204, 400, 401, 403, 404, 500, 503],
            weights=[50, 10, 5, 10, 5, 5, 5, 8, 2],
            k=1,
        )[0]
        resp_time = round(random.uniform(20.0, 2500.0), 3)  # ms
        user_id = random.choice(
            existing_user_ids + [None] * (len(existing_user_ids) // 5)
        )  # ~17% chance of None
        session_id = random.choice(existing_session_ids)
        payload = random.randint(0, 1024 * 10)  # 0 to 10KB payload

        data.append(
            (
                request_id,
                timestamp,
                endpoint,
                method,
                resp_code,
                resp_time,
                user_id,
                session_id,
                payload,
            )
        )
    return data


def generate_resource_utilization(n, existing_server_ids):
    """Generate n resource utilization records."""
    data = []
    if not existing_server_ids:
        print("Warning: Cannot generate resource utilization without existing servers.")
        return data

    for _ in range(n):
        resource_id = str(uuid.uuid4())
        timestamp = generate_random_timestamp()
        resource_type = random.choice(RESOURCE_TYPES)
        server_id = random.choice(existing_server_ids)
        status = random.choice(RESOURCE_STATUSES)

        if resource_type in ["CPU", "Memory", "Disk I/O"]:
            max_capacity = 100.00
            current_usage = round(random.uniform(5.0, 98.0), 2)
        elif resource_type == "Network Bandwidth":
            max_capacity = random.choice([100.00, 1000.00, 10000.00])  # Mbps
            current_usage = round(
                random.uniform(0.1 * max_capacity, 0.9 * max_capacity), 2
            )
        elif resource_type == "Database Connections":
            max_capacity = random.choice([50.00, 100.00, 200.00, 500.00])
            current_usage = round(random.randint(5, int(max_capacity * 0.95)), 2)
        else:
            max_capacity = 1000.00
            current_usage = round(random.uniform(10, 950), 2)

        if (
            status == "ok" and current_usage > 80.0 and max_capacity == 100.0
        ):  # Adjust status logically
            status = "warning"
        if (
            status in ["ok", "warning"]
            and current_usage > 95.0
            and max_capacity == 100.0
        ):
            status = "critical"

        data.append(
            (
                resource_id,
                timestamp,
                resource_type,
                current_usage,
                max_capacity,
                server_id,
                status,
            )
        )
    return data


# --- Main Execution ---
if __name__ == "__main__":
    # Remove existing DB file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed existing database file: {DB_FILE}")

    conn = create_connection(DB_FILE)

    if conn is not None:
        try:
            # Create tables
            create_tables(conn, SQL)

            # --- Generate Data ---
            print(f"\nGenerating {NUM_ROWS} rows for each table...")

            # User Sessions (Generate first to get IDs)
            user_session_data, user_ids, session_ids = generate_user_sessions(
                NUM_ROWS, NUM_UNIQUE_USERS
            )
            print(f"Generated {len(user_session_data)} user sessions.")

            # System Performance (Generate next to get server IDs)
            system_performance_data, server_ids = generate_system_performance(
                NUM_ROWS, NUM_UNIQUE_SERVERS
            )
            print(
                f"Generated {len(system_performance_data)} system performance metrics."
            )

            # Application Errors (Needs session/user IDs)
            application_error_data = generate_application_errors(
                NUM_ROWS, session_ids, user_ids
            )
            print(f"Generated {len(application_error_data)} application errors.")

            # API Requests (Needs session/user IDs)
            api_request_data = generate_api_requests(NUM_ROWS, session_ids, user_ids)
            print(f"Generated {len(api_request_data)} API requests.")

            # Resource Utilization (Needs server IDs)
            resource_utilization_data = generate_resource_utilization(
                NUM_ROWS, server_ids
            )
            print(
                f"Generated {len(resource_utilization_data)} resource utilization records."
            )

            # --- Insert Data ---
            print("\nInserting data into tables...")
            cursor = conn.cursor()

            if user_session_data:
                cursor.executemany(
                    "INSERT INTO user_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    user_session_data,
                )
                print(f"Inserted {len(user_session_data)} rows into user_sessions.")

            if application_error_data:
                cursor.executemany(
                    "INSERT INTO application_errors VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    application_error_data,
                )
                print(
                    f"Inserted {len(application_error_data)} rows into application_errors."
                )

            if system_performance_data:
                cursor.executemany(
                    "INSERT INTO system_performance VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    system_performance_data,
                )
                print(
                    f"Inserted {len(system_performance_data)} rows into system_performance."
                )

            if api_request_data:
                cursor.executemany(
                    "INSERT INTO api_requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    api_request_data,
                )
                print(f"Inserted {len(api_request_data)} rows into api_requests.")

            if resource_utilization_data:
                cursor.executemany(
                    "INSERT INTO resource_utilization VALUES (?, ?, ?, ?, ?, ?, ?)",
                    resource_utilization_data,
                )
                print(
                    f"Inserted {len(resource_utilization_data)} rows into resource_utilization."
                )

            # Commit changes
            conn.commit()
            print("\nData insertion complete and changes committed.")

        except sqlite3.Error as e:
            print(f"\nAn error occurred during data generation or insertion: {e}")
            print("Rolling back changes...")
            conn.rollback()  # Rollback changes if any error occurs

        finally:
            # Close the connection
            conn.close()
            print("SQLite connection closed.")
    else:
        print("Failed to create database connection. Exiting.")
