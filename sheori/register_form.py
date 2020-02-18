from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

from sheori.models import GENDER_LIST, RESIDENCE_LIST, Profile


class RegisterForm(UserCreationForm):
    age = forms.IntegerField(required=True)
    gender = forms.ChoiceField(choices=GENDER_LIST, required=True)
    residence = forms.ChoiceField(choices=RESIDENCE_LIST, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'age', 'gender', 'residence']
        labels = {
            'username': 'ユーザー名',
            'password1': 'パスワード',
            'password2': 'パスワード確認',
            'age': '年齢',
            'gender': '性別',
            'residence': '金沢在住経験',
        }

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError('Cannot create User and Profile without database save')

        user = super().save()

        try:
            max_id = Profile.objects.latest('id').id
        except ObjectDoesNotExist:
            max_id = 'U00000'

        prof_id = 'U' + (str(int(max_id[1:]) + 1).zfill(5))

        age = self.cleaned_data['age']
        gender = self.cleaned_data['gender']
        residence = self.cleaned_data['residence']

        profile = Profile(id=prof_id, age=age, gender=gender, residence=residence, user_id=user.id)
        profile.save()

        return user
