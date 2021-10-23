from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from django.views.generic import CreateView
from django.contrib.auth import  authenticate
from django.shortcuts import render, redirect
from accounts.forms import SignUpForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_user_model
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin




class SignUpView(CreateView):
    def post(self, request, *args, **kwargs):
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            auth_login(request, user)
            return redirect('authorize')
        return render(request, 'registration/signup.html', {'form': form})

    def get(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        return render(request, 'registration/signup.html', {'form': form})

    def form_valid(self, form):
        user = form.save()
        auth_login(self.request, user)
        self.object = user
        return HttpResponseRedirect(self.get_success_url())

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('main')
        else:
            return redirect('login')
    return render(request, 'registration/login.html')



class UserDeleteView(LoginRequiredMixin, generic.View):
    def get(self, *args, **kwargs):
        User = get_user_model()
        User.objects.filter(email=self.request.user.email).delete()
        auth_logout(self.request)
        return redirect('index')
        # return render(self.request, 'registration/delete.html')
