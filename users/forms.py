# users/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CareerProfile

class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email or username',
        }),
        label='Email or Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
        }),
        label='Password'
    )


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']  # 'username' removed from display fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email address'
        })

        self.fields['password1'].widget.attrs.update({
            'id': 'id_password1',
            'class': 'form-control',
            'placeholder': 'Enter password'
        })

        self.fields['password2'].widget.attrs.update({
            'id': 'id_password2',
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })


class EducationForm(forms.ModelForm):
    EDUCATION_LEVELS = [
        ('', 'Select your highest level of education'),  # default placeholder
        ('high_school', "High School"),
        ('associate', "Associate Degree"),
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('phd', "Ph.D."),
        ('other', "Other"),
    ]

    highest_education = forms.ChoiceField(
        choices=EDUCATION_LEVELS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CareerProfile
        fields = ['highest_education', 'field_of_study', 'university']
        widgets = {
            'field_of_study': forms.TextInput(attrs={'class': 'form-control'}),
            'university': forms.TextInput(attrs={'class': 'form-control'}),
        }


INTEREST_CHOICES = [
    ('Data Science', 'Data Science'),
    ('Web Development', 'Web Development'),
    ('AI / ML', 'AI / ML'),
    ('Cybersecurity', 'Cybersecurity'),
    ('UI/UX Design', 'UI/UX Design'),
    ('Project Management', 'Project Management'),
    ('Product Design', 'Product Design'),
]

SKILL_CHOICES = [
    ('Python', 'Python'),
    ('JavaScript', 'JavaScript'),
    ('SQL', 'SQL'),
    ('HTML/CSS', 'HTML/CSS'),
    ('Git', 'Git'),
    ('Communication', 'Communication'),
    ('Teamwork', 'Teamwork'),
    ('Leadership', 'Leadership'),
    ('React', 'React'),
]


class BackgroundForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(
        choices=[(c[0], c[1]) for c in INTEREST_CHOICES],  # only (value, label)
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    skills = forms.MultipleChoiceField(
        choices=[(c[0], c[1]) for c in SKILL_CHOICES],  # only (value, label)
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = CareerProfile
        fields = ['academic_background', 'interests', 'skills']
        widgets = {
            'academic_background': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'E.g. I studied Computer Science with focus on software engineering...'
            }),
        }


class GoalsForm(forms.ModelForm):
    class Meta:
        model = CareerProfile
        fields = ['career_goals', 'avatar']
        widgets = {
            'career_goals': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your career goals here...'
            }),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
