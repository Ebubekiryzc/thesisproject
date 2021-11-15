from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, label='Kullanıcı Adı')
    password = forms.CharField(
        max_length=20, label='Parola', widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    email = forms.CharField(max_length=320, label='Email',widget=forms.EmailInput)
    username = forms.CharField(max_length=50, label='Kullanıcı Adı')
    password = forms.CharField(
        max_length=20, label='Parola', widget=forms.PasswordInput)
    confirmPassword = forms.CharField(
        max_length=20, label='Parolayı Doğrula', widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        confirmPassword = self.cleaned_data.get('confirmPassword')

        if password and confirmPassword and password != confirmPassword:
            raise forms.ValidationError('Parolalar Eşleşmiyor')

        values = {
            'email': email,
            'username': username,
            'password': password,
        }
        return values
