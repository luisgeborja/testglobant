from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import F, Q, Count, Case, When, Value, FloatField, Avg
from api_globant.models import *

def quarters(request):
    """
    Retrieves the number of employees hired per quarter for each job and department in 2021.
    Returns JSON response.
    """
    employees_by_quarter = HiredEmployees.objects.filter(
        hiredate__year=2021,
        hiredate__isnull=False,
        department_id__isnull=False,
        job_id__isnull=False
    ).annotate(quarter=Case(
        When(hiredate__month__lte=3, then=Value('Q1')),
        When(hiredate__month__lte=6, then=Value('Q2')),
        When(hiredate__month__lte=9, then=Value('Q3')),
        default=Value('Q4'),
        output_field=models.CharField()
    )).values(
        department_name=F('department_id__department'),
        job_name=F('job_id__job'),
        quarter_name=F('quarter')
    ).annotate(total_employees=Count('id')).order_by('department_id__department', 'job_id__job', 'quarter')
    
    for employee_data in employees_by_quarter:
        print(employee_data)

    response = list(employees_by_quarter)
    return JsonResponse(response, safe=False, status=200)

def number_hires(request):
    """
    Retrieves the average count of employees hired by department in 2021 and the departments with above-average hiring.
    Returns JSON response.
    """
    average_employees = HiredEmployees.objects.filter(
        hiredate__year=2021
    ).values('department_id').annotate(
        employee_count=Count('id')
    ).aggregate(
        average=Avg('employee_count', output_field=FloatField())
    )['average']

    # Obtener los departamentos con más empleados que el promedio
    departments_above_average = HiredEmployees.objects.filter(
        hiredate__year=2021,
        hiredate__isnull=False,
        department_id__isnull=False,
        job_id__isnull=False
    ).values('department_id').annotate(
        employee_count=Count('id')
    ).filter(employee_count__gt=average_employees).order_by('-employee_count')

    # Listar IDs, nombres y número de empleados contratados por cada departamento
    result = departments_above_average.values(
        'department_id__id',
        'department_id__department'
    ).annotate(
        total_employees=Count('id')
    )

    for data in result:
        print(f"Department ID: {data['department_id__id']}, Department Name: {data['department_id__department']}, Number of Employees: {data['total_employees']}")

    # Lista para almacenar los datos
    data = [
        {
            'department_id': entry['department_id__id'],
            'department_name': entry['department_id__department'],
            'total_employees': entry['total_employees']
        }
        for entry in result
    ]
    
    """for entry in result:
        department_id = entry['department_id__id']
        department_name = entry['department_id__department']
        total_employees = entry['total_employees']
        data.append({
            'department_id': department_id,
            'department_name': department_name,
            'total_employees': total_employees
        })"""
    return JsonResponse(data, safe=False, status=200)
