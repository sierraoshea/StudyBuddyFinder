from django.views import generic
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .forms import EditProfileForm
from .models import UserClasses

def index(request):
    if request.user.is_authenticated:
        first_initial = request.user.username[0].upper()
    else:
        first_initial = ""
    return render(request, 'welcome/index.html', {'first_initial': first_initial})

class EditView(generic.UpdateView):
    form_class = EditProfileForm
    template_name = 'welcome/profile.html'
    success_url = reverse_lazy('index')

    def get_object(self):
        return self.request.user

def edit_classes(request):
    template_name = 'welcome/edit_classes.html'

    try:
        selected_class = request.user.userclasses_set.get(pk=request.POST['class'])
       
    except(KeyError):
        return render(request, template_name)
    else:
        selected_class.delete()
        return render(request, template_name)

    
