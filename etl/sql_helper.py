import psycopg2


def check_redshift_connection(redshift_connection_string):

    outcome = False

    try: 
        connection = psycopg2.connect(redshift_connection_string)
        outcome = True
    except Exception as e:
        outcome = False
        print(f"Exception while connecting to redshift {e}")
    finally:
        return outcome
