from django.contrib import admin

# Register your models here.
from attendance.models import Semester, Course, Lecturer, Class, Student, Enrollment, Attendance

admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(Lecturer)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Enrollment)
admin.site.register(Attendance)