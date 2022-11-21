import pandas as pd
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.utils import json

from attendance.models import Semester, Course, Lecturer, Student, Class, CollegeDay, Enrollment, Attendance
from attendance.serializers import SemesterSerializer, CourseSerializer, LecturerSerializer, StudentSerializer, \
    ClassSerializer, CollegeDaySerializer, EnrollmentSerializer, AttendanceSerializer, AttendanceSerializerWithValue


class SemesterViewset(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]


class CourseViewset(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]


class LecturerViewset(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        lecturer = self.get_object()
        username = lecturer.firstname.lower()
        user = User.objects.get(username=username)
        lecturer.delete()
        user.delete()
        return Response(data='Deleted Successfully!')


class StudentViewset(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        username = student.firstname.lower()
        user = User.objects.get(username=username)
        student.delete()
        user.delete()
        return Response(data='Deleted Successfully!')


class ClassViewset(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]


class CollegeDayViewset(viewsets.ModelViewSet):
    queryset = CollegeDay.objects.all()
    serializer_class = CollegeDaySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]


class EnrollmentViewset(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def attendance_detail(request):
    try:
        if request.method == 'GET' and 'studentid' in request.GET:
            att = Attendance.objects.filter(studentID_id=request.GET["studentid"])
            serializer = AttendanceSerializerWithValue(att, many=True)
            return Response(serializer.data)
        elif request.method == 'GET' and 'collagedayid' in request.GET:
            att = Attendance.objects.filter(collegedayID_id=request.GET["collagedayid"])
            serializer = AttendanceSerializer(att, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    except Attendance.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


class AttendanceViewset(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        myid = user.id

        if user.groups.all()[0].name == "lecturer":
            lecturer = Lecturer.objects.get(firstname=user.first_name)
            myid = lecturer.id
        elif user.groups.all()[0].name == "student":
            student = Student.objects.get(firstname=user.first_name)
            myid = student.id

        return Response({
            'token': token.key,
            'group': user.groups.all()[0].name,
            'myid': myid,
        })


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def uploadStudentListFromFile(request):
    try:
        if request.method == 'POST' and request.FILES["myfile"]:
            myfile = request.FILES["myfile"]
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            upload_file_url = fs.url(filename)
            excel_data = pd.read_excel(myfile)
            data = pd.DataFrame(excel_data)
            usernames = data["Username"].tolist()
            firstnames = data["First Name"].tolist()
            lastnames = data["Last Name"].tolist()
            emails = data["Email"].tolist()
            dobs = data["DOB"].tolist()

            i = 0
            while i < len(usernames):
                username = usernames[i]
                firstname = firstnames[i]
                lastname = lastnames[i]
                email = emails[i]
                dob = dobs[i]
                # password = str(dobs[i]).split(" ")[0].replace("-", "")
                user = User.objects.create_user(username=username)
                user.first_name = firstname
                user.last_name = lastname
                user.email = email
                user.set_password(firstname.lower())

                user.save()
                student = Student(id=user.id)
                student.firstname = user.first_name
                student.lastname = user.last_name
                student.email = user.email
                student.DOB = dob
                student.save()
                i = i + 1

            return Response({
                'status': 'ok',
            })

        return Response({
            'status': 'wrong_method',
        })
    except Exception as e:
        print(e)
        return Response({
            'status': 'error',
        })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def sendEmail(request):
    data = json.loads(request.body)
    id = data["studentID"]
    studentEnrollment = Enrollment.objects.get(studentID_id=id)
    att = Attendance.objects.filter(studentID_id=id)

    totalclass = att.count()
    attended = att.filter(status=1).count()

    percent = (totalclass * 100) / attended
    percent_float = "{:.2f}".format(percent)

    emailAddress = studentEnrollment.studentID.email
    emailSubject = "You have been informed about your attendance"
    emailBody = "<b>Student ID :</b> #" + str(studentEnrollment.studentID.id) + \
                "<b>Name :</b> #" + studentEnrollment.studentID.firstname + " " + studentEnrollment.studentID.lastname + "\n\n" + \
                "Kia ora (greeting) <b>" + studentEnrollment.studentID.firstname + "</b>\n" + \
                "Please note that your Attendance is currently - <b>" + percent_float + "%</b>\n\n" + \
                "If you attendance is below 80%, it will affect to your study outcome.\n" + \
                "If you have any concern please do not be hesitate  to contact student support as soon as " \
                "possible\n\n\n" + \
                "<b>Best Regards<b>"

    senderEmail = 'gabriel_sl19798@hotmail.com'
    try:
        send_mail(emailSubject, emailBody, senderEmail, [emailAddress], fail_silently=False)
    except:
        return JsonResponse({"send_status": "ERROR" + str(id)})
    return JsonResponse({"send_status": "OK"})
