from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

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


class StudentViewset(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]

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
