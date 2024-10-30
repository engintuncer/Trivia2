from flask import Flask, render_template, request
import requests
import random
import html

app = Flask(__name__, template_folder="web_app/templates")


# Fetch categories
def fetch_categories():
    url = "https://opentdb.com/api_category.php"
    response = requests.get(url)
    categories = response.json()["trivia_categories"]
    return {str(cat['id']): cat['name'] for cat in categories}

# Fetch questions
def fetch_trivia_questions(amount=5, category=None, difficulty=None):
    url = "https://opentdb.com/api.php"
    params = {
        "amount": amount,
        "type": "multiple"
    }
    if category:
        params["category"] = category
    if difficulty:
        params["difficulty"] = difficulty

    response = requests.get(url, params=params)
    data = response.json()
    if data["response_code"] == 0:
        questions = data["results"]
        for question in questions:
            question['question'] = html.unescape(question['question'])
            question['correct_answer'] = html.unescape(question['correct_answer'])
            question['incorrect_answers'] = [html.unescape(ans) for ans in question['incorrect_answers']]
        return questions
    return []

# Home page route
@app.route('/')
def index():
    categories = fetch_categories()
    return render_template('index.html', categories=categories)

# Fetch and display questions
@app.route('/get_questions', methods=['POST'])
def get_questions():
    data = request.form
    amount = int(data.get('amount', 5))
    category = data.get('category', None)
    difficulty = data.get('difficulty', None)
    questions = fetch_trivia_questions(amount=amount, category=category, difficulty=difficulty)
    return render_template('questions.html', questions=questions, score=0, current=0)

# Check answer and proceed
@app.route('/check_answer', methods=['POST'])
def check_answer():
    questions = eval(request.form['questions'])
    current = int(request.form['current'])
    selected_answer = request.form['answer']
    score = int(request.form['score'])

    correct_answer = questions[current]['correct_answer']
    if selected_answer == correct_answer:
        score += 1

    current += 1
    if current < len(questions):
        return render_template('questions.html', questions=questions, score=score, current=current)
    else:
        return render_template('score.html', score=score, total=len(questions))

if __name__ == '__main__':
    app.run(debug=True)
