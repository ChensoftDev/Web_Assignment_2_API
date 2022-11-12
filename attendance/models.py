from django.db import models
from django.core.validators import MinValueValidator
from datetime import date

from django.http import JsonResponse
from django.urls import reverse


class Semester(models.Model):
    currentyear = int(date.today().year)
    year = models.IntegerField(validators=[MinValueValidator(currentyear)], default=currentyear)
    semester = models.CharField(max_length=2, null=False, blank=False)

    def __str__(self):
        return str(self.year) + " " + self.semester

    def get_absolute_url(self):
        return reverse('index')


class Course(models.Model):
    code = models.CharField(max_length=10, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.code + " " + self.name

    def get_absolute_url(self):
        return reverse('index')


class Lecturer(models.Model):
    firstname = models.CharField(max_length=100, null=False, blank=False)
    lastname = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=200)
    course = models.ManyToManyField(Course,null=True,blank=False)
    DOB = models.DateField(null=False, blank=False)

    def __str__(self):
        return self.firstname + " " + self.lastname

    def get_absolute_url(self):
        return reverse('index')


class Student(models.Model):
    firstname = models.CharField(max_length=100, null=False, blank=False)
    lastname = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=200)
    DOB = models.DateField(null=False, blank=False)

    def __str__(self):
        return self.firstname + " " + self.lastname

    def get_absolute_url(self):
        return reverse('index')


class Class(models.Model):
    number = models.CharField(max_length=10, null=False, blank=False, unique=True)
    semester = models.ForeignKey(Semester, null=False, blank=False, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, null=False, blank=False, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.number) + " " + self.course.name

    def get_absolute_url(self):
        return reverse('index')


class CollegeDay(models.Model):
    classID = models.ManyToManyField(Class, through='Attendance')
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.date.__str__()


class Enrollment(models.Model):
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE)
    classID = models.ForeignKey(Class, on_delete=models.CASCADE)

    def __str__(self):
        # return str(JsonResponse({"error": "Post not found", "status": 404}))
        # return str(JsonResponse({'class': self.classID,'student_id': self.studentID}))
        return str(self.classID) + " " + str(self.studentID)


class Attendance(models.Model):
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE)
    classID = models.ForeignKey(Class, on_delete=models.CASCADE)
    collegedayID = models.ForeignKey(CollegeDay, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.studentID.firstname) + " " + str(self.studentID.lastname)