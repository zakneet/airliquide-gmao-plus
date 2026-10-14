from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'password')
        read_only_fields = ('id',)

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated):
        password = validated.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Ce champ est obligatoire.'})
        return User.objects.create_user(password=password, **validated)

    def update(self, instance, validated):
        password = validated.pop('password', None)
        user = super().update(instance, validated)
        if password:
            user.set_password(password)
            user.save()
        return user
