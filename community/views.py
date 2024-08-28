from django.shortcuts import get_object_or_404, render, redirect

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import auth
from django.db.models import Q
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from datetime import datetime
import os
import random
import string

from authentications.models import CustomUser
from .models import CommunityPage, CommunityPost, AssignmentPost, StudentAssignment, PostLike, PostComment
from quiz.models import Exam, ExamSubmission

# Create your views here.

# Ana sayfa view
@login_required
def open_feed(request):

    newest_subscribed_communities = CommunityPage.objects.filter(subscribers=request.user.id).order_by('-created')[:3]

    community_count = newest_subscribed_communities.count()

    user = request.user
    
    user_communities = user.subscribed_communities.all()

    # Bu topluluklardaki normal ve ödev postları al
    normal_posts = CommunityPost.objects.filter(post_community__in=user_communities).exclude(post_type="Assignment")
    assignment_posts = AssignmentPost.objects.filter(post_community__in=user_communities)

    # Postları birleştir ve tarihe göre sıralandır
    all_posts = list(normal_posts) + list(assignment_posts)
    all_posts.sort(key=lambda x: x.post_created, reverse=True)

    veriler = {
        "newest_subscribed_communities" : newest_subscribed_communities,
        "community_count" : community_count,
        'posts': all_posts,
    }

    return render(request, 'feed.html' , veriler)

# Profil sayfası view
@login_required
def open_profile(request, username):

    # Profil sayfasına erişilmeye çalışılan kullanıcı ve mevcut kullanıcı sorgulanır.
    current_user = request.user
    profile_user = CustomUser.objects.get(username=username)

    room_name_degeri = None

    if current_user == profile_user:
        is_own_profile = True
    else:
        is_own_profile = False

        room_name_degeri = f"chatroom_{min(current_user.username, profile_user.username)}_{max(current_user.username, profile_user.username)}"

    # Ödev ve sınav kayıtlarının işlemi gerçekleştirilir.
    assignments = StudentAssignment.objects.none()
    exams = ExamSubmission.objects.none()

    if current_user.usertype == "Academic" :
        assignments = StudentAssignment.objects.filter(student=profile_user)
        exams = ExamSubmission.objects.filter(student=profile_user)

    content = {
        'profile_user': profile_user, 
        'is_own_profile': is_own_profile,
        'room_name_degeri' : room_name_degeri,
        'assignments' : assignments,
        'exams' : exams,
    }

    return render(request, 'profile-page2.html', content )

# Ayarlar sayfası view
@login_required
def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@login_required
def save_uploaded_file(uploaded_file):
    # Dosya adını rastgele oluştur
    image_filename , image_fileextention = os.path.splitext(uploaded_file.name)
    random_filename = image_filename + "_" +  random_string(10) + image_fileextention
    # Dosyayı kaydet
    file_path = os.path.join('images/', random_filename)
    with default_storage.open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return file_path

@login_required
def open_settings(request):
    
    if request.method == "POST" :

        if 'settings_form' in request.POST.keys():

            firstname = request.POST["firstname"]
            lastname = request.POST["lastname"]
            about = request.POST["about"]

            if 'profilephoto' in request.FILES.keys():

                profilephoto = request.FILES["profilephoto"]

                profile_photo_path = save_uploaded_file(profilephoto)
                # CustomUser modeline kaydedin
                custom_user = CustomUser.objects.get(pk=request.user.id)  # Varsayılan olarak mevcut kullanıcıyı alıyoruz
                custom_user.userprofilephoto = profile_photo_path
                custom_user.save()

            if 'backgroundphoto' in request.FILES.keys():

                backgroundphoto = request.FILES["backgroundphoto"]
                
                background_photo_path = save_uploaded_file(backgroundphoto)
                # CustomUser modeline kaydedin
                custom_user = CustomUser.objects.get(pk=request.user.id)  # Varsayılan olarak mevcut kullanıcıyı alıyoruz
                custom_user.userbackgroundphoto = background_photo_path
                custom_user.save()

            if ( firstname != "" ) and ( lastname != "" ) :
                custom_user = CustomUser.objects.get(pk=request.user.id)
                custom_user.first_name = firstname
                custom_user.last_name = lastname
                custom_user.userabout = about
                custom_user.save()

            return render(request, "settings.html", { "message" : "Update is successful" } )
        
        elif 'delete_form' in request.POST.keys() :

            password = request.POST["password"]

            custom_user = CustomUser.objects.get(pk=request.user.id)

            if custom_user.check_password(password) :

                # Bütün ödev cevapları silinir.
                StudentAssignment.objects.filter(student=custom_user).delete()
                
                # Bütün sınav cevapları silinir.
                ExamSubmission.objects.filter(student=custom_user).delete()

                # Yapılan bütün like ve yorumlar silinir.
                PostLike.objects.filter(user=custom_user).delete()
                PostComment.objects.filter(user=custom_user).delete()

                # Kullanıcının yapmış olduğu postlar silinir.
                CommunityPost.objects.filter(post_creator=custom_user).delete()

                # Kullanıcının oluşturduğu topluluklar ve ilgili tüm nesneler silinir.
                created_communities = CommunityPage.objects.filter(creator=custom_user)
                for community in created_communities:
                    # Toplulukla ilgili tüm postlar, ödevler ve sınavlar silinir.
                    CommunityPost.objects.filter(post_community=community).delete()
                    AssignmentPost.objects.filter(post_community=community).delete()
                    Exam.objects.filter(exam_community=community).delete()
                    
                    # Topluluğun kendisi silinir.
                    community.delete()
                
                # Kullanıcıya dair profil fotoğrafı ve background fotoğrafı otomatik olarak silinir.

                custom_user.delete()

                return redirect("featuredpages_frontpage_name")
            else :
                return render(request, "settings.html", { "delete_message" : "Password is incorrect" } )

    else:    
        return render(request, "settings.html")

# Gruplar sayfası view
@login_required
def open_groups(request):

    user_subscribed_communities = CommunityPage.objects.filter(subscribers__id=request.user.id)

    return render(request, "groups.html" , { 'user_subscribed_communities' : user_subscribed_communities} )

# Grup oluşturma sayfası view
@login_required
def create_group(request):

    custom_user_usertype = request.user.return_usertype() 

    if (custom_user_usertype != "Academic" ):
        return redirect("community_groups_name")
    else :   
        if request.method == "POST" :

            title = request.POST["title"]
            id_name = request.POST["id_name"]
            access_code = request.POST["access_code"]
            info = request.POST["info"]
            terms = request.POST["terms"]

            if CommunityPage.objects.filter(id_name = id_name).exists() :
                return render(request, "add-new-community.html" , { "error" : "Community's ID Name is Used" } )

            creator_id = request.user.id  # Oturum açmış kullanıcının ID'sini al

            # Yaratıcı kullanıcıyı al
            creator = CustomUser.objects.get(id=creator_id)

            new_community = CommunityPage.objects.create(community_title=title , id_name=id_name , community_access_code=access_code , 
                                                     info=info , terms=terms , creator=creator)
            
            new_community.admins.add(creator)
            new_community.subscribers.add(creator)

            new_community.save()

            return redirect("community_groups_name")


        return render(request, "add-new-community.html")
    
# Topluluklara erişim için kullanılan view fonksiyonu tanımlanır.

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    user = request.user
    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
    likes_list = [{'username': like.username} for like in post.likes.all()]
    return JsonResponse({'liked': liked, 'like_count': post.likes.count(), 'likes_list': likes_list})

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    content = request.POST.get('content')
    if content:
        comment = PostComment.objects.create(post=post, user=request.user, content=content)
        return JsonResponse({
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'created': comment.created.strftime('%Y-%m-%d %H:%M:%S'),
                'user': {
                    'username': comment.user.username,
                    'first_name': comment.user.first_name,
                    'last_name': comment.user.last_name,
                    'userprofilephoto': comment.user.userprofilephoto.url
                }
            }
        })
    return JsonResponse({'error': 'Content is required.'}, status=400)

@login_required
def open_community(request, slug) :

    sorgulanacak_community = get_object_or_404(CommunityPage, slug=slug)
    
    if request.user not in sorgulanacak_community.subscribers.all() :

        if request.method == "POST" :
            
            if "accesscode_form" in request.POST.keys():

                access_code = request.POST["access_code"]

                if access_code == sorgulanacak_community.community_access_code :
                    sorgulanacak_community.subscribers.add(request.user)
                    return redirect('community_opencommunity_name', slug=slug)
                else:
                    return render( request, "group-accesscode-detail.html", { "error" : "Access Code is incorrect" , "sorgulanacak_community" : sorgulanacak_community} )

        return render(request, "group-accesscode-detail.html", { "sorgulanacak_community" : sorgulanacak_community } )

    if request.method == "POST" :

        if 'new_post_form' in request.POST.keys():

            radio_post_type = "Normal"

            if 'post_type' in request.POST.keys():
                radio_post_type = request.POST['post_type'] 
            else:
                radio_post_type = "Normal"

            if radio_post_type == "Assignment" :    # Ödev ile ilgili post seçilmiştir.
                
                post_type = "Assignment"

                # Ödev postu için temel parametreler alınır.
                post_content = request.POST["post_content"] 
                community_id_name = request.POST["community_id_name"]

                post_creator = CustomUser.objects.get(pk=request.user.id)
                post_community = get_object_or_404(CommunityPage, id_name=community_id_name)

                assignment_header = request.POST["post_header"]
                assignment_slug = slugify(assignment_header)

                assignment_raw_duedate = request.POST["post_duedate"]

                assignment_duedate = datetime.strptime(assignment_raw_duedate, '%Y/%m/%d %H:%M')

                # Ödev postunda dosya olup olmayacağına göre iki farklı işlem yapılır.
                if 'homework_file' in request.FILES:    # Ödev postunda dosya var.
                    assignment_file = request.FILES['homework_file']

                    # Şimdi yeni ödev postu veri tabanına kaydedilir.
                    new_assignment_post = AssignmentPost.objects.create(post_creator = post_creator , post_content = post_content , post_community = post_community ,
                                                                        assignment_header = assignment_header , assignment_duedate = assignment_duedate , 
                                                                        assignment_file = assignment_file , post_type=post_type, slug=assignment_slug)
                                                            
                    new_assignment_post.save()

                    return redirect("community_opencommunity_name" , slug=post_community.slug)

                else:   # Ödev postunda dosya yok.
                    
                    # Şimdi yeni ödev postu veri tabanına kaydedilir.
                    new_assignment_post = AssignmentPost.objects.create(post_creator = post_creator , post_content = post_content , post_community = post_community ,
                                                                        assignment_header = assignment_header , assignment_duedate = assignment_duedate , post_type=post_type ,
                                                                        slug = assignment_slug)
                                                            
                    new_assignment_post.save()

                    return redirect("community_opencommunity_name" , slug=post_community.slug)

            elif radio_post_type == "Link" :      # Link içeren post seçilmiştir.
                
                post_type = "Link"

                post_content = request.POST["post_content"] 
                community_id_name = request.POST["community_id_name"]

                post_creator = CustomUser.objects.get(pk=request.user.id)
                post_community = get_object_or_404(CommunityPage, id_name=community_id_name)

                post_link = request.POST["post_link"]

                new_post = CommunityPost.objects.create(post_creator = post_creator , post_content = post_content , 
                                                        post_community = post_community , post_link = post_link , 
                                                        post_type = post_type)

                new_post.save()

                return redirect("community_opencommunity_name" , slug=post_community.slug)    

            else:                                   # Normal post seçilmiştir.

                post_type = "Normal"

                post_content = request.POST["post_content"] 
                community_id_name = request.POST["community_id_name"]

                post_creator = CustomUser.objects.get(pk=request.user.id)
                post_community = get_object_or_404(CommunityPage, id_name=community_id_name)

                new_post = CommunityPost.objects.create(post_creator = post_creator , post_content = post_content , post_community = post_community , 
                                                        post_type = post_type)

                new_post.save()

                return redirect("community_opencommunity_name" , slug=post_community.slug)    

    # Community bilgileri ile ilgili veriler çekilir.
    community_bilgileri = get_object_or_404(CommunityPage, slug=slug)
    members = community_bilgileri.subscribers.all()[:3]

    current_time = timezone.now()
    exams = Exam.objects.filter(exam_end_date__gte=current_time).order_by('exam_start_date')
    exam_count = exams.count()

    # Post verileri veri tabanından çekilir.
    normal_post_verileri = CommunityPost.objects.filter(post_community=community_bilgileri).exclude(post_type="Assignment").prefetch_related('post_comments')
    assignment_post_verileri = AssignmentPost.objects.filter(post_community=community_bilgileri).prefetch_related('post_comments')

    post_verileri = list(normal_post_verileri) + list(assignment_post_verileri)
    post_verileri.sort(key=lambda x: x.post_created, reverse=True)

    admin_permission = False 

    if community_bilgileri.admins.filter(id=request.user.id).exists():
        admin_permission = True

    content = {

        "community_bilgileri" : community_bilgileri ,
        "members" : members ,
        "post_verileri" : post_verileri,
        'exams' : exams ,
        'exam_count' : exam_count ,
        'admin_permission' : admin_permission , 

    }

    return render(request, "group-detail.html" , content)

# Ödev postlarının detaylarına bakıldığı sayfa

@login_required
def download_submission(request, submission_id):
    submission = get_object_or_404(StudentAssignment, id=submission_id)
    file_path = submission.submitted_file.path
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

@login_required
def download_assignment(request, assignment_id):
    assignment = get_object_or_404(AssignmentPost, id=assignment_id)
    file_path = assignment.assignment_file.path
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

@login_required
def open_postdetail(request, community_slug, slug):
    
    community = get_object_or_404(CommunityPage, slug=community_slug)

    # Veri tabanından post verisi çekilir.
    post = get_object_or_404(AssignmentPost, slug=slug)

    is_admin = False
    student_assignments = StudentAssignment.objects.none()
    student_assignments_count = 0
    
    # Kullanıcı admin ise
    if request.user.administered_communities.filter(id=community.id).exists():
        is_admin = True
        student_assignments = StudentAssignment.objects.filter(assignment=post)
        student_assignments_count = student_assignments.count()
    else:
        try:
            # Belirtilen öğrenciye ait ödevi veri tabanında arar ve bulursa atar
            student_assignments = get_object_or_404(StudentAssignment, student=request.user)
        except Http404:
            # Ödev bulunamazsa, hata yakalanır ve student_assignments None olarak kalır
            pass

    # Eğer form submit edilmişse
    if request.method == 'POST':
        # Dosya yükleme işlemi
        if 'submitted_file' in request.FILES.keys():
            submitted_file = request.FILES['submitted_file']
            submission = StudentAssignment.objects.create(
                assignment=post,
                student=request.user,
                submitted_file=submitted_file,
            )
            submission.save()
    
            return redirect('community_postdetail_name', community_slug=community_slug, slug=slug)

    current_time = timezone.now()

    time_passed = False
    if current_time > post.assignment_duedate :
        time_passed = True

    context = {
        'post': post,
        'is_admin' : is_admin,
        'student_assignments': student_assignments,
        'student_assignments_count' : student_assignments_count,
        'time_passed' : time_passed,
    }

    return render(request, 'post-detail.html', context)

# Arama sonuçlarının görüntülendiği sayfa

@login_required
def open_searchresults(request):

    search_content = request.GET.get('search_content', '').strip()  # Boşsa varsayılan olarak boş metin
    search_content_parts = search_content.split()

    user_results = CustomUser.objects.none()

    # User results aramaları yapılır.
    if len(search_content_parts) > 1:
        first_name = " ".join(search_content_parts[:-1])
        last_name = search_content_parts[-1]
        user_results = CustomUser.objects.filter(
            Q(first_name__iexact=first_name) &
            Q(last_name__iexact=last_name)
        )
    elif len(search_content_parts) == 1:
        user_results = CustomUser.objects.filter(
            Q(username__iexact=search_content) |
            Q(first_name__iexact=search_content) |
            Q(last_name__iexact=search_content)
        )

    # Community results aramaları yapılır.
    community_results = CommunityPage.objects.filter(
        Q(community_title__icontains=search_content) |  
        Q(id_name__icontains=search_content)
    )

    user_no_result = not user_results.exists()  # Boşsa True
    community_no_result = not community_results.exists()  # Boşsa True

    content = {

        "search_content" : search_content ,
        "user_results" : user_results ,
        "community_results" : community_results ,
        'user_no_result': user_no_result,
        'community_no_result': community_no_result,
    }

    return render(request, "search-result.html" , content)

@login_required
def open_allmembers(request, slug):

    # Topluluk belirlenir.
    community = get_object_or_404(CommunityPage, slug=slug)
    
    # Topluluğun adminlerini al
    admin_members = community.admins.all()
    
    # Topluluğun admin olmayan üyelerini al
    student_members = community.subscribers.exclude(id__in=admin_members.values_list('id', flat=True))

    # Template'e gönderilecek context verileri
    context = {
        'community': community,
        'admin_members': admin_members,
        'student_members': student_members
    }

    return render(request, 'all-members.html', context)

@login_required
def open_communitysettings(request, slug):

    # Topluluk belirlenir.
    community = get_object_or_404(CommunityPage, slug=slug)

    if request.user != community.creator:
        return redirect("community_opencommunity_name" , slug=community.slug )
    else: 
        all_subscribers = community.subscribers.all()

        selected_users = all_subscribers.filter(usertype="Academic").exclude(id__in=community.admins.all())

        if request.method == "POST" :

            if 'admin_form' in request.POST.keys():
                
                selected_member_username = request.POST["selected_member"]

                selected_member = get_object_or_404(CustomUser, username=selected_member_username)

                print("Selected Member Kişisi : " , selected_member.username)

                community.admins.add(selected_member)

                community.save()

                content = {
                    "admin_message" : "New admin added successfully" ,
                    "selected_members" : selected_users ,
                    "community" : community , 
                }

                return render(request, "community-settings.html", content)


            elif 'settings_form' in request.POST.keys():
        
                info = request.POST["info"]
                terms = request.POST["terms"]

                if 'profilephoto' in request.FILES.keys():

                    profilephoto = request.FILES["profilephoto"]
                
                    if profilephoto:
                        profile_photo_path = save_uploaded_file(profilephoto)
                    
                        community.profilephoto = profile_photo_path
                        community.save()

                if 'backgroundphoto' in request.FILES.keys():

                    backgroundphoto = request.FILES["backgroundphoto"]

                    if backgroundphoto:
                        background_photo_path = save_uploaded_file(backgroundphoto)
                
                        community.backgroundphoto = background_photo_path
                        community.save()

                community.info = info
                community.terms = terms

                community.save()

                content = {
                    "message" : "Update is succesful" ,
                    "selected_members" : selected_users ,
                    "community" : community , 
                }

                return render(request, "community-settings.html", content )
            
            elif 'delete_form' in request.POST.keys() :

                password = request.POST["password"]

                custom_user = CustomUser.objects.get(pk=request.user.id)

                if custom_user.check_password(password) :
                    
                    # Topluluktaki bütün ödevler ve içeriği silinir.
                    assignments = AssignmentPost.objects.filter(post_community=community)
                    for assignment in assignments:
                        StudentAssignment.objects.filter(assignment=assignment).delete()
                    assignments.delete()
                    
                    # Topluluktaki bütün postlar silinir.
                    CommunityPost.objects.filter(post_community=community).delete()

                    # Topluluktaki bütün sınavlar silinir.
                    Exam.objects.filter(exam_community=community).delete()

                    # Topluluk silinir. 
                    community.delete()

                    return redirect("community_feed_name")
                else :

                    content = {
                        "delete_message" : "Password is incorrect" ,
                        "selected_members" : selected_users ,
                        "community" : community , 
                    }
                    return render(request, "community-settings.html", content )

        else:

            content = {
                "selected_members" : selected_users ,
                "community" : community ,
            }

            return render(request, "community-settings.html", content )

@login_required
def deletepost(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    
    post_community = post.post_community

    # Postu sil
    post.delete()
    
    # Topluluk beslemesi gibi uygun bir sayfaya yönlendirme yapın
    return redirect('community_opencommunity_name' , slug=post_community.slug)


