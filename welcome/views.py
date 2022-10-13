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
import ast



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
    current_classes = []
    for cur_class in request.user.userclasses_set.all():
        current_classes.append(cur_class.as_array())
    return render(request, template_name, {'class_list': class_list, 'current_classes': current_classes})


def delete_class(request):
    template_name = 'welcome/edit_classes.html'
    try:
        selected_class = request.user.userclasses_set.get(pk=request.POST['class_to_delete'])
       
    except(KeyError):
        return HttpResponseRedirect(reverse('classes'))
    else:
        selected_class.delete()
        return HttpResponseRedirect(reverse('classes'))


def add_classes(request):
    try:
        selected_classes = request.POST.getlist('class_to_add')
    except(KeyError):
        return HttpResponseRedirect(reverse('classes'))
    
    else:
        add = True
        for class_to_add in selected_classes:
            c = ast.literal_eval(class_to_add)
            UserClasses.objects.create(user=request.user,subject=c[0], catalog_number=c[1], component=c[2])
        return HttpResponseRedirect(reverse('classes'))
