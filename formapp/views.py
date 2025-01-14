from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.template.context_processors import csrf
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from formapp.models import Question
from csv import reader

import xlwt

# Create your views here.
def login(request):
    c = {}
    c.update(csrf(request))
    
    return render(request,'login.html', c)

def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username,password=password)
    if user is not None:        
        auth.login(request, user)
        return HttpResponseRedirect('/que')    
    else:
        print("username",username)
        print("password",password)        
        messages.add_message(request,messages.WARNING,'Invalid Login Details')
        return render(request,'login.html')

# @login_required(login_url='/login')
# def que1(request):
#     return render(request,'que1.html')

# @login_required(login_url='/login')
# def que2(request):
#     return render(request,'que2.html')

@login_required(login_url='/login')
def que(request):
    u = User.objects.get(username = request.user.username)
    try:
        que = Question.objects.get(user = u)
        if que is not None:
            messages.add_message(request,messages.SUCCESS,'You have already submited answer...')
            return render(request,'thanks.html')
        else:
            return render(request,'que.html')
    except:    
        return render(request,'que.html')

# def ans1(request):
#     u = User.objects.get(username = request.user.username)
    
#     que.Question1=request.POST['answer1']   
#     que.save()
#     return redirect('/que2')

# def ans2(request):
#     u = User.objects.get(username = request.user.username)
#     que=Question.objects.get(user=u)        
#     que.Question2=request.POST['answer2']
#     que.save()
#     return redirect('/que3')

def ans(request):
    u = User.objects.get(username = request.user.username)
    que=Question()
    que.user=u
    que.username = request.user.username
    que.name = request.user.first_name
    que.Question1=request.POST['answer1']
    que.Question2=request.POST['answer2']
    que.Question3=request.POST['answer3']
    que.Question4=request.POST['answer4']
    que.save()
    return redirect('/thanks')

def thanks(request):
    messages.add_message(request,messages.SUCCESS,'Your answer submited successfully...')
    return render(request,'thanks.html')

def logout_request(request):
    logout(request)
    return redirect('/login')

def export_xls(request):
    if((request.GET['uname'] == "sdm") and (request.GET['pass'] == "sdm123")):        
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="answer.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Answers')
        # Sheet header, first row
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Name','UserID', 'Answer1', 'Answer2', 'Answer3', 'Answer4', 'Time']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        # Sheet body, remaining rows

        font_style = xlwt.XFStyle()
        times = Question.objects.all().values_list('time',flat=True)
        # time = now.strftime('%H:%M:%S')
        rows = Question.objects.all().values_list('name','username', 'Question1', 'Question2', 'Question3','Question4')

        for (row,time) in zip(rows, times):
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
            ws.write(row_num, 6, time.strftime('%H:%M:%S'), font_style)            
        wb.save(response)
        return response

def bulk_add_users(request):
    if((request.GET['uname'] == "sdm") and (request.GET['pass'] == "sdm123")): 
        with open('day1.csv', mode='r') as csv_file:
            csv_reader = reader(csv_file)
            line_count = 0
            for line in csv_reader:
                if(line_count != 0):
                    # id = line[0]
                    name = line[0]
                    username = line[1]
                    password = line[2]
                    if not (username and
                            password):
                        raise ValueError(f'Invalid User data!')
                    user = User(username=username)
                    user.first_name = name
                    user.set_password(password)
                    user.save()
                line_count+=1