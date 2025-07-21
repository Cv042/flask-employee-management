from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Employee(db.Model):
    """Employee model for database operations"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Numeric(10, 2), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Employee {self.name}>'
    
    def to_dict(self):
        """Convert employee object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'position': self.position,
            'salary': float(self.salary),
            'hire_date': self.hire_date.strftime('%Y-%m-%d') if self.hire_date else None,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    @staticmethod
    def search_employees(search_term, page=1, per_page=12, sort_by='name', sort_order='asc'):
        """Search employees with pagination and sorting"""
        query = Employee.query
        
        # Apply search filter
        if search_term:
            search_filter = f'%{search_term}%'
            query = query.filter(
                db.or_(
                    Employee.name.ilike(search_filter),
                    Employee.email.ilike(search_filter),
                    Employee.department.ilike(search_filter),
                    Employee.position.ilike(search_filter)
                )
            )
        
        # Apply sorting
        if sort_by and hasattr(Employee, sort_by):
            sort_column = getattr(Employee, sort_by)
            if sort_order.lower() == 'desc':
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(Employee.name.asc())
        
        # Apply pagination
        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    @staticmethod
    def get_departments():
        """Get all unique departments"""
        return [dept[0] for dept in db.session.query(Employee.department.distinct()).all()]
    
    @staticmethod
    def get_statistics():
        """Get employee statistics"""
        total_employees = Employee.query.count()
        dept_stats = db.session.query(
            Employee.department,
            db.func.count(Employee.id).label('count')
        ).group_by(Employee.department).all()
        
        return {
            'total_employees': total_employees,
            'departments': [{'name': dept, 'count': count} for dept, count in dept_stats]
        }