from django.urls import path
from .views import auth, auth_second_step,  send_auth_token_again

app_name = 'accounts'

urlpatterns = [
    path('auth',auth,name='auth'),
    path('_second-auth',auth_second_step,name='second-auth'),
    path('send-auth-token',send_auth_token_again,name='send-auth-token-again'),

]
