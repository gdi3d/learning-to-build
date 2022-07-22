from flask import jsonify, make_response

def APIResponse(data, message, message_code, http_code, fields={}):
    """DRF response object

    Returns a DRF response object with
    a predeclared model
    
    [description]
    :param data: Data to sent on the response.
                 It can be a dictionary or None
    :type data: dict, none
    :param message: A human readable response about
                    the response of the operation
    :type message: str
    :param message_code: A code representing the response
    :type message_code: str
    :param http_code: The HTTP status code of the response
    :type http_code: int
    :param fields: If there's any validation errors on the payload
                    we indicate here the fields and the errors
                    generally using the format of DRF serializer errors, defaults to {}
    :type fields: dict, optional
    :param content_type: The content type of the response, defaults to "application/json"
    :type content_type: str, optional
    :returns: DRF Response object
    :rtype: {rest_framework.response.Response}
    """
    
    if not data:
        data = {}

    data = {
        'data': data,
        'message': message,
        'message_code': message_code,
        'http_code': http_code,
        'error_fields': fields,
    }

    return make_response(jsonify(data), http_code)