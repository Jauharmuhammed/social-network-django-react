from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.accounts.models import CustomUser, UserProfile
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
import datetime

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['is_admin'] = user.is_superuser

        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'mobile_number', 'first_name', 'last_name', 'date_joined', 'is_superuser', 'is_active']

    def get_profile(self, obj):
            profile = obj.userprofile
            serializer = UserProfileSerializer(profile, many=False)
            return serializer.data

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=CustomUser.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('email', 'password', )


    def create(self, validated_data):
        email=validated_data['email']
        username = email.split('@')[0]

        try:

            user = CustomUser.objects.create(
                email=validated_data['email'].lower(),
                username=username,
            )
        except:
            random = str(datetime.datetime.now().microsecond)[:4]
            username = str(email.split('@')[0]) + random
            print(username)

            user = CustomUser.objects.create(
                email=validated_data['email'].lower(),
                username=username,
            )

        
        user.set_password(validated_data['password'])
        user.save()

        return user



class UserProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField(read_only=True)
    followers_count = serializers.IntegerField(source='get_followers_count')
    followings_count = serializers.IntegerField(source='get_followings_count')
    full_name = serializers.CharField(source='get_full_name')
    class Meta:
        model = UserProfile
        exclude = ['profile_picture', 'profile_picture_url']

    def get_profile_pic(self, obj):
        try:
            pic = obj.profile_picture.url
        except:
            pic = '/media/profile_picture/profile.png'
        return pic

