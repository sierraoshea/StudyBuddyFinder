from django.views import generic
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

from django.shortcuts import redirect
from .forms import EditProfileForm
from .models import UserClasses, Class, UserToUserChat, Time, Day 
import ast
import requests
from itertools import groupby
from .models import Friend_Request
from .models import Class
from .models import FriendList



def index(request):
    if request.user.is_authenticated:
        if not request.user.day_set.all():
            days = ['M','T','W','Th','F','Sa','Su']
            for day in days:
                thisday = Day.objects.create(user= request.user, day = day)
                for j in range(10, 23):
                    Time.objects.create(day = thisday, time = str(j)+":00")

        #current_list = FriendList.objects.select_related().filter(user=request.user.id)
        #if current_list.exists():
            #friend_list = current_list.first().friends
    #return render(request, 'welcome/index.html', {'friends': friend_list})
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
                thisclass = Class.objects.get(id.subject +str(id.catalog_number))
                thisclass.students.remove(request.user)
            except:
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
            UserClasses.objects.create(user=request.user,subject=c[0], catalog_number=c[1], component=c[2], section=c[3], professor=c[4])
        return HttpResponseRedirect(reverse('classes'))


def subject_view(request, subject):
    classes = requests.get('http://luthers-list.herokuapp.com/api/dept/' + subject + '/?format=json').json()
    
    
    result = {
            key : list(group) for key, group in groupby(classes,key=lambda x:x['subject'] + " " + x['catalog_number'] + " " + x['description'])
           } 

    return render(request, 'welcome/subject.html', {'classes': result})


def search_classes(request):
    searchPhrase = request.POST['searchbox']
    foundClasses = []
    response = requests.get('http://luthers-list.herokuapp.com/api/dept/CS/?format=json').json()
    for thisClass in response:
        if searchPhrase in thisClass["description"]:
            foundClasses.append(thisClass)
    return render(request, 'welcome/home.html', {'response': foundClasses})


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
    current_list = FriendList.objects.select_related().filter(user=request.user.id)
    friend_list = current_list.first().friends
    friend_request, created = Friend_Request.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        return HttpResponseRedirect(reverse('index'), {'friend_list': friend_list})
    else:
        return HttpResponseRedirect(reverse('index'), {'friend_list': friend_list})


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
        return HttpResponseRedirect(reverse('friends'), {'friend_list': friend_list.friends})
    for i in current_list:
        i.friends.add(friend_request.from_user)
        add_friend_back(friend_request.from_user, friend_request.to_user)
        if request.method == "POST":
            friend_request.delete()
            return HttpResponseRedirect(reverse('friends'), {'friend_list': i.friends})


def add_friend_back(to_user, from_user):
    current_list = FriendList.objects.select_related().filter(user=to_user)
    if not current_list.exists():
        friend_list = FriendList()
        friend_list.user = to_user
        friend_list.save()
        friend_list.friends.add(from_user)
        friend_list.save()
        return HttpResponseRedirect(reverse('friends'), {'friend_list': friend_list.friends})
    for i in current_list:
        i.friends.add(from_user)
        return HttpResponseRedirect(reverse('friends'), {'friend_list': i.friends})


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
                return HttpResponseRedirect(reverse('friends'), {'friend_list': i.friends})
        from_user_friendlist = FriendList.objects.select_related().filter(user=from_user)
        if from_user_friendlist.exists():
            for j in from_user_friendlist:
                j.friends.remove(to_user)
                return HttpResponseRedirect(reverse('friends'), {'friend_list': j.friends})


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


def rooms(request):
    
    rooms = UserToUserChat.objects.filter(user1=request.user) | UserToUserChat.objects.filter(user2=request.user)

    return render(request, 'welcome/rooms.html', {'rooms': rooms})


def room(request, room_name):
    if not UserToUserChat.objects.filter(roomName=room_name):
        return HttpResponseRedirect(reverse('index')) #doesn't exist
    
    room = UserToUserChat.objects.get(roomName=room_name)
    if(request.user != room.user1 and request.user != room.user2):
        return HttpResponseRedirect(reverse('index')) #not allowed
    
    return render(request, 'welcome/room.html', {'room_name': room_name})


def updateTimes(request):
    try:
        ids = request.POST.getlist('available_times')
    except(KeyError):
        return HttpResponseRedirect(reverse('index'))

    for day in request.user.day_set.all():
        for time in day.time_set.all():
            if day.day+time.time in ids:
                time.available = True
                time.save()
            else:
                time.available = False
                time.save()

    return HttpResponseRedirect(reverse('index'))

def page(request):
    return render(request,'index.html')


# Things to ask about:
# How to disable a button and make it say sent after friend request was sent
# How to make sure you cannot send a friend request to someone twice
# Add a logout feature
# Removing friends from a list
