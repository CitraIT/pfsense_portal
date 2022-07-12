from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from .forms import LoginForm


@login_required
def index(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login")
    else:
        return redirect("/dashboard")


@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                return redirect("/dashboard")
            else:
                return render(request, "core/login.html", context={'form': form, 'error': 'Usuário ou senha inválidos'})
        else:
                return render(request, "core/login.html", context={'form': form, 'error': 'Usuário ou senha inválidos'})
    else:
        form = LoginForm()
        return render(request, "core/login.html", context={'form': form})



# Logout
@login_required
def logout_user(request):
    logout(request)
    return redirect("/")
