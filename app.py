import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
from dotenv import load_dotenv
import os
from process_answers import process_answers
import json
from flask import jsonify

app = Flask(__name__)

# List of questions
questions = [
    "What is your name?",
    "How old are you?",
    "What is your email?",
    "Have you experienced a week or longer of lower-than-usual interest in activities that you usually enjoy? Examples might include work, exercise, or hobbies.",
    "Could you tell me about any times over the past few months that you’ve been bothered by low feelings, stress, or sadness?",
    "Tell me about how confident you have been feeling in your capabilities recently.",
    "Can you tell me about your hopes and dreams for the future? What feelings have you had recently about working toward those goals?",
    "Describe how ‘supported’ you feel by others around you – your friends, family, or otherwise.",
    "Tell me about any important activities or projects that you’ve been involved with recently. How much enjoyment do you get from these?",
    "Do feelings of anxiety or discomfort around others bother you?"
]




@app.route('/')
def index():
    return render_template('index.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    new_answers = request.get_json()
    # Assign a unique ID to each submission
    with open('answered.json','r') as f:
        data = json.load(f)
        i = data['next']

    with open('answers.json', 'r') as f:
        answers = json.load(f)

    new_answers['id'] = i
    # Update answer ID counter
    # Insert new answers at the beginning of the dictionary
    answers = {str(new_answers['id']): new_answers, **answers}

    

    
    

    # Add new data
    data[str(new_answers['id'])] = new_answers

    # Write data back to file
    with open('answers.json', 'w') as f:
        json.dump(answers, f)

    threading.Thread(target=process).start()



    return redirect(url_for('thankyou'))

def process():
    load_dotenv()

    with open('answered.json','r') as f:
        data = json.load(f)
        i = data['next']

    with open('answers.json', 'r') as f:
        data = json.load(f)
        answers=data[str(i)]

    password=os.getenv("EMAIL_PASSWORD")
    process_answers(answers,password)

    with open('answered.json','r') as f:
        data = json.load(f)
        list = data['answered']
        list.append(i)
        data['next']+=1

@app.route('/thankyou')
def thankyou():
    
    load_dotenv()

    with open('answered.json','r') as f:
        data = json.load(f)
        i = data['next']

    with open('answers.json', 'r') as f:
        data = json.load(f)
        answers=data[str(i)]

    password=os.getenv("EMAIL_PASSWORD")
    process_answers(answers,password)

    with open('answered.json','r') as f:
        data = json.load(f)
        list = data['answered']
        list.append(i)
        data['next']+=1
    return render_template('thankyou.html')

    

if __name__ == '__main__':
    app.run(debug=True)
