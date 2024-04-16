import datetime
#from http import client
import urllib.request
import requests
from django.http import JsonResponse
import json
from django.contrib import auth
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import re
from openai import OpenAI
import openai

# Create your views here.

@login_required(login_url = "signin")

def IndexPage(request) :
    return render(request, "index.html")


def SignUpPage(request) :

    if request . method == "POST" :
        user_name = request . POST . get("username") # or user_name = request . POST["username"]
        user_email = request . POST . get("email") #or user_name = request . POST["email"]
        user_pwd1 = request . POST . get("password1")# or user_name = request . POST["password1"]
        user_pwd2 = request . POST . get("password2") # or user_name = request . POST["password2"]
        
        if  not user_name or not user_email or not user_pwd1 or not user_pwd2 :
           
           messages . error(request, "Please fill in all requred input fields")
           return redirect("signup")
        
        elif user_pwd1 != user_pwd2 :
             
             messages . error(request, "The two passwords did not match ")
             return redirect("signup")

        elif  User . objects . filter(username = user_name) :
            messages . error(request, "Sorry! The username already exists" . format(user_name))
            return redirect("signup")
        
        elif User . objects . filter(email = user_email) :
            messages . error(request, "The email address has already been taken.")
            return redirect("signup")

        
        elif len(user_name) > 20 :
            messages . error(request, "The username is too long.")
            return redirect("signup")
        
        elif len(user_pwd1) < 7 :
            messages . error(request, "Your password is too short. Must be 7 characters and above")
            return redirect("signup")
        
        elif not user_name .isalnum() :

            messages . error(request, "Username must only contain letters and numbers. Special characters are not allowed")
            return redirect("signup")

        else :
            #validate user email
            email_regex_pattern = "^[a-zA-Z0-9.]+@([a-z.]*\.[a-z]+)$"
            validate_email = user_email
            match = re.match(email_regex_pattern, validate_email)
            if not match :
                 messages.error(request, "Invalid email address format")
                 return redirect("signup")
                
            #create the user
            user = User.objects.create_user(user_name, user_email, user_pwd1)
            user . save()
            messages.success(request, "Account created successfully!")
            return redirect("signin")
        
    #landpage to registration page
    return render(request, "register.html")


def SignInPage(request) :

    if request . method == "POST" :
        login_name = request . POST . get("username")
        login_pwd = request . POST . get("password")
        user = authenticate(request, username  = login_name, password = login_pwd )
        if user is not None :
           
            login(request, user)
            return(redirect("index"))

        elif not login_name or not login_pwd :
            messages . error(request, "Please fill in all requred input fields")
            return redirect("signin")
           
        else :
            
          messages . error(request, "Incorrect username or password ")
          return redirect("signin")

    return render(request, "login.html")

# function for requesting weather data
def WeatherData(request):
    if request.method == "POST":
        city = request.POST.get("city")
        if not city:
            messages.error(request, "Please enter a city, town or local area name")
            return redirect("index")
        else:
            source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' + city + '&units=metric&appid=9652f47dc947aeebbed77aa2b15306ea').read()
            list_of_data = json.loads(source)
            city = city
            data = {
                "country_code" : str(list_of_data['sys']['country']),
                "coordinate" : str(list_of_data['coord']['lon']) + ', ' + str(list_of_data['coord']['lat']),
                "temp" : str(list_of_data['main']['temp']) + ' °C',
                "pressure" : str(list_of_data['main']['pressure']),
                "humidity" : str(list_of_data['main']['humidity']),
                "main" : str(list_of_data['weather'][0]['main']),
                "description" : str(list_of_data['weather'][0]['description']),
                "icon" : list_of_data['weather'][0]['icon'],
                "city_name": city,
                 "day": datetime.datetime.fromtimestamp(list_of_data['dt']).strftime("%A"),

            }
            
    else:
        data = {}

    return render(request, "index.html", {'data':data}) 


open_api_key = "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"
client = OpenAI(api_key= open_api_key)
openai.api_key = open_api_key
def askOpenAi(message):
    response = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [
        {"role": "system", "content": "You are an helpful assistant."},
        {"role": "user", "content": message},
    ]
    )
    print(response)
    answer = response.choices[0].message.content.strip()
    return answer
    # print(response.choices[0].message.content)

def chatBot(request):
    if request.method == "POST":
        message = request.POST.get('message')
        response = askOpenAi(message)
        return JsonResponse({'response': response})
        

    return render(request, "index.html")

def Logout(request) :
    logout(request)
    return redirect("signin")
