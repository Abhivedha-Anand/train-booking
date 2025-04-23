from flask import Flask, render_template, request, redirect, session
import pymysql
import random
import string
import datetime

app = Flask(__name__)
app.secret_key = "any-secret-key"  # Needed to use sessions

connection = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='01022004',
    database='railwaydb'
)

def generate_pnr():
    date_code = datetime.datetime.now().strftime("%d%m")
    random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{date_code}{random_code}"

def preference(pref, L):
    if pref == 'L':
        lst = [0, 1, 2, 3, 4]
    elif pref == 'M':
        lst = [1, 0, 2, 3, 4]
    elif pref == 'U':
        lst = [2, 0, 1, 3, 4]
    elif pref == 'SL':
        lst = [3, 0, 1, 2, 4]
    elif pref == 'SU':
        lst = [4, 0, 1, 2, 3]
    else:
        lst = [0, 1, 2, 3, 4]

    for i in lst:
        if L[i] > 0:
            L[i] -= 1
            return ['L', 'M', 'U', 'SL', 'SU'][i]
    if L[5] > 0:
        L[5] -= 1
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

        passenger_list = list(passengers.values())
        
        session['passengers'] = passenger_list
        return render_template('confirmation.html', passengers=passenger_list)

    return render_template('passengerDetailsPage.html')

@app.route('/confirm', methods=['POST'])
def confirm():
    pnr = generate_pnr()
    passengers = session.get('passengers', [])

    seat_counts = [1, 1, 1, 1, 1, 1]  # Customize seat counts here

    updated_passengers = []

    with connection.cursor() as cursor:
        for p in passengers:
            berth_pref = p['berth']
            allotted_berth = preference(berth_pref[0], seat_counts)
            p['berth_allotted'] = allotted_berth
            p['seat_no'] = ""  # Leave blank for now

            # Save to DB
            query = "INSERT INTO passengers (name, age, gender, berth_preference, nationality, pnr, berth_allotted, seat_no) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (
                p['name'], int(p['age']), p['gender'], p['berth'], p['nationality'],
                pnr, p['berth_allotted'], p['seat_no']
            ))

            updated_passengers.append(p)

        connection.commit()


    # with connection.cursor() as cursor:
    #     for p in passengers:
    #         query = "INSERT INTO passengers (name, age, gender, berth_preference, nationality, pnr) VALUES (%s, %s, %s, %s, %s, %s)"
    #         cursor.execute(query, (p['name'], int(p['age']), p['gender'], p['berth'], p['nationality'], pnr))
    #     connection.commit()

    session.pop('passengers', None)  # clear after storing
    return render_template('success.html', pnr=pnr, passengers=updated_passengers)
if __name__ == '__main__':
    app.run(debug=True)
