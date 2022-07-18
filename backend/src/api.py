import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks_available = Drink.query.all()
    drinks= [drink.short() for drink in drinks_available]

    return jsonify({
        "status": "ok",
        'drinks': drinks
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    drinks_available = Drink.query.all()
    drinks=[drink.long() for drink in drinks_available]

    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    req = request.get_json()
    drink_now = Drink()
    drink_now.title = req['title']
    recipe = req['recipe']
    if isinstance(recipe, dict):
        recipe = [recipe]
        drink_now.recipe = json.dumps(recipe)

    try:
        drink_now.insert()

    except BaseException:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink_now.long()]})


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    req_title = request.get_json().get('title')
    req_recipe = request.get_json().get('recipe')
    drink_to_update = Drink.query.filter(Drink.id == id).one_or_none()
    drink_to_update.title = req_title
    drink_to_update.recipe = json.dumps(request.get_json())

    if not drink_to_update:
        abort(404)

    try:
        drink_to_update.update()

    except BaseException:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink_to_update.long()]}), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink_to_delete = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink_to_delete:
        abort(404)

    try:
        drink_to_delete.delete()
    except BaseException:
        abort(400)

    return jsonify({'success': True, 'delete': id}), 200



'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Request is uprocessible"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "resource not found",
        "error": 404,
   
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "message": 'Error occurred on server',
        "error": 500
       
    }), 500


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "message": 'Unauthorized to use method',
        "error": 405

    }), 405



@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "message": error.error['description'],
        "error": error.status_code
        
    }), error.status_code


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "message": 'Reques Bad',
        "error": 400
  
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "message": 'Unathorized to perform action',
        "error": 401
    }), 401

