from django import forms
from django.core.validators import RegexValidator
from .models import Order

class CheckoutForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=20,
        validators=[RegexValidator(r"^\+?[0-9][0-9\s()\-]{6,18}$", "Enter a valid phone number.")],
        widget=forms.TextInput(attrs={"class":"form-control", "autocomplete":"tel", "placeholder":"e.g. +91 98765 43210"}),
    )

    class Meta:
        model = Order
        fields = ("full_name", "email", "phone", "address", "city", "postal_code", "payment_method")
        widgets = {
            "full_name": forms.TextInput(attrs={"class":"form-control", "autocomplete":"name", "placeholder":"Name on the delivery"}),
            "email": forms.EmailInput(attrs={"class":"form-control", "autocomplete":"email", "placeholder":"you@example.com"}),
            "phone": forms.TextInput(attrs={"class":"form-control"}),
            "address": forms.Textarea(attrs={"class":"form-control", "rows":3, "autocomplete":"street-address", "placeholder":"House number, street, area"}),
            "city": forms.TextInput(attrs={"class":"form-control", "autocomplete":"address-level2", "placeholder":"City"}),
            "postal_code": forms.TextInput(attrs={"class":"form-control", "autocomplete":"postal-code", "placeholder":"PIN code"}),
            "payment_method": forms.Select(attrs={"class":"form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_method"].help_text = "Cash on Delivery places the order now. UPI and card open a demo payment step."
