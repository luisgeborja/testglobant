import os
import django
import pandas as pd
from django.utils.dateparse import parse_datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testglobant.settings')
django.setup()
from api_globant.models import Departments, Jobs, HiredEmployees

# File names and their column specifications
files_to_load = ['departments.csv', 'jobs.csv', 'hired_employees.csv']
max_row = 1000

for file in files_to_load:
    if file == 'departments.csv':
        cols = ["department"]
        type_cols = {"department": str}
    elif file == 'jobs.csv':
        cols = ["job"]
        type_cols = {"job": str}
    else:
        cols = ["name", "hiredate", "department_id", "job_id"]
        type_cols = {"name": str, "hiredate": str, "department_id": float, "job_id": float}

    # Read CSV file into DataFrame
    df_file = pd.read_csv(f'api_globant/data_files/{file}', sep=',', header=None, index_col=0, names=cols, dtype=type_cols)
    df_file.reset_index(drop=True, inplace=True)
    
    if file == 'hired_employees.csv':
        # Convert department_id and job_id to Int64 type
        df_file["job_id"] = pd.to_numeric(df_file["job_id"], errors='coerce').fillna(pd.NA).astype(pd.Int64Dtype())
        df_file["department_id"] = pd.to_numeric(df_file["department_id"], errors='coerce').fillna(pd.NA).astype(pd.Int64Dtype())

    nrows = df_file.shape[0]
    for i in range(0, nrows, max_row):
        df_part = df_file.iloc[i:i + max_row].copy()
        for index, row in df_part.iterrows():
            if file == 'departments.csv':
                # Create Departments instances
                department = Departments.objects.create(department=row["department"])
            elif file == 'jobs.csv':
                # Create Jobs instances
                job = Jobs.objects.create(job=row["job"])
            else:
                # Create HiredEmployees instances and link with Departments and Jobs
                # Assume 'hiredate' column contains date and time in ISO format
                # Convert to string
                hiredate_iso = str(row["hiredate"])
                
                # Retrieve Department and Job instances based on provided IDs
                department_id = None
                if pd.notnull(row["department_id"]):
                    department_id = Departments.objects.filter(id=row["department_id"]).first()
                
                job_id = None
                if pd.notnull(row["job_id"]):
                    job_id = Jobs.objects.filter(id=row["job_id"]).first()
                
                # Create HiredEmployees instance
                hired_employee = HiredEmployees.objects.create(
                    name=row["name"],
                    hiredate=parse_datetime(hiredate_iso),
                    department_id=department_id,
                    job_id=job_id
                )
