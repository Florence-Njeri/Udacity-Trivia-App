import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    # CORS(app, resources={r"*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers 
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=["GET"])
    def available_categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)
        category = []
        for categ in categories:
            category.append({
                "id": categ.id,
                "type": categ.type
            })

        return jsonify({
            'success':True,
            'categories': None,
            'total_categories': len(categories)
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=["GET"])
    def questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request,selection)
        categories = Category.query.order_by(Category.id).all()

        if len(current_questions) == 0:
            abort(404)
        category = []
        for categ in categories:
            category.append({
                "id": categ.id,
                "type": categ.type
            })
        
        return jsonify({
            'success':True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': None,
            'categories': category
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()

            if question is None:
                abort(404)
            else:  
                question.delete() 
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request,selection)
                
                return jsonify({
                    'success': True,
                    'deleted': question.id,
                    'questions': current_questions,
                    'total_questions': len(selection)
                })

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=["POST"])
    def create_question():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)

        try:
            question = Question(question, answer, category, difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request,selection)

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    'questions': current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get("searchTerm", None)
        selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).order_by(Question.id).all()
        if (len(selection) == 0):
            abort(404)

        current_questions = paginate_questions(request,selection)

        return jsonify(
                {
                    "success": True,
                    'questions': current_questions,
                    "total_questions": len(selection),
                    "current_category": None
                }
            )

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=["GET"])
    def questions_by_category(category_id):
        category = Category.query.get_or_404(category_id)

        if category is None:
            abort(404)
            
        questions = Question.query.filter_by(category = category_id).all()
        body = request.get_json()
        category = body.get("category", None)

        # selection = Question.query.filter(Question.category.all([category])).one_or_none()
        selection = Question.query.filter((Question.category) == str(category.id)).order_by(Question.id).all()
        current_questions = paginate_questions(request,selection)
        if len(current_questions) == 0:
            abort(404)

        return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(questions),
                    "current_category": category.type
                }
            )

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=["POST"])
    def play():
        body = request.get_json()

        previous_questions = body.get("previous_questions", None)
        category = body.get("quiz_category", None)

        if (previous_questions is None) or  (category is None):
            abort(400)

        if category.id == 0:
            questions = Question.id.not_in(previous_questions)

        selection = Question.query.filter(category == category).filter(Question.id.in_(previous_questions)).order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            "success": True,
            'questions': current_questions,
            "total_questions": len(Question.query.all()),
            "current_category": category.type
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):   
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "Not found"
            }), 400

    @app.errorhandler(404)
    def not_found(error):   
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404


    @app.errorhandler(422)
    def unprocessable(error):   
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "Unprocessable"
            }), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):   
        return jsonify({
            "success": False, 
            "error": 500,
            "message": "Unprocessable"
            }), 500

    return app

