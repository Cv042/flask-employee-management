from flask import Blueprint, render_template, request, jsonify, current_app
from app.models import Employee
import math

# Create blueprint
employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/')
def index():
    """Main page with employee list"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'name', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)
    
    # Get pagination configuration
    per_page = current_app.config.get('POSTS_PER_PAGE', 12)
    
    # Search and paginate employees
    employees = Employee.search_employees(
        search_term=search,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Get departments for filter dropdown
    departments = Employee.get_departments()
    
    # Calculate pagination info
    pagination_info = get_pagination_info(employees, current_app.config.get('MAX_PAGINATION_LINKS', 5))
    
    return render_template('index.html',
                         employees=employees,
                         departments=departments,
                         search=search,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         pagination=pagination_info)

@employee_bp.route('/api/employees')
def api_employees():
    """API endpoint for employee data"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    sort_by = request.args.get('sort_by', 'name', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)
    per_page = request.args.get('per_page', 12, type=int)
    
    # Limit per_page to prevent abuse
    per_page = min(per_page, 100)
    
    # Search and paginate employees
    employees = Employee.search_employees(
        search_term=search,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Convert to dictionary format
    employee_data = [emp.to_dict() for emp in employees.items]
    
    # Calculate pagination info
    pagination_info = get_pagination_info(employees, current_app.config.get('MAX_PAGINATION_LINKS', 5))
    
    return jsonify({
        'employees': employee_data,
        'pagination': pagination_info,
        'total': employees.total,
        'pages': employees.pages,
        'current_page': employees.page,
        'per_page': employees.per_page,
        'has_next': employees.has_next,
        'has_prev': employees.has_prev
    })

@employee_bp.route('/api/employee/<int:employee_id>')
def api_employee_detail(employee_id):
    """API endpoint for single employee details"""
    employee = Employee.query.get_or_404(employee_id)
    return jsonify(employee.to_dict())

@employee_bp.route('/api/departments')
def api_departments():
    """API endpoint for departments"""
    departments = Employee.get_departments()
    return jsonify(departments)

@employee_bp.route('/api/statistics')
def api_statistics():
    """API endpoint for employee statistics"""
    stats = Employee.get_statistics()
    return jsonify(stats)

def get_pagination_info(pagination_obj, max_links=5):
    """Helper function to generate pagination information"""
    current_page = pagination_obj.page
    total_pages = pagination_obj.pages
    
    # Calculate the range of page numbers to display
    start_page = max(1, current_page - max_links // 2)
    end_page = min(total_pages, start_page + max_links - 1)
    
    # Adjust start_page if we're near the end
    if end_page - start_page + 1 < max_links:
        start_page = max(1, end_page - max_links + 1)
    
    return {
        'current_page': current_page,
        'total_pages': total_pages,
        'has_prev': pagination_obj.has_prev,  
        'has_next': pagination_obj.has_next,
        'prev_num': pagination_obj.prev_num,
        'next_num': pagination_obj.next_num,
        'start_page': start_page,
        'end_page': end_page,
        'pages': list(range(start_page, end_page + 1)),
        'total_items': pagination_obj.total,
        'per_page': pagination_obj.per_page
    }