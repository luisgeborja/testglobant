from django.db import models

class Departments(models.Model):
    department = models.CharField(max_length=30)

class Jobs(models.Model):
    job = models.CharField(max_length=40)

class HiredEmployees(models.Model):
    name = models.CharField("Person's name", max_length=50)
    hiredate = models.DateField(null=True)
    department_id = models.ForeignKey(Departments, on_delete=models.CASCADE, blank=True, null=True)
    job_id = models.ForeignKey(Jobs, on_delete=models.CASCADE, blank=True, null=True)
    def get_iso_date(self):
        return self.hiredate.isoformat() if self.hiredate else None