
from flask import Blueprint, request
from models import db, JobApplication
from validators import validate_application
from sqlalchemy.exc import IntegrityError
from datetime import datetime

routes = Blueprint('routes', __name__)


# ==========================================================
# HOME
# ==========================================================

@routes.route('/')
def home():
    return {
        'Message': 'Job Application Tracker API',
        'Status': 'Running'
    }, 200


# ==========================================================
# SERIALIZER
# ==========================================================

def serialize_application(application):
    return {
        'id': application.id,
        'company_name': application.company_name,
        'job_title': application.job_title,
        'location': application.location,
        'salary': application.salary,
        'application_date': (
            application.application_date.strftime('%Y-%m-%d')
            if application.application_date else None
        ),
        'status': application.status,
        'notes': application.notes
    }


# ==========================================================
# CREATE APPLICATION - POST
# ==========================================================

@routes.route('/applications', methods=['POST'])
def create_application():

    data = request.get_json(silent=True)

    data, error = validate_application(data)

    if error:
        return data, error

    new_application = JobApplication(
        company_name=data['company_name'],
        job_title=data['job_title'],
        location=data['location'],
        salary=data['salary'],
        application_date=data['application_date'],
        status=data['status'],
        notes=data['notes']
    )

    try:
        db.session.add(new_application)
        db.session.commit()

        return {
            'message': 'Application created successfully',
            'id': new_application.id
        }, 201

    except IntegrityError:
        db.session.rollback()
        return {'error': 'Duplicate entry or invalid data'}, 409

    except Exception:
        db.session.rollback()
        return {'error': 'Application failed to create'}, 500


# ==========================================================
# GET ALL APPLICATIONS - GET
# FILTER + SEARCH + DATE RANGE + SORT + PAGINATION
# ==========================================================

@routes.route('/applications', methods=['GET'])
def get_all():

    query = JobApplication.query

    # ---------------- STATUS FILTER ----------------

    status = request.args.get('status')

    allowed_status = [
        'Applied',
        'Interview',
        'Accepted',
        'Rejected'
    ]

    if status and status not in allowed_status:
        return {
            'error': 'Invalid status',
            'allowed_status': allowed_status
        }, 400

    if status:
        query = query.filter_by(status=status)

    # ---------------- COMPANY SEARCH ----------------

    company = request.args.get('company')

    if company:
        query = query.filter(
            JobApplication.company_name.ilike(f'%{company.strip()}%')
        )

    # ---------------- DATE RANGE FILTER ----------------

    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    start_date = None
    end_date = None

    if date_from:
        try:
            start_date = datetime.strptime(
                date_from, '%Y-%m-%d'
            ).date()

        except ValueError:
            return {'error': 'date_from must be YYYY-MM-DD'}, 400

    if date_to:
        try:
            end_date = datetime.strptime(
                   date_to, '%Y-%m-%d'
            ).date()

        except ValueError:
            return {'error': 'date_to must be YYYY-MM-DD'}, 400

    if start_date and end_date and start_date > end_date:
        return {
            'error': 'date_from cannot be later than date_to'
        }, 400

    if start_date:
        query = query.filter(
            JobApplication.application_date >= start_date
        )

    if end_date:
        query = query.filter(
            JobApplication.application_date <= end_date
        )

    # ---------------- SORTING ----------------

    sort = request.args.get('sort')

    allowed_sort = [
        'salary_asc',
        'salary_desc',
        'date_newest',
        'date_oldest'
    ]

    if sort and sort not in allowed_sort:
        return {
            'error': 'Invalid sort option',
            'allowed_sort': allowed_sort
        }, 400

    if sort == 'salary_asc':
        query = query.order_by(JobApplication.salary.asc())

    elif sort == 'salary_desc':
        query = query.order_by(JobApplication.salary.desc())

    elif sort == 'date_newest':
        query = query.order_by(
            JobApplication.application_date.desc()
        )

    elif sort == 'date_oldest':
        query = query.order_by(
            JobApplication.application_date.asc()
        )

    # ---------------- TOTAL COUNT ----------------

    total = query.count()

    # ---------------- PAGINATION ----------------

    page = request.args.get('page', '1')
    limit = request.args.get('limit', '5')

    try:
        page = int(page)
        limit = int(limit)

    except ValueError:
        return {
            'error': 'Page and limit must be integers'
        }, 400

    if page < 1 or limit < 1 or limit > 100:
        return {
            'error': 'Page must be positive and limit must be between 1 and 100'
        }, 400

    applications = query.offset(
        (page - 1) * limit
    ).limit(limit).all()

    # ---------------- RESPONSE ----------------

    result = [
        serialize_application(application)
        for application in applications
    ]

    return {
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': (total + limit - 1) // limit,
        'applications': result
    }, 200


# ==========================================================
# GET APPLICATION BY ID
# ==========================================================

@routes.route('/applications/<int:application_id>', methods=['GET'])
def get_by_id(application_id):

    application = db.session.get(
        JobApplication, application_id
    )

    if not application:
        return {'error': 'Application not found'}, 404

    return {
        'application': serialize_application(application)
    }, 200


# ==========================================================
# UPDATE APPLICATION - PATCH
# ==========================================================

@routes.route('/applications/<int:application_id>', methods=['PATCH'])
def update_application(application_id):

    application = db.session.get(
        JobApplication, application_id
    )

    if not application:
        return {'error': 'Application not found'}, 404

    data = request.get_json(silent=True)

    data, error = validate_application(data, partial=True)

    if error:
        return data, error

    if not data:
        return {'error': 'No fields provided for update'}, 400

    for field, value in data.items():
        setattr(application, field, value)

    try:
        db.session.commit()

        return {
            'message': 'Application updated successfully'
        }, 200

    except IntegrityError:
        db.session.rollback()
        return {'error': 'Duplicate entry or invalid data'}, 409

    except Exception:
        db.session.rollback()
        return {'error': 'Failed to update application'}, 500


# ==========================================================
# DELETE APPLICATION
# ==========================================================

@routes.route('/applications/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):

    application = db.session.get(
        JobApplication, application_id
    )

    if not application:
        return {'error': 'Application not found'}, 404

    try:
        db.session.delete(application)
        db.session.commit()

        return {
            'message': 'Application deleted successfully'
        }, 200

    except Exception:
        db.session.rollback()
        return {'error': 'Failed to delete application'}, 500
