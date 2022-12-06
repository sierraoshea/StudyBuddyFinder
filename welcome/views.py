from django.views import generic
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import redirect
from .forms import EditProfileForm
from .models import UserClasses, Class, UserToUserChat, Time, Day, meeting, Bio, Message
import json
import ast
import requests
from itertools import groupby
from django.core.exceptions import ValidationError
from .models import Friend_Request
from .models import Class
from .models import FriendList
from django.db.models import Q
from datetime import datetime


import string
import random


def index(request):
    if request.user.is_authenticated:
        meetings = meeting.objects.filter(participants=request.user, date__gte = datetime.today()).order_by('date')
        meetings_old = meeting.objects.filter(date__lt = datetime.today())

        for old_meeting in meetings_old:
            old_meeting.delete()

        sent_requests = []
        for thisRequest in request.user.from_user.all():
            sent_requests.append(thisRequest.to_user)

        received_requests = []
        user_to_id = {}
        for thisRequest in request.user.to_user.all():
            received_requests.append(thisRequest.from_user)
            user_to_id[thisRequest.from_user.id] = thisRequest.id

        print(user_to_id)

        if not request.user.day_set.all():
            days = ['M','T','W','Th','F','Sa','Su']
            for day in days:
                thisday = Day.objects.create(user= request.user, day = day)
                for j in range(10, 23):
                    Time.objects.create(day = thisday, time = str(j)+":00")
        active =[]
        if request.user.classes.all():
            active.append( request.user.classes.all()[0])

        
        return render(request, 'welcome/index.html', {'meetings': meetings, 'sent_requests' : sent_requests, 'received_requests': received_requests, 'active':active, 'user_to_id': user_to_id })

    return render(request, 'welcome/index.html')


class EditView(generic.UpdateView):
    form_class = EditProfileForm
    template_name = 'welcome/profile.html'
    success_url = reverse_lazy('index')

    def get_object(self):
        return self.request.user


def edit_classes(request):
    template_name = 'welcome/edit_classes.html'

    # Basic idea for displaying JSON into a view. Parse the JSON in here (or in another file/function?) 
    # and pass it as a list of lists (or other) in the render.

    dept_list = requests.get('http://luthers-list.herokuapp.com/api/deptlist/?format=json').json()
    return render(request, template_name, {'dept_list': dept_list})


def delete_class(request):
    template_name = 'welcome/edit_classes.html'
    try:
        selected_classes = request.POST.getlist('class_to_delete')
        class_ids = []
        for c in selected_classes:
            class_ids.append(request.user.userclasses_set.get(pk=c))
    except(KeyError):
        return HttpResponseRedirect(reverse('classes'))
    else:
        for id in class_ids:
            try:
                thisclass = Class.objects.get(Name=id.subject + str(id.catalog_number))
                thisclass.students.remove(request.user)
            except(KeyError):
                pass
            id.delete()

        return HttpResponseRedirect(reverse('classes'))


def add_classes(request):
    try:
        selected_classes = request.POST.getlist('class_to_add')
    except(KeyError):
        return HttpResponseRedirect(reverse('classes'))
    
    else:
        add = True
        for class_to_add in selected_classes:
            c = class_to_add.split("/")
            UserClasses.objects.create(user=request.user,subject=c[0], catalog_number=c[1], component=c[2], section=c[3], professor=c[4], description=c[5])
        return HttpResponseRedirect(reverse('classes'))


def subject_view(request, subject):
    classes = requests.get('http://luthers-list.herokuapp.com/api/dept/' + subject + '/?format=json').json()
    
    current_classes = UserClasses.objects.filter(user=request.user)

    result = {
            key : list(group) for key, group in groupby(classes,key=lambda x:x['subject'] + " " + x['catalog_number'] + " " + x['description'])
           } 

    return render(request, 'welcome/subject.html', {'classes': result, 'current_classes': current_classes, "sub": subject})


def search_classes(request):
    searchPhrase = request.POST['searchbox']
    foundClasses = []
    response = requests.get('http://luthers-list.herokuapp.com/api/dept/CS/?format=json').json()
    for thisClass in response:
        if searchPhrase in thisClass["description"]:
            foundClasses.append(thisClass)
    return render(request, 'welcome/home.html', {'response': foundClasses})


def view_other_user(request, user_id):
    if user_id == request.user.id:
        return view_myprofile(request)
    
    student = get_object_or_404(User, pk=user_id)

    requests = []
    for thisRequest in request.user.from_user.all():
        requests.append(thisRequest.to_user)

    return render(request, 'welcome/other_profile.html', {'student' : student, 'sent_requests': requests} )


def update(request):
    try:
        selected_classes = request.POST.getlist('class_to_update')
        class_ids = []
        for c in selected_classes:
            class_ids.append(request.user.userclasses_set.get(pk=c))
    except(KeyError):
        return HttpResponseRedirect(reverse('index'))

    else:
        toAdd = []
        for c in request.user.userclasses_set.all():

            if c in class_ids:
                c.available = True
                c.save()
                try:
                    thisclass = Class.objects.get(Name=c.subject + str(c.catalog_number))
                except:
                    thisclass = Class.objects.create(Name=c.subject + str(c.catalog_number))

                toAdd.append(thisclass)

            else:
                c.available = False
                c.save()
                try:
                    thisclass = Class.objects.get(Name=c.subject + str(+c.catalog_number))
                    thisclass.students.remove(request.user)
                except:
                    pass
        for each in toAdd:
            each.students.add(request.user)

        return HttpResponseRedirect(reverse('index'))


def send_friend_request(request, userID):
    from_user = request.user
    to_user = User.objects.get(id=userID)
    Friend_Request.objects.get_or_create(from_user=from_user, to_user=to_user)
    return HttpResponseRedirect(reverse('index'))


def accept_friend_request(request, requestID):
    friend_request = Friend_Request.objects.get(id=requestID)
    current_list = FriendList.objects.select_related().filter(user=request.user.id)
    if not current_list.exists():
        friend_list = FriendList()
        friend_list.user = friend_request.to_user
        friend_list.save()
        friend_list.friends.add(friend_request.from_user)
        friend_list.save()
        add_friend_back(friend_request.from_user, friend_request.to_user)
        # trying to add user back on both lists
        # friend_list.from_user
        if request.method == "POST":
            friend_request.delete()
        return HttpResponseRedirect(reverse('friends'))
    for i in current_list:
        i.friends.add(friend_request.from_user)
        add_friend_back(friend_request.from_user, friend_request.to_user)
        if request.method == "POST":
            friend_request.delete()
            return HttpResponseRedirect(reverse('friends'))


def add_friend_back(to_user, from_user):

    room_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    private_chat = UserToUserChat(user1=to_user, user2=from_user, roomName=room_name)
    private_chat.save()

    current_list = FriendList.objects.select_related().filter(user=to_user)
    if not current_list.exists():
        friend_list = FriendList()
        friend_list.user = to_user
        friend_list.save()
        friend_list.friends.add(from_user)
        friend_list.save()
        return HttpResponseRedirect(reverse('friends'))
    for i in current_list:
        i.friends.add(from_user)
        return HttpResponseRedirect(reverse('friends'))


def decline_friend_request(request, requestID):
    friend_request = Friend_Request.objects.get(id=requestID)
    if request.method == "POST":
        friend_request.delete()
        return HttpResponseRedirect(reverse('friends'))
    return HttpResponseRedirect(reverse('friends'))


def remove_friend(request, userID):
    if request.method == "POST":
        from_user = request.user.id
        to_user = User.objects.get(id=userID)
        to_user_friendlist = FriendList.objects.select_related().filter(user=to_user)
        if to_user_friendlist.exists():
            for i in to_user_friendlist:
                i.friends.remove(from_user)
                return HttpResponseRedirect(request, 'welcome/friends.html', {'friend_list_to_user': i.friends})
        from_user_friendlist = FriendList.objects.select_related().filter(user=from_user)
        if from_user_friendlist.exists():
            for j in from_user_friendlist:
                j.friends.remove(to_user)
                return HttpResponseRedirect(request, 'welcome/friends.html', {'friend_list_this_user': j.friends})
        room = UserToUserChat.objects.filter(user1=request.user) | UserToUserChat.objects.filter(user2=from_user)
        if room.exists():
            room.delete
    return HttpResponseRedirect(reverse('friends'))


def study_partners(request):
    if request.user.UserClasses.available == True:
        same_classes_available = UserClasses.objects.filter(search_classes=request.user.UserClasses.search_class, available=True).exclude(id=request.user.id)
        return render(request, 'welcome/index.html', {'user': request.user, 'other_users': same_classes_available})
    else:
        return render(request, 'welcome/index.html')


def friends(request):
    current_list = FriendList.objects.select_related().filter(user=request.user.id)
    try:
        friend_list = current_list.first().friends
    except(AttributeError):
        friend_list = []

    try:
        friend_request = Friend_Request.objects.filter(to_user=request.user.id)
    except(AttributeError):
        friend_request = []
    return render(request, 'welcome/friends.html', {'friends': friend_request, 'friend_list': friend_list})


def room(request, room_name):
    
    rooms = UserToUserChat.objects.filter(user1=request.user) | UserToUserChat.objects.filter(user2=request.user)

    if room_name=='default':
        return render(request, 'welcome/room2.html', {'room_name': room_name, 'rooms': rooms})

    if not UserToUserChat.objects.filter(roomName=room_name):
        return HttpResponseRedirect(reverse('room', kwargs={'room_name': 'default'})) #doesn't exist
    
    room = UserToUserChat.objects.get(roomName=room_name)
    messages = Message.objects.filter(room=room).order_by('-date_added')[:20:-1]
    if(request.user != room.user1 and request.user != room.user2):
        return HttpResponseRedirect(reverse('room', kwargs={'room_name': 'default'})) #not allowed
    
    return render(request, 'welcome/room2.html', {'room_name': room_name, 'messages': messages, 'rooms': rooms})
  
def updateTimes(request):
    try:
        ids = request.POST.getlist('available_times')
    except(KeyError):
        return HttpResponseRedirect(reverse('myprofile'))

    for day in request.user.day_set.all():
        for time in day.time_set.all():
            if day.day+time.time in ids:
                if time.available is not True:
                    time.available = True
                    time.save()
            else:
                if time.available is not False:
                    time.available = False
                    time.save()
    return HttpResponseRedirect(reverse('myprofile'))

def view_myprofile(request):
    thisbio, _ =Bio.objects.get_or_create(student=request.user)
    user = request.user
    return render(request, 'welcome/myprofile.html', {'student':user, 'contents':thisbio.content})

def save_bio(request):
    newcontent = request.POST.get('bio')
    if newcontent is None:
        newcontent = ""
    request.user.bio.content = newcontent 
    request.user.bio.save()
    return HttpResponseRedirect(reverse('myprofile'))

def new_meeting(request, reciever_id):
    reciever = User.objects.get(pk=reciever_id)
    return render(request, "welcome/newmeeting.html", {'reciever' : reciever, 'errmsg':''})

def confirm_meeting(request, reciever_id):
    reciever = User.objects.get(pk=reciever_id)
    title = request.POST.get('title')
    date = request.POST.get('date')
    time = request.POST.get('time')

    date_as_date = datetime.strptime(date + " " + time + ":00", "%Y-%m-%d %H:%M:%S")

    if(date_as_date < datetime.today()):
        return render(request, "welcome/newmeeting.html", {'reciever' : reciever, 'errmsg':'Please enter a valid date and time.'})
    
    try:
        newmeeting = meeting.objects.create(title=title, date=date, time=time)
    except(ValidationError):
        return render(request, "welcome/newmeeting.html", {'reciever' : reciever, 'errmsg':'Please fill out all fields.'})
    
    newmeeting.participants.add(request.user, reciever)
    newmeeting.save()

    return HttpResponseRedirect(reverse('index'))

def edit_meeting(request, meeting_id):
    m = meeting.objects.get(id=meeting_id)
    reciever = m.participants.all().get(~Q(id=request.user.id))

    return render(request, "welcome/edit_meeting.html", {'meeting' : m, 'reciever':reciever, 'errmsg':''})

def update_meeting(request, meeting_id):
    meet = meeting.objects.get(id=meeting_id)
    reciever = meet.participants.all().get(~Q(id=request.user.id))
    title = request.POST.get('title')
    date = request.POST.get('date')
    time = request.POST.get('time')

    if(time[-3:] == ".00"):
        time = time[:-6]

    date_as_date = datetime.strptime(date + " " + time + ":00", "%Y-%m-%d %H:%M:%S")

    if(date_as_date < datetime.today()):
        return render(request, "welcome/edit_meeting.html", {'meeting' : meet, 'reciever' : reciever, 'errmsg':'Please enter a valid date and time.'})
    
    try:
        meet.title = title
        meet.date = date
        meet.time = time
    except(ValidationError):
        return render(request, "welcome/edit_meeting.html", {'meeting' : meet, 'reciever' : reciever, 'errmsg':'Please fill out all fields.'})
    
    meet.save()

    return HttpResponseRedirect(reverse('index'))

def delete_meeting(request, meeting_id):
    try:
        meet = meeting.objects.get(id=meeting_id)
    except(KeyError):
        return HttpResponseRedirect(reverse('index'))

    meet.delete()

    return HttpResponseRedirect(reverse('index'))

def page(request):
    return render(request,'index.html')


# Things to ask about:
# make sure you cannot add classes twice
# be able to sort users based on certain features
# change the setup of the page when you are not logged in
# if you change friends on backend it does not update main friends
# make sure you are showing the correct friend list once you remove people
# fix remove friend so it actually removes them

