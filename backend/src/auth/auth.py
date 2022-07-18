from os import environ
import json
from flask import abort,request
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = environ.get('AUTH0_DOMAIN', 'dev-m00boybg.auth0.com')
ALGORITHMS = ['RS256']
API_AUDIENCE = environ.get('API_AUDIENCE', 'coffee')

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''


def get_token_auth_header():
#get auth header from request
    header = request.headers.get("Authorization", None)

    if not header:
        raise AuthError({"code": "header_missing",
                         "description":
                         "Authorization header absent"}, 401)
# split to get the token from it 
    parts = header.split(' ')

#check if the token is in the right format
    if len(parts) != 2 or not parts:
        raise AuthError({
            'code': 'invalid_token',
            'description': 'Invalid authorization token format'
            ' Bearer token'}, 401)

# check if the token begins with bearer
    elif parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header doesnt begin with Bearer'}, 401)

# return correct token
    return parts[1]


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the
    payload
    !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission
    string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    # check for permissions
    if 'permissions' not in payload:
        abort(400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized_access',
            'description': 'No Permission to access',
        }, 401)
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

    !!NOTE urlopen has a common certificate error described here:
    https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
  
    url = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(url.read())


    bearer_token = jwt.get_unverified_header(token)

  
    if 'kid' not in bearer_token:
        raise AuthError({
            'code': 'header_invalid',
            'description': 'Authorization not expected'
        }, 401)

    rsa_key = {}

    for key in jwks['keys']:
        if key['kid'] == bearer_token['kid']:
            rsa= {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
            break

    if rsa:
        try:
            pay = jwt.decode(
                token,
                rsa,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            return pay

    

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'claim_invalid',
                'description': 'This is an invalid claim '
              
            }, 401)

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'expired_token',
                'description': 'Sumbitted an expired token'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'header_invalid',
                'description': 'header is not in the right format.'
            }, 400)

    raise AuthError({
        'code': 'header_invalid',
        'description': 'Key missing'
    }, 400)


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims
    and check the requested permission
    return the decorator which passes the decoded payload to the
    decorated method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator