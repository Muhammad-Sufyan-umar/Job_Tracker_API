
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
db=SQLAlchemy()


class JobApplication(db.Model):
    __table_args__ = (
    UniqueConstraint('company_name','job_title', name='unique_company_job'),
)
    id=db.Column(db.Integer,primary_key=True)
    company_name=db.Column(db.String(100),nullable=False)
    job_title=db.Column(db.String(100),nullable=False)
    location=db.Column(db.String(100))
    salary=db.Column(db.Float)
    application_date=db.Column(db.Date,nullable=False)
    status=db.Column(db.String(20),nullable=False,default='Applied')
    notes=db.Column(db.Text)

    
    



