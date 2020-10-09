
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group

from django.dispatch import receiver
from django.db.models.signals import post_save

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator

from project.settings import SITE_ID
from project.models import LogMixin


class Company(LogMixin):
    name = models.CharField('Name', max_length=63)
    credits = models.PositiveIntegerField(default=0)
    subscription_based = models.BooleanField(default=False)

    class Meta:
        managed = True
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return '{}: {} {}'.format(self.name, self.credits, self.subscription_based)


class AuthUser(AbstractUser):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return '{} {}'.format(self.username, self.company)


class AuthGroup(Group):
    class Meta:
        proxy = True
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'


@receiver(post_save, sender=AuthUser)
def send_password_reset_email_when_created(sender, instance, created, *args, **kwargs):
    if created and not instance.is_staff:
        user = AuthUser._default_manager.get(email__iexact=instance.email)
        current_site = Site.objects.get(id=SITE_ID)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': 'http',
        }
        subject = loader.render_to_string(
            'registration/password_reset_subject.txt', context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(
            'registration/password_reset_email.html', context)
        email_message = EmailMultiAlternatives(
            subject, body, 'admin@abc.com', [user.email])
        email_message.send()
        print('password reset email sent')