from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required

from .models import CustomUser

# Create your views here.

# Login view
def open_signin(request):
    if request.user.is_authenticated:
        return redirect("community_feed_name")

    if request.method == 'POST' :
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username = username , password = password )

        if user is not None :

            login(request, user)
            
            return redirect("community_feed_name")
        else :
            return render(request, "sign-in.html", { "error" : "Username or Password is Incorrect" })

    else :
        return render(request, "sign-in.html")

# Register view
def open_signup(request):
    if request.user.is_authenticated :
        return redirect("community_feed_name")

    if request.method == 'POST' :
        username = request.POST["username"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        usertype = request.POST["usertype"]
        email = request.POST["email"]
        password = request.POST["password"]
        repassword = request.POST["repassword"]

        if password != repassword:
            return render(request, 'signup-2.html' , { "error" : "Passwords Do Not Match" } )
        
        if CustomUser.objects.filter(username = username).exists() :
            return render(request, 'signup-2.html' , { "error" : "Username is Used" } )

        if CustomUser.objects.filter(email = email).exists() :
            return render(request, 'signup-2.html' , { "error" : "E-Mail is Used" } )
                
        user = CustomUser.objects.create_user( username = username , email = email , first_name = firstname , last_name = lastname , 
                                               usertype = usertype , password = password)
        
        user.save()

        return redirect("authentications_signin_name")
        
    else :
        return render(request, 'signup-2.html')

# Logout view
@login_required
def user_logout(request):
    logout(request)

    return redirect("authentications_signin_name")