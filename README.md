# Django-Iran-OTP
Django Iran OTP is django plugin to authenticate user with phone number and generate one-time password

## Usage
```bash
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts.apps.AccountsConfig",
    "user.apps.UserConfig"
]
AUTH_USER_MODEL = 'user.User'

```
Its important user model have (number) CharField

## setting.py
```bash


AUTH_TIME = timedelta(minutes=2)
AUTH_TIME_AGAIN = timedelta(minutes=1)
AUTH_STEP_ONE_TEMPLATE = 'accounts/auth.html'
AUTH_TIME_AGAIN_MILISECOND = 60000
AUTH_STEP_TWO_TEMPLATE = 'accounts/second-auth.html'
AUTH_SERVICE = {
    "SMS.IR":{
        "secret_key":"",
        "user_api_key":"",
        "otp_template_id":""
    }
}
LOGIN_REDIRECT_OTP = '/'
```
## AUTH_TIME
Time for expire token

## AUTH_TIME_AGAIN
Time for resend token
## LOGIN_REDIRECT_OTP
default:'/'
redirect url after login is successful
## Override Template: AUTH_STEP_ONE_TEMPLATE | AUTH_STEP_TWO_TEMPLATE
Override template
!Important
Request POST name for get number ===== request.POST.get('number')
context ={
'millisecond':AUTH_TIME_AGAIN_MILISECOND
}
for set setInterval in frontend
# AUTH_SERVICE:(SMS.IR) & ... soon
