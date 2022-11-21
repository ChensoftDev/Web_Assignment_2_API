from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from attendance.models import Semester, Course, Lecturer, Student, Class, CollegeDay, Enrollment, Attendance


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class LecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = ['id', 'firstname', 'lastname', 'email', 'course', 'DOB']

    def create(self, validated_data):
        lecturer = Lecturer.objects.create(**validated_data)
        first_name = self.validated_data.get("firstname")
        last_name = self.validated_data.get("lastname")
        email = self.validated_data.get("email")

        try:
            user = User.objects.create_user(username=first_name.lower())
            user.set_password(first_name.lower())
            user.first_name = first_name
            user.last_name = last_name
            user.email = email

            lecturer_group = Group.objects.get(name='lecturer')
            user.groups.add(lecturer_group)

            lecturer.user = user
            lecturer.save()
            Token.objects.create(user=user)
            user.save()
        except Exception as e:
            print(e)

        return lecturer


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'firstname', 'lastname', 'email', 'DOB']

    def create(self, validated_data):
        student = Student.objects.create(**validated_data)
        first_name = self.validated_data.get("firstname")
        last_name = self.validated_data.get("lastname")
        email = self.validated_data.get("email")

        try:
            user = User.objects.create_user(username=first_name.lower())
            user.set_password(first_name.lower())
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            student_group = Group.objects.get(name='student')
            user.groups.add(student_group)

            Token.objects.create(user=user)
            student.user = user
            student.save()
            user.save()
        except Exception as e:
            print(e)

        return student



class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"


class CollegeDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeDay
        fields = "__all__"

    def create(self, validated_data):
        date = validated_data.get('date', None)
        if date is not None:
            result, created = CollegeDay.objects.get_or_create(date=date)
        return result


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = "__all__"


class AttendanceSerializerWithValue(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "class": obj.classID.number,
            "date": obj.collegedayID.date,
            "status": obj.status,
        }


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"

    def create(self, validated_data):
        classid = validated_data.get('classID', int)
        dayid = validated_data.get('collegedayID', int)
        studentid = validated_data.get('studentID', int)
        status = validated_data.get('status', bool)
        if studentid is not None:
            result, created = Attendance.objects.update_or_create(classID=classid, collegedayID=dayid,
                                                                  studentID=studentid,
                                                                  defaults={'status': status})
        return result
