from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.contrib.auth.models import User, auth
# from apps.accounts.models import User
# from apps.accounts.serializers import UserSerializer
from django.contrib import messages

# Create your views here.


# @csrf_exempt
# def userApi(request, id=0):
#     if request.method == 'GET':
#         users = User.objects.all()
#         users_serializer = UserSerializer(users, many=True)
#         return JsonResponse(users_serializer.data, safe=False)
#     elif request.method == 'POST':
#         user_data = JSONParser().parse(request)
#         users_serializer = UserSerializer(data=user_data)
#         if users_serializer.is_valid():
#             users_serializer.save()
#             return JsonResponse('Added Successfully', safe=False)
#         return JsonResponse('Failed to Add', safe=False)
#     elif request.method == 'PUT':
#         user_data = JSONParser().parse(request)
#         user = User.objects.get(UserId=user_data['UserId'])
#         user_serializer = UserSerializer(user, data=user_data)
#         if user_serializer.is_valid():
#             user_serializer.save()
#             return JsonResponse("Updated Successfully", safe=False)
#         return JsonResponse("Failed to Update")
#     elif request.method == 'DELETE':
#         user = User.objects.get(UserId=id)
#         user.delete()
#         return JsonResponse("Deleted Successfully", safe=False)

def register(request):
    if request.method == 'POST':
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        repeatPassword = request.POST["repeat-password"]

        if password == repeatPassword:
            # user zaten mevcut mu ?
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already on use.")
                # hata olursa tekrar register sayfasına yönlendiriyoruz.
                return redirect('register')

            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username already on use.")
                return redirect('register')
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                user.save()
                return redirect('login')
        else:
            messages.info(request, "The passwords not same.")
            return redirect('register')
    else:
        return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Kullanıcı bilgileri geçersiz')
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect('/')
