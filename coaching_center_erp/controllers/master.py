from odoo import http
from odoo.http import request, Response
import json
from werkzeug.exceptions import Forbidden

class CoachingAPIController(http.Controller):

    def _json_response(self, data, status=200):
        """ Helper to return a JSON response with CORS headers """
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type'),
        ]
        return Response(json.dumps(data), status=status, headers=headers)

    @http.route('/students_register', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False)
    def create_student(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return self._json_response({}, 200)

        try:
            data = json.loads(request.httprequest.data or '{}')
            data = data.get('data', {})  # from React

            if not data.get('name') or not data.get('phone') or not data.get('email'):
                return self._json_response({
                    'status': {
                        'success': False,
                        'error_code': 400,
                        'error_message_en': 'Missing required fields',
                        'error_message_hi': 'फ़ील्ड आवश्यक है।',
                        'error_description': 'Name, phone, and email are required.',
                    },
                    'result': {}
                }, 400)

            student = request.env['coaching.student'].sudo().create({
                'name': data.get('name'),
                'dob': data.get('dob'),
                'gender': data.get('gender'),
                'phone': data.get('phone'),
                'email': data.get('email'),
                'guardian_name': data.get('guardian_name'),
                'guardian_phone': data.get('guardian_phone'),
                'street': data.get('street'),
                'street2': data.get('street2'),
                'zip': data.get('zip'),
                'city': data.get('city'),
                'state_id': data.get('state_id'),
                'country_id': data.get('country_id'),
                'batch_id': data.get('batch_id'),
                'admission_date': data.get('admission_date'),
                'status': data.get('status', 'active'),
            })

            return self._json_response({
                'status': {
                    'success': True,
                    'error_code': 200,
                    'error_message_en': 'Student created successfully.',
                    'error_message_hi': 'छात्र सफलतापूर्वक जोड़ा गया।',
                    'error_description': 'Student registration completed.'
                },
                'result': {
                    'id': student.id,
                    'name': student.name,
                    'student_id': student.student_id,
                    'email': student.email,
                    'phone': student.phone,
                    'batch_id': student.batch_id.id if student.batch_id else None,
                }
            })

        except Exception as e:
            return self._json_response({
                'status': {
                    'success': False,
                    'error_code': 500,
                    'error_message_en': 'Internal Server Error',
                    'error_message_hi': 'सर्वर में त्रुटि हुई',
                    'error_description': str(e),
                },
                'result': {}
            }, 500)

    @http.route('/api/country_details', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False)
    def get_country_details(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return self._json_response({}, 200)

        try:
            countries = request.env['res.country'].sudo().search([])
            country_data = [{
                'id': country.id,
                'name': country.name,
            } for country in countries]

            return self._json_response({
                'status': {
                    'success': True,
                    'error_code': 200,
                    'error_message_en': 'Country details fetched successfully',
                    'error_message_hi': 'देश का विवरण सफलतापूर्वक प्राप्त किया गया।',
                    'error_description': 'Country details fetched successfully',
                },
                'result': {
                    'country_details': country_data
                }
            })

        except Exception as e:
            return self._json_response({
                'status': {
                    'success': False,
                    'error_code': 500,
                    'error_message_en': 'Failed to fetch country details',
                    'error_message_hi': 'देश का विवरण प्राप्त करने में विफल',
                    'error_description': str(e),
                },
                'result': {}
            }, 500)

    @http.route('/api/state_details', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False)
    def get_state_details(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return self._json_response({}, 200)

        try:
            data = json.loads(request.httprequest.data or '{}')
            country_id = data.get('country_id')

            if not country_id:
                return self._json_response({
                    'status': {
                        'success': False,
                        'error_code': 400,
                        'error_message_en': 'Missing country_id',
                        'error_message_hi': 'country_id आवश्यक है।',
                        'error_description': 'You must provide a valid country_id to get states.'
                    },
                    'result': {}
                }, 400)

            states = request.env['res.country.state'].sudo().search([
                ('country_id', '=', int(country_id)),
            ])

            state_data = [{
                'id': state.id,
                'name': state.name,
            } for state in states]

            return self._json_response({
                'status': {
                    'success': True,
                    'error_code': 200,
                    'error_message_en': 'State details fetched successfully',
                    'error_message_hi': 'राज्य विवरण सफलतापूर्वक प्राप्त किया गया।',
                    'error_description': 'State details fetched successfully'
                },
                'result': {
                    'state_details': state_data
                }
            })

        except Exception as e:
            return self._json_response({
                'status': {
                    'success': False,
                    'error_code': 500,
                    'error_message_en': 'Failed to fetch state details',
                    'error_message_hi': 'राज्य विवरण प्राप्त करने में विफल',
                    'error_description': str(e)
                },
                'result': {}
            }, 500)

    @http.route('/api/batch_list', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False)
    def get_batch_list(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return self._json_response({}, 200)

        try:
            batches = request.env['coaching.batch'].sudo().search([])

            batch_data = []
            for batch in batches:
                batch_data.append({
                    'id': batch.id,
                    'name': batch.name,
                })

            return self._json_response({
                'status': {
                    'success': True,
                    'error_code': 200,
                    'error_message_en': 'Batch list fetched successfully',
                    'error_message_hi': 'बैच सूची सफलतापूर्वक प्राप्त की गई।',
                    'error_description': 'Batch list fetched successfully'
                },
                'result': {
                    'batch_list': batch_data
                }
            })

        except Exception as e:
            return self._json_response({
                'status': {
                    'success': False,
                    'error_code': 500,
                    'error_message_en': 'Failed to fetch batch list',
                    'error_message_hi': 'बैच सूची प्राप्त करने में विफल',
                    'error_description': str(e)
                },
                'result': {}
            }, 500)
    
    
    @http.route('/api/subject_list', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False)
    def get_subject_list(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return self._json_response({}, 200)

        try:
            subjects = request.env['coaching.subject'].sudo().search([])

            subject_data = []
            for subject in subjects:
                subject_data.append({
                    'id': subject.id,
                    'name': subject.name,
                })

            return self._json_response({
                'status': {
                    'success': True,
                    'error_code': 200,
                    'error_message_en': 'Subject list fetched successfully',
                    'error_message_hi': 'विषय सूची सफलतापूर्वक प्राप्त की गई।',
                    'error_description': 'Subject list fetched successfully'
                },
                'result': {
                    'subject_list': subject_data
                }
            })
        

        except Exception as e:
            return self._json_response({
                'status': {
                    'success': False,
                    'error_code': 500,
                    'error_message_en': 'Failed to fetch subject list',
                    'error_message_hi': 'विषय सूची प्राप्त करने में विफल',
                    'error_description': str(e)
                },
                'result': {}
            }, 500)


    @http.route('/api/course_list', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False)
    def get_subject_list(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return self._json_response({}, 200)

        try:
            courses = request.env['coaching.course'].sudo().search([])

            course_data = []
            for course in courses:
                course_data.append({
                    'id': course.id,
                    'name': course.name,
                })

            return self._json_response({
                'status': {
                    'success': True,
                    'error_code': 200,
                    'error_message_en': 'Course list fetched successfully',
                    'error_message_hi': 'कोर्स सूची सफलतापूर्वक प्राप्त की गई।',
                    'error_description': 'Course list fetched successfully'
                },
                'result': {
                    'course_list': course_data
                }
            })
        

        except Exception as e:
            return self._json_response({
                'status': {
                    'success': False,
                    'error_code': 500,
                    'error_message_en': 'Failed to fetch Course list',
                    'error_message_hi': 'कोर्स सूची प्राप्त करने में विफल',
                    'error_description': str(e)
                },
                'result': {}
            }, 500)


    @http.route('/api/signup', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False)
    def signup(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return self._json_response({}, 200)

        try:
            data = json.loads(request.httprequest.data or '{}')
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not all([name, email, password]):
                return self._json_response({
                    'status': {
                        'success': False,
                        'error_code': 400,
                        'error_message_en': 'Missing required fields',
                        'error_message_hi': 'नाम, ईमेल और पासवर्ड आवश्यक हैं।',
                        'error_description': 'All fields are required.'
                    },
                    'result': {}
                }, 400)

            existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if existing_user:
                return self._json_response({
                    'status': {
                        'success': False,
                        'error_code': 409,
                        'error_message_en': 'User already exists',
                        'error_message_hi': 'यूज़र पहले से मौजूद है।',
                        'error_description': 'A user with this email already exists.'
                    },
                    'result': {}
                }, 409)

            user = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'email': email,
                'password': password,
            })

            return self._json_response({
                'status': {
                    'success': True,
                    'error_code': 201,
                    'error_message_en': 'User created successfully',
                    'error_message_hi': 'यूज़र सफलतापूर्वक बनाया गया।',
                    'error_description': 'Signup completed.'
                },
                'result': {
                    'user_id': user.id,
                    'name': user.name,
                    'email': user.login,
                }
            })

        except Exception as e:
            return self._json_response({
                'status': {
                    'success': False,
                    'error_code': 500,
                    'error_message_en': 'Internal server error',
                    'error_message_hi': 'सर्वर त्रुटि',
                    'error_description': str(e)
                },
                'result': {}
            }, 500)

    @http.route('/api/login', type='http', auth='public',  methods=['POST', 'OPTIONS'], csrf=False)
    def login(self, **kwargs):
        if request.httprequest.method == 'OPTIONS':
            return self._json_response({}, 200)
        login = kwargs.get('login')
        password = kwargs.get('password')

        if not login or not password:
            return self._json_response({
                'status': {
                    'success': False,
                    'error_code': 400,
                    'error_message_en': 'Username and password are required',
                    'error_message_hi': 'यूज़रनेम और पासवर्ड आवश्यक हैं।',
                    'error_description': 'Missing login credentials.'
                },
                'result': {}
            }, 400)

        user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        if not user:
            return self._json_response({
                'status': {
                    'success': False,
                    'error_code': 401,
                    'error_message_en': 'Invalid user or credentials',
                    'error_message_hi': 'अमान्य यूज़र या पासवर्ड।',
                    'error_description': 'User not found with given email.'
                },
                'result': {}
            }, 401)

        try:
            credentials = {'login': login, 'password': password, 'type': 'password'}
            request.session.authenticate(request.db, credentials)

            return self._json_response({
                'status': {
                    'success': True,
                    'error_code': 200,
                    'error_message_en': 'Login successful',
                    'error_message_hi': 'लॉगिन सफल रहा',
                    'error_description': 'User authenticated successfully.'
                },
                'result': {
                    'user_id': user.id,
                    'user_name': user.name,
                    'user_email': user.login,
                    'session_id': request.session.sid,
                }
            })

        except Exception as e:
            return self._json_response({
                'status': {
                    'success': False,
                    'error_code': 500,
                    'error_message_en': 'Internal Server Error',
                    'error_message_hi': 'सर्वर त्रुटि',
                    'error_description': str(e)
                },
                'result': {}
            }, 500)

    
