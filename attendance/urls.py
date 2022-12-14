from django.urls import path
from rest_framework.routers import DefaultRouter

from attendance.views import SemesterViewset, CourseViewset, LecturerViewset, StudentViewset, ClassViewset, \
    CollegeDayViewset, EnrollmentViewset, AttendanceViewset, attendance_detail, uploadStudentListFromFile, sendEmail

router = DefaultRouter()




router.register('semester',SemesterViewset,'semester_model_viewset')
router.register('course',CourseViewset,'course_model_viewset')
router.register('lecturer',LecturerViewset,'lecturer_model_viewset')
router.register('student',StudentViewset,'student_model_viewset')
router.register('class',ClassViewset,'class_model_viewset')
router.register('collegeday',CollegeDayViewset,'collegeday_model_viewset')
router.register('enrollment',EnrollmentViewset,'enrollment_model_viewset')
router.register('attendance',AttendanceViewset,'attendance_model_viewset')

urlpatterns = router.urls


urlpatterns.append(path('attendance_details/', attendance_detail))
urlpatterns.append(path('upload/', uploadStudentListFromFile))
urlpatterns.append(path('sendemail/', sendEmail))
