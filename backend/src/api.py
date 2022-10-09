from ast import Delete
import os
from queue import Empty
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''

db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

# created a get drinks route which fetches the short form representation of drinks
@app.route("/drinks")
# called the wrapper method for role permisions i created and passed the arguegemt 
# to get drinks if the individual is allowed to accssed then it brings it forth
@requires_auth('get:drinks')
def get_drinks_short_recipe(payload):
    # query to get all the drinks the coffee shop
    drinks=Drink.query.all()

    # list of an empty array initialized ready to be populated 
    drinks_short=[]

    # then i iterate over the list i got from from getting all the element in the database
    for drink in drinks:
    
        # then i chose a way to display them that is the short representaion
        drinks_short.append(drink.short())
    
    # if the drink after populating is still none then it should throw and error
    if drinks_short is None:
        abort(401)

    # else return a jsonify of the drinks short description
    return jsonify({
        "success":True,
        "drinks":drinks_short
     })



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drink-details")
@requires_auth('get:drink-details')
def get_drink_details(payload):
    # query to get all the drinks from my database
    drinks=Drink.query.all()
     
    #  initialized an empty list ready to be populated 
    drinks_long=[]
     

    #  iterated over all the drinks i got from the database 
    for drink in drinks:
    #  then added all to my empty list to display long details of the data
        drinks_long.append(drink.long())
    # if it didnt update the list then there was an error which should abort the operation
    if drinks_long is None:
        abort(401)
    
    # if there was no error bring forth this representation with status code of 200
    return jsonify({
        "success":True,
        "drinks":drinks_long
     }),200


    

    



'''
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    # got the body from the request body thta is a json object 
    body= request.get_json()
    
    # if it didnt get any body from the request then theres is nothing to post it should abort 
    if body is None:
        abort(401)
    
    # else i have a key of title and recipe which is the name of the field in my frontend that i am trying to get my data from
    # if both arent given valid credentials or inputted it should abort
    if ("title" and "recipe" not in body):
            abort(422)
    
    # else they actually supplied a data to be stored then i get them and save them in a local variable
    try:
        drink_title=body.get("title")

        ingredients=body.get("recipe")

        # Converts input dictionary into string and stores it as a json_string
        # had to do this because it was not convertting it to a dictionary before storing, error was 'cant adapt to type dict'
        real_recipe=json.dumps(ingredients)
        
        # after converting it to a dict now i can create a new object for drink
        posted_drink= Drink(title=drink_title,recipe= real_recipe)
        
        # then i inserted to my database
        posted_drink.insert()

        # it should return this if everything goes well 
        return jsonify({
            "success":True,
            "drinks":posted_drink.long()
        })
        # else it should run this except block if there was an issue after the try
    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
# i have to get the drink_id from the argument so as to know which particular data i am trying to fetch to update 
def edit_drink(payload,drink_id):

    # then i rrun a query to fetch my data based on that predefined id and store it in a local varibale
    particular_drink_to_update= Drink.query.filter_by(id=drink_id).first()
    
    # if i didnt get my data something went wrong or the data does not exist it should abort
    if not particular_drink_to_update:
        abort(404)
    
    #  else uts a b=valid id then i want to get the request body 
    body= request.get_json()
    
    # if nothung was supplied then it should discard the update operation
    if body is None:
        abort(401)

    try:
        # if both my key title and recipe is in the body that means i want to update both at the same time 
      if "title" in body and "recipe" in body:

        # it should carry out this operation, get the value and store them in a local varibale 
            particular_drink_to_update.title =body.get("title")
            ingredients=body.get("recipe")

            #  had to Convert input dictionary into string and stores it as a json_string in my real recipe variable
            real_recipe=json.dumps(ingredients)
            
            # then i updated that so called recipe of the drink i wantto update 
            particular_drink_to_update.recipe=(real_recipe)

        #  or that means i wasnt supplied with both credentials, i was suppilied with just 1 in that case i want to update just that 1
      if "title" in body :
        # if it was just title i got update the title
        particular_drink_to_update.title =body.get("title")


    #   else if it was just the recipe , update the recipe and leave title as is 
      elif "recipe" in body:
         ingredients=body.get("recipe")
         real_recipe=json.dumps(ingredients)

    #    update the recipe
         particular_drink_to_update.recipe=(real_recipe)

            # real_recipe=json.dumps(ingredients)

            # updated_drink= Drink(title=drink_title,recipe= real_recipe)

    #  then update is and return the full representation of this if there was no error at all
      particular_drink_to_update.update()
      return jsonify({
              "success":True,
             "drinks":[particular_drink_to_update.long()]
        })
    #  else if there was an error in this operation throw an error
    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
# i have to get the drink_id from the argument so as to know which particular data i am trying to fetch to update 
def delete_drink(payload,drink_id):

     # then i rrun a query to fetch my data based on that predefined id and store it in a local varibale
     particular_drink_to_del= Drink.query.filter(Drink.id==drink_id).first()
     
    #  if no valid drink with that id abort
     if not particular_drink_to_del:
        abort(404)
    #  else delete that particular data from my database
     try:
        particular_drink_to_del.delete()

    #  and give back this as a response
        return jsonify({
             "success":True,
             "delete":particular_drink_to_del.id
        })
        # if there was an error in the operation thrpw this error
     except:
        abort(422)







# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
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

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def un_authenticated(auth_error):
    return jsonify({
        "success":False,
        "error":auth_error.status_code,
        "message":auth_error.error

    }),401

