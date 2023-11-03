from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import F, Q, Count, Case, When, Value, FloatField, Avg
from api_globant.models import *

def quarters(request):
    """
    Retrieves the number of employees hired per quarter for each job and department in 2021.
    Returns JSON response.
    """
    # Fetch employees hired per quarter for each department and job in 2021
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

    response = list(employees_by_quarter)
    return JsonResponse(response, safe=False, status=200)

def number_hires(request):
    """
    Retrieves the average count of employees hired by department in 2021 and the departments with above-average hiring.
    Returns JSON response.
    """
    # Calculate the average count of employees hired by department in 2021
    average_employees = HiredEmployees.objects.filter(
        hiredate__year=2021
    ).values('department_id').annotate(
        employee_count=Count('id')
    ).aggregate(
        average=Avg('employee_count', output_field=FloatField())
    )['average']

    # Fetch departments with more employees hired than the average
    departments_above_average = HiredEmployees.objects.filter(
        hiredate__year=2021,
        hiredate__isnull=False,
        department_id__isnull=False,
        job_id__isnull=False
    ).values('department_id').annotate(
        employee_count=Count('id')
    ).filter(employee_count__gt=average_employees).order_by('-employee_count')

    # List IDs, names, and total employees hired for each department
    result = departments_above_average.values(
        'department_id__id',
        'department_id__department'
    ).annotate(
        total_employees=Count('id')
    )

    # Prepare the data into a list
    data = [
        {
            'department_id': entry['department_id__id'],
            'department_name': entry['department_id__department'],
            'total_employees': entry['total_employees']
        }
        for entry in result
    ]
    
    return JsonResponse(data, safe=False, status=200)
