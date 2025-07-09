from django import forms


class BookingForm(forms.Form):
    selected_seats = forms.CharField(widget=forms.HiddenInput())
