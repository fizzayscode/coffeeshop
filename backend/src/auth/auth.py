import json

from flask import request, _request_ctx_stack,abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'fizzayscode.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'


## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})




## Auth Header
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
    return response

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''

# method to check if there's a key authorization in request header then remove the bearer from the authrorization
#  array and return only the token itself.
def get_token_auth_header():
    # check if theres no key authrorization in the header that was sent then raise an error if there wasnt
    if 'Authorization' not in request.headers:
         raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

    # then get the authorization result store it in a variable
    auth_header=request.headers.get('Authorization')
    
    # then i split it on space becauase the authorization comes in with the token and a bearer
    headers_parts=auth_header.split(' ')
    
   # checking to see the request i got from header after
   #  splitting it to an array is actually conatining 2 elements the bearer and the token itself  
#    if it is greater greater than two then throw error
    if len(headers_parts)!=2:
        raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

    # if it lesser than two throw an error
    if len(headers_parts) < 2:
        raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)
    
    if len(headers_parts) > 2:
        raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)
    
    # then run the next command cause we are now sure it is two elements contained
    # then checking to see if the first element in the array after the split is not  actually containing bearer
    # changed the result to lowercase to actually be able to compare with the lowercase beaerer
    if headers_parts[0].lower()!="bearer":
         raise AuthError({
                'code': 'invalid_header',
                'description': 'theres is no bearer contained in the token.'
            }, 400)
    
    # if it actually contains the bearer then i was get get rid of the bearer and return my key that is the second element in  the arraylist
    # print(headers_parts)
    return headers_parts[1]

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    # checking to see if theres a key 'permission' in my payload that was decoded by verify_decode_jwt method if there is not then rasise an error
        if 'permissions' not in payload:
              raise AuthError({
                    'code': 'invalid_claims',
                    'description': 'Permissions is not included in the jwt.'
                }, 400)
        # checking to see if that permissions array is not actually existing in the payload 
        if permission not in payload['permissions']:
           raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)


        # then return a boolean true if theres permission and actual elements in the permissions array
        return True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''

#Method to decode and verify the jwt token that was sent, takes in our token as parameter to verify if its valid
def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    
    # this gets our data header that was sent through our postman 
    unverified_header = jwt.get_unverified_header(token)
    
    # ?this uses a certian algorithm to decode with the key
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

             # Finally, verify!!!
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # getting my token to store in the local varibale token
            token = get_token_auth_header()
            try:
                # then im trying to decode that token from calling the method to verify my token and return me my payload for use
                # if somethign went wrong it should abort
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            # after getting my payload i am trying to check if the user making that request is actually allowed to maje that request
            # that is taking the permission im giving from my decorator as a string and comparin
            # g to see if a user is allowed in my payload permissions data
            check_permissions(permission, payload)
            return f(payload,*args,**kwargs)
        return wrapper
    return requires_auth_decorator

    

  