from django.urls import path

from . import views

"""
    exam-generator : Sınav ekleme sayfası ( Hoca  görür )
    exam-solve : Sınav çözme Sayfası ( Öğrenci görür )
    exam-result : Sınav sonuç sayfası ( Hem Hoca hem Öğrenci görür )
    exam-list : Sınavların listelendiği sayfa ( Hem Hoca hem Öğrenci görür )

"""

urlpatterns = [

    path("exam-generator/<slug:community_slug>/" , views.exam_generator , name="quiz_examgenerator_name" ),   
    path("exam-solve/<slug:slug>/" , views.exam_solve , name="quiz_examsolve_name" ),   
    path("all-exam-results/<slug:community_slug>/<slug:exam_slug>/" , views.all_exam_results , name="quiz_allexamresults_name"),            
    path("exam-result/<slug:community_slug>/<slug:exam_slug>/<str:student_username>/" , views.exam_result , name="quiz_examresult_name" ),            
    path("exam-list/<slug:community_slug>/" , views.exam_list , name="quiz_examlist_name"),                   

]