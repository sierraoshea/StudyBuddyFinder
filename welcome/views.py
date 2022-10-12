from django.views import generic
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .forms import EditProfileForm
from .models import UserClasses



def index(request):
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
    class_list = [["CS", 3100, "LEC"], ["CS", 3240, "LEC"]]
    return render(request, template_name, {'class_list': class_list})


def delete_class(request):
    template_name = 'welcome/edit_classes.html'
    try:
        selected_class = request.user.userclasses_set.get(pk=request.POST['class'])
       
    except(KeyError):
        return HttpResponseRedirect(reverse('classes'))
    else:
        selected_class.delete()
        return HttpResponseRedirect(reverse('classes'))


def add_classes(request):
    return HttpResponse("Not setup yet")