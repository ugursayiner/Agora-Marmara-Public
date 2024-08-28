from django.shortcuts import render, redirect, get_object_or_404

from django.utils.dateparse import parse_datetime
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from authentications.models import CustomUser
from community.models import CommunityPage
from .models import Exam, ExamSubmission

# Create your views here.

@login_required
def exam_generator(request, community_slug):

    custom_user_usertype = request.user.return_usertype() 

    if (custom_user_usertype != "Academic" ):
        return redirect("community_groups_name")
    else: 
        
        community = get_object_or_404(CommunityPage, slug=community_slug)

        if request.method == "POST" :
            
            exam_title = request.POST["exam_title"]

            exam_start_date_raw = request.POST["exam_start_date"]
            exam_end_date_raw = request.POST["exam_end_date"]

            try:
                exam_start_date = datetime.strptime(exam_start_date_raw, '%Y-%m-%dT%H:%M')
                exam_end_date = datetime.strptime(exam_end_date_raw, '%Y-%m-%dT%H:%M')
            except ValueError:
                return render(request, 'add-new-exam.html', {'error': 'Invalid date/time format'})
        
            question1 = request.POST["question1"]
            question2 = request.POST["question2"]
            question3 = request.POST["question3"]
            question4 = request.POST["question4"]
            question5 = request.POST["question5"]

            exam_creator = request.user

            new_exam = Exam.objects.create(exam_title=exam_title , exam_creator = exam_creator , exam_community=community ,
                                           exam_start_date=exam_start_date , exam_end_date=exam_end_date , 
                                           question1=question1 , question2=question2 , question3=question3,
                                           question4=question4 , question5=question5 )
            
            new_exam.save()

            return redirect("community_opencommunity_name" , slug=community.slug)

        return render(request, "add-new-exam.html")

@login_required
def exam_solve(request, slug):
    
    solved_exam = get_object_or_404(Exam, slug=slug)

    current_time = timezone.now()

    if current_time < solved_exam.exam_start_date:

        # Sınav saatinden önce giriş yapılmaya çalışılıyor ise 

        content = {
            'error_start' : 'The exam has not started yet.' ,
            'solved_exam_start_date' : solved_exam.exam_start_date , 
            'solved_exam_title' : solved_exam.exam_title ,
        }

        return render(request, 'solve-exam.html', content)
    
    elif current_time > solved_exam.exam_end_date:

        # Sınav saatinden sonra giriş yapılmaya çalışılıyor ise

        content = {
            'error_end' : 'The exam has already ended.' ,
            'solved_exam_end_date' : solved_exam.exam_end_date ,
            'solved_exam_title' : solved_exam.exam_title ,
        }

        return render(request, 'solve-exam.html' , content)
    
    else:

        # Eğer öğrenci sınavı çözmüş ise
        mevcut_kayit = ExamSubmission.objects.filter(exam=solved_exam , student=request.user).exists()

        if mevcut_kayit:

            content = {
            'error_student' : 'You have already taken this exam.' ,
            'solved_exam_title' : solved_exam.exam_title ,
            }

            return render(request, "solve-exam.html" , content)
        
        else :
        
            if request.method == "POST" :

                answer1 = request.POST["answer1"]
                answer2 = request.POST["answer2"]
                answer3 = request.POST["answer3"]
                answer4 = request.POST["answer4"]
                answer5 = request.POST["answer5"]

                student = request.user

                # Default exam_score değeri 0'dır.

                new_submission = ExamSubmission.objects.create( exam = solved_exam , student = student , answer1=answer1 , answer2=answer2 , 
                                                                answer3=answer3 , answer4=answer4 , answer5=answer5 )
                
                new_submission.save()

                return redirect("community_opencommunity_name" , slug=solved_exam.exam_community.slug )


            content = {
                'solved_exam_title' : solved_exam.exam_title ,
                'solved_exam' : solved_exam ,
            }

            return render(request, "solve-exam.html" , content)

@login_required
def all_exam_results(request, community_slug, exam_slug):
    
    # Sınava dair veriler veri tabanından çekilir.
    solved_exam = get_object_or_404(Exam, slug=exam_slug)

    # Sınav sonuçlarına ait veriler veri tabanından çekilir.
    student_submissions = ExamSubmission.objects.filter(exam=solved_exam)

    content = {
        "solved_exam" : solved_exam ,
        "student_submissions" : student_submissions ,
    }

    return render(request, "all-exam-results.html", content )

@login_required
def exam_result(request, community_slug , exam_slug, student_username):

    # Sınav bilgileri elde edilir.     
    solved_exam = get_object_or_404(Exam, slug=exam_slug)

    # CustomUser'dan öğrenciye ulaşılır.
    student = get_object_or_404(CustomUser, username=student_username)

    # Öğrencinin sınavına ulaşılır.
    student_submission = get_object_or_404(ExamSubmission, exam=solved_exam , student=student)

    current_time = timezone.now()

    if current_time < solved_exam.exam_end_date:

        content = {
            'error_end' : 'The exam is still ongoing.' ,
            'solved_exam_end_date' : solved_exam.exam_end_date , 
            'solved_exam_title' : solved_exam.exam_title ,
        }

        return render(request, 'result-exam.html', content)
    
    else:

        if request.method == "POST":

            exam_score = request.POST["exam_score"]

            student_submission.exam_score = exam_score

            student_submission.save()

            return redirect( "quiz_examresult_name" , community_slug=community_slug , exam_slug=exam_slug , student_username=student_username)

        content = {
            'solved_exam' : solved_exam ,
            'student_submission' : student_submission ,
        }

        return render(request, 'result-exam.html' , content)

@login_required
def exam_list(request, community_slug):
    
    community = get_object_or_404(CommunityPage, slug=community_slug)

    current_time = timezone.now()

    # Şu anda aktif olan sınavlar listelenir.
    current_exams = Exam.objects.filter( exam_community=community, exam_start_date__lte=current_time, exam_end_date__gte=current_time )

    # Bitmiş sınavlar listelenir.
    passed_exams = Exam.objects.filter( exam_community=community, exam_end_date__lt=current_time ).order_by('-exam_end_date')

    # Gelecekteki sınavlar listelenir.
    future_exams = Exam.objects.filter( exam_community=community, exam_start_date__gt=current_time )

    content = {

        'current_exams': current_exams,
        'passed_exams': passed_exams,
        'future_exams': future_exams,
        'community' : community ,

    }

    return render(request, "exam-list.html" , content)

