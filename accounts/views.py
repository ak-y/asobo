from django.http import HttpResponse, JsonResponse, HttpResponseRedirect

from django.views.generic import CreateView
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from accounts.forms import SignUpForm

class SignUpView(CreateView):
    def post(self, request, *args, **kwargs):
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('authorize')
        return render(request, 'registration/signup.html', {'form': form})

    def get(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        return render(request, 'registration/signup.html', {'form': form})

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.object = user
        return HttpResponseRedirect(self.get_success_url())

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            return redirect('login')
    return render(request, 'calendarapp/signin.html')