from datetime import datetime
import math


def validate_application(data, partial=False):
    if not isinstance(data, dict) or not data:
        return {'error': 'Valid data must be provided'}, 400

    cleaned = {}

    # Required fields for POST; optional for PATCH
    required_fields = ['company_name', 'job_title', 'application_date']

    for field in required_fields:
        if not partial and field not in data:
            return {'error': f'{field} is required'}, 400

    # Company Name
    if 'company_name' in data:
        value = data['company_name']
        if not isinstance(value, str) or not value.strip():
            return {'error': 'Company name must be a non-empty string'}, 400
        cleaned['company_name'] = value.strip()

    # Job Title
    if 'job_title' in data:
        value = data['job_title']
        if not isinstance(value, str) or not value.strip():
            return {'error': 'Job title must be a non-empty string'}, 400
        cleaned['job_title'] = value.strip()

    # Application Date
    if 'application_date' in data:
        value = data['application_date']
        if not isinstance(value, str):
            return {'error': 'Date must be YYYY-MM-DD'}, 400
        try:
            cleaned['application_date'] = datetime.strptime(
                value, '%Y-%m-%d'
            ).date()
        except ValueError:
            return {'error': 'Date must be YYYY-MM-DD'}, 400

    # Salary
    if 'salary' in data or not partial:
        salary = data.get('salary')
        if salary is not None:
            if isinstance(salary, bool) or not isinstance(salary, (int, float)):
                return {'error': 'Salary must be a number'}, 400
            if not math.isfinite(salary) or salary <= 0:
                return {'error': 'Salary must be finite and greater than 0'}, 400
        cleaned['salary'] = salary

    # Status
    if 'status' in data or not partial:
        status = data.get('status', 'Applied')
        if not isinstance(status, str) or status not in (
            'Applied', 'Interview', 'Accepted', 'Rejected'
        ):
            return {'error': 'Invalid application status'}, 400
        cleaned['status'] = status

    # Optional text fields
    for field in ['location', 'notes']:
        if field in data or not partial:
            value = data.get(field)
            if value is not None:
                if not isinstance(value, str):
                    return {'error': f'{field} must be a string'}, 400
                value = value.strip()
            cleaned[field] = value

    return cleaned, None

