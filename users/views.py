from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views import View

from .forms import LoginForm, RegistrationForm


class RegisterView(View):
    """
    Handles user registration process.

    If the given data are valid then it creates user,create and save hashed password
    in database.Also flashes a success message.

    """

    def get(self, request):
        form = RegistrationForm()
        return render(request, "users/register.html", {"form": form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!!!")
            return redirect("login")
        else:
            messages.error(request, "Registration failed. Please check the errors.")
        return render(request, "users/register.html", {"form": form})


class LoginView(View):
    """
    Handles user login process.

    If the given data are valid then users are directed to home page and
    flashes a success message.But if data are not valid it flashes a unsuccessful
    message.

    """

    def get(self, request):
        form = LoginForm()
        return render(request, "users/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect("dashboard:movie-list")
            else:
                messages.error(
                    request, "Login Unsuccessful. Please check your email and password."
                )
        return render(request, "users/login.html", {"form": form})


class LogoutView(View):
    """
    Handles user logout process.

    When a user ask for logout,they are logged out and are
    redirected to the login page.

    """

    def get(self, request):
        logout(request)
        return redirect("login")
