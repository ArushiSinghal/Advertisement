from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.models import User

#from userauth.models import UserProfile,
from userauth.models import UploadAdvetisement,Add_Device
class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

   	class Meta:
        	model = User
        	fields = ('username', 'email', 'password', 'first_name' , 'last_name',)

'''class UserProfileForm(forms.ModelForm):
	#password2 = forms.CharField(label=_("Password confirmation"),
        #widget=forms.PasswordInput,
        #help_text=_("Enter the same password as above, for verification."))
    	class Meta:
        	model = UserProfile
        	#fields = ('applying_as_a','first_name','last_name',)
		fields = ('applying_as_a',)'''
class UploadForm(forms.ModelForm):
	class Meta:
		model = UploadAdvetisement
		fields = ('upload_Advertisement','time_of_advertisement'
		   		,'no_of_slots','select_bundles','no_of_weeks','bussinessPoint_longitude'
				,'bussinessPoint_latitude')
		# widgets = {'bussinessPoint_longitude': forms.HiddenInput() }
class  Login_Adver(forms.ModelForm):
        password = forms.CharField(widget=forms.PasswordInput())
        #password = forms.CharField(max_length=32, widget=forms)           
        class Meta:
                model = Add_Device
                fields = ('Username','password',)

