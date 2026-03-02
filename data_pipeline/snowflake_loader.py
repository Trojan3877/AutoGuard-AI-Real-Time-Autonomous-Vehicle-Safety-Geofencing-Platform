import snowflake.connector

def load_sensor_data():
    conn = snowflake.connector.connect(
        user="USER",
        password="PASSWORD",
        account="ACCOUNT"
    )
    cs = conn.cursor()
    cs.execute("SELECT * FROM VEHICLE_SENSOR_DATA")
    return cs.fetchall()
