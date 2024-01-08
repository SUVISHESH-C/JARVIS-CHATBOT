# app.py
from flask import Flask, request, jsonify
import pymysql


app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'db': 'course_selection',
    'cursorclass': pymysql.cursors.DictCursor  # This sets the cursor to return results as dictionaries
}

# Initialize MySQL connection
connection = pymysql.connect(**db_config)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)
    intent = req['queryResult']['intent']['displayName']
    fee=10000
    discount=0
    if intent == 'course_selection':
        student_name = req['queryResult']['parameters']['cust_name']
        course_name = req['queryResult']['parameters']['course_name']
        counted = check_count(course_name)
        if counted < 60:
            insert_data(student_name, course_name)
            if counted < 18:
                discount = fee - (fee * 30/100)
                response = {
                    'fulfillmentText': f'Registration successful! Thank you, {student_name}.'
                                       f' You are enrolled in {course_name}.'
                                       f'Hurray you have got the discount of 30 percent for the '
                                       f'course and the amount is {discount}.'
                                       f'Is there anything which i provide you.'
                }
            else :
                response = {
                    'fulfillmentText': f'Registration successful! Thank you, {student_name}.'
                                       f' You are enrolled in {course_name}.'
                                       f'Is there anything which i can provide you.'
                }
        else:
            response = {
                'fulfillmentText': f'sorry for the inconvience sir/madam.The slots are'
                                   f' filled you can wait untill the next term or '
                                   f'choose any other course to improvise the skills'
            }
        return jsonify(response)

    elif intent == 'Default Welcome Intent':
        response1 = {
            'text': {'text': ['Welcome! How can I assist you today?'
                              'Please be polite and descriptive in nature so that '
                              'we can have effective conversation..']}
        }
        response2 = {
            'text': {'text': ['These courses are specifically designed for the students '
                              'from engineering branch..I can provide the list of courses..'
                              'I can Describe courses, fetch you with number of students in your '
                              'desired field,course with highest students,discount offer for the'
                              ' specific students,details about fee structure,professors '
                              'teaching the course,	prerequisities of every course,'
                              'duration of course and '
                              'finally why choose jarvis to shape your career']}
        }

        return jsonify({
            'fulfillmentMessages': [response1, response2]
        })

    elif intent == 'count_check':
        course_name = req['queryResult']['parameters']['course_name']
        count = check_count(course_name)
        if count == 60:
            response = {
                'fulfillmentText': 'The slots are already full ,'
                                    'you cannot enroll in this course as this course '
                                   'exceeds the count of 60.'
                                   'You can try for any other courses present in the list'
                                   ' to improve your horizon of knowledge'
            }
        else:
            response = {
                'fulfillmentText': f'Number of students enrolled in the course named {course_name} '
                        f'until now is {count}.You can check for any discounts ,'
                                   f'for example :discount of particular(name) course '
            }
        return jsonify(response)
    elif intent == 'max_course':
        return get_most_common_course()


def check_count(course_name):
    try:
        with connection.cursor() as cursor:
            # Your SQL query to fetch the count of a specific course
            sql = f"SELECT COUNT(*) as count FROM students WHERE course = %s"
            cursor.execute(sql, (course_name,))
            result = cursor.fetchone()

            # Extract count from the result and return it as an integer
            count = result['count'] if result else 0

            # Print or use the count variable as needed
            print(f"Count of {course_name}: {count}")

            # Return the count as an integer
            return count
    except Exception as e:
        return jsonify({'error': f"Error fetching data from the database: {e}"}), 500

# ...


def insert_data(student_name, course_name):
    try:
        with connection.cursor() as cursor:
                # Your SQL query to insert data into the database
            sql = "INSERT INTO students (name, course) VALUES (%s, %s)"
            cursor.execute(sql, (student_name, course_name))
        connection.commit()
    except Exception as e:
        print(f"Error inserting data into the database: {e}")


# ...

def get_most_common_course():
    try:
        with connection.cursor() as cursor:
            # Your SQL query to get the most common course and its count
            sql = ("SELECT course, COUNT(*) as course_count FROM students GROUP BY "
                   "course ORDER BY course_count DESC LIMIT 1")
            cursor.execute(sql)
            result = cursor.fetchone()

            if result:
                most_common_course = result['course']
                course_count = result['course_count']

                response = {
                    'fulfillmentText': f'The most sort out course is {most_common_course} '
                                       f'with the student count of {course_count}.'
                }
            else:
                response = {'fulfillmentText': 'No data available'}

            return jsonify(response)

    except Exception as e:
        return jsonify({'error': f"Error fetching data from the database: {e}"}), 500

# ...


if __name__ == '__main__':
    app.run(debug=True)
