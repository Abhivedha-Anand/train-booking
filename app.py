from flask import Flask, render_template, request, redirect, session
import pymysql
import random
import string
import datetime
 
app = Flask(__name__)
app.secret_key = "any-secret-key"
 
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='NishRav_67',
    database='railwayDatabase',
    port=3306
)
 
def generate_pnr():
    date_code = datetime.datetime.now().strftime("%d%m")
    random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{date_code}{random_code}"
 
def preference(pref, L, pref_type):
    if pref_type == 'seating':  # GN or 2S
        options = ['Window', 'Middle', 'Aisle']
    else:  # Sleeper or AC
        options = ['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper']
 
    if pref in options:
        lst = [options.index(pref)] + [i for i in range(len(options)) if i != options.index(pref)]
    else:
        lst = list(range(len(options)))
 
    for i in lst:
        if L[i] > 0:
            L[i] -= 1
            return options[i]
 
    if L[-1] > 0:
        L[-1] -= 1
        return 'rac'
 
    return 'waiting'
 
 
@app.route('/', methods=['GET', 'POST'])
def passengerDetailsPage():
    if request.method == 'POST':
        form = request.form
        passengers = {}
 
        for key in form:
            if '-' in key:
                field, num = key.split('-')
                if num not in passengers:
                    passengers[num] = {}
                passengers[num][field] = form[key]
 
        # Example: also collect train_no and class_code
        session['passengers'] = list(passengers.values())
        session['train_no'] = form.get('train_no')
        session['class_code'] = form.get('class_code')
        return render_template('confirmation.html', passengers=session['passengers'])
 
    return render_template('passengerDetailsPage.html')
 
@app.route('/confirm', methods=['POST'])
def confirm():
    pnr = generate_pnr()
    passengers = session.get('passengers', [])
    train_no = 12633  #session.get('train_no')
    class_code = '2S' #session.get('class_code')
 
    updated_passengers = []
 
    # Determine if class uses seating or sleeper-type preference
    if class_code in ['2S', 'GN']:
        berth_types = ['Window', 'Middle', 'Aisle']
        pref_type = 'seating'
    else:
        berth_types = ['Lower', 'Middle', 'Upper', 'Side Lower', 'Side Upper']
        pref_type = 'sleeper'
 
    seat_counts = {bt: 0 for bt in berth_types}
    seat_counts['rac'] = 6
 
    with connection.cursor() as cursor:
        query = """
            SELECT berth_type, COUNT(*) FROM seat_berths
            WHERE train_no = %s AND class_code = %s AND status = 'Available'
            GROUP BY berth_type
        """
        cursor.execute(query, (train_no, class_code))
        for row in cursor.fetchall():
            berth_type, count = row
            if berth_type in seat_counts:
                seat_counts[berth_type] = count
 
    seat_count_list = [seat_counts[bt] for bt in berth_types] + [seat_counts['rac']]
 
    with connection.cursor() as cursor:
        for p in passengers:
            pref_code = p['berth']
            allotted_berth = preference(pref_code, seat_count_list, pref_type)
 
            if allotted_berth != 'waiting' and allotted_berth != 'rac':
                seat_query = """
                    SELECT seat_number FROM seat_berths
                    WHERE train_no = %s AND class_code = %s AND berth_type = %s AND status = 'Available'
                    LIMIT 1
                """
                cursor.execute(seat_query, (train_no, class_code, allotted_berth))
                seat_row = cursor.fetchone()
 
                if seat_row:
                    seat_no = seat_row[0]
                    update_query = """
                        UPDATE seat_berths
                        SET status = 'Booked'
                        WHERE train_no = %s AND class_code = %s AND seat_number = %s
                    """
                    cursor.execute(update_query, (train_no, class_code, seat_no))
                else:
                    seat_no = "Waiting"
            else:
                seat_no = "Waiting"
 
            p['berth_allotted'] = allotted_berth
            p['seat_no'] = seat_no
 
            insert_query = """
                INSERT INTO passengers (name, age, gender, berth_preference, nationality, pnr, berth_allotted, seat_no)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                p['name'], int(p['age']), p['gender'], p['berth'], p['nationality'],
                pnr, p['berth_allotted'], p['seat_no']
            ))
 
            updated_passengers.append(p)
 
        connection.commit()
 
    return render_template('success.html', pnr=pnr, passengers=updated_passengers)
 
if __name__ == '__main__':
    app.run(debug=True)
 
