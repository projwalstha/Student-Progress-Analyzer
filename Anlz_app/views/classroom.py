from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.views.generic import ListView
from ..models import  User
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
class SignUpView(TemplateView):
    template_name = 'registration/signup.html'
@method_decorator([staff_member_required],name='dispatch')
class UserListView(ListView):
    model=User
    context_object_name = 'User'
    template_name = 'admin_page.html'

def home(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teachers:quiz_change_list')
        elif request.user.is_student:
            return redirect('students:quiz_list')
        else:
            return redirect('admin_page')
    return render(request, 'base2.html')

@staff_member_required
def approve(request, pk):

    user = User.objects.get(id=pk)
    user.is_active = True
    user.save()
    return HttpResponse("Teacher's account Activated")
