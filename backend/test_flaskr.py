import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_pagination_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_questions_405(self):
        res = self.client().post("/questions")

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()["success"], False)

    def test_delete_question(self):
        id =  Question.query.all()[-1]
        self.client().delete("/questions/8")
        question = Question.query.filter(Question.id == 8).one_or_none()
        self.assertEqual(question, None)

    def test_get_deleted_question_405(self):
        res = self.client().post("/questions/800")

        self.assertEqual(res.status_code, 405)

    def test_create_question(self):
        data = {
            "question": "Who authored the Lies of Locke Lamora?",
            "answer": "Scott Lynch",
            "difficulty": "1",
            "category": "5"
        }
        res = self.client().post("/questions", json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(len(data["questions"]))
    
    def test_create_question_400(self):
        data = {
            "question": "Who authored the Lies of Locke Lamora?",
            "answer": "Scott Lynch",
            "difficulty": "",
            "category": ""
        }
        res = self.client().post("/questions", json=data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.get_json()["success"], False)

    def test_create_question_405(self):
        data = {
            "question": "Who authored the Lies of Locke Lamora?",
            "answer": "Scott Lynch",
            "difficulty": "",
            "category": ""
        }
        res = self.client().put("/questions", json=data)

        self.assertEqual(res.status_code, 405)
    
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])

    def test_get_categories_405(self):
        res = self.client().post("/categories")

        self.assertEqual(res.status_code, 405)

    def test_search_question(self):
        data = {"searchTerm": "American"}
        res = self.client().post("questions/search", json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
    
    def test_search_question_404(self):
        data = {"searchTerm": "Americanzzzzzzzzzzz"}
        res = self.client().post("questions/search", json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_questions_by_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], False)

    def test_questions_by_category(self):
        res = self.client().get("/categories/134567/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_play_quiz(self):
        data = {
            "quiz_category": {"id": 1 },
            "previous_questions": []
        }
        res = self.client().post("/quizzes", json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))

    def test_play_quiz_404(self):
        data = {
            "quiz_category": {"id": 10000 },
            "previous_questions": []
        }
        res = self.client().post("/quizzes", json=data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()