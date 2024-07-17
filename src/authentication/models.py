import secrets
import time

from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from no_sql_client import NoSQLClient


class OrganismType(models.Model):
    label = models.CharField(unique=True, max_length=128, null=False, blank=False)
    description = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label}"


class Organism(models.Model):
    type = models.ForeignKey(OrganismType, on_delete=models.CASCADE)
    name = models.CharField(unique=True, max_length=128, null=False, blank=False)
    acronym = models.CharField(max_length=32, blank=True, null=True)
    address = models.CharField(max_length=256)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=22, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.acronym}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    organism = models.ForeignKey(Organism, on_delete=models.CASCADE, blank=True, null=True)


class Facilitator(models.Model):
    no_sql_user = models.CharField(max_length=150, unique=True)
    no_sql_pass = models.CharField(max_length=128)
    no_sql_db_name = models.CharField(max_length=150, unique=True)
    username = models.CharField(max_length=150, unique=True, verbose_name=_('username'))
    password = models.CharField(max_length=128, verbose_name=_('password'))
    code = models.CharField(max_length=6, unique=True, verbose_name=_('code'))
    active = models.BooleanField(default=False, verbose_name=_('active'))
    develop_mode = models.BooleanField(default=False, verbose_name=_('test mode'))
    training_mode = models.BooleanField(default=False, verbose_name=_('test mode'))
    organism = models.ForeignKey(Organism, on_delete=models.CASCADE, null=True, blank=True)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='user_supervisor')
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='user_coordinator')

    __current_password = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__current_password = self.password

    def __str__(self):
        return self.username

    def set_no_sql_user(self):
        now = str(int(time.time()))

        # Added to avoid repeating the same value for no_sql_user when bulk creating facilitators
        while Facilitator.objects.filter(no_sql_user=now).exists():
            now = str(int(time.time()))

        self.no_sql_user = now

    def simple_save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        replicate_design = True
        if "replicate_design" in kwargs:
            replicate_design = kwargs.pop("replicate_design")

        if not self.id:

            self.set_no_sql_user()

            no_sql_pass_length = 13
            self.no_sql_pass = secrets.token_urlsafe(no_sql_pass_length)

            self.no_sql_db_name = f'facilitator_{self.no_sql_user}'

            if not self.code:
                self.code = self.get_code(self.no_sql_user)

            if not self.password:
                self.password = f'ChangeItNow{self.code}'

            nsc = NoSQLClient()
            nsc.create_user(self.no_sql_user, self.no_sql_pass)
            facilitator_db = nsc.create_db(self.no_sql_db_name)
            if replicate_design:
                nsc.replicate_design_db(facilitator_db)
            nsc.add_member_to_database(facilitator_db, self.no_sql_user)

        if self.password and self.password != self.__current_password:
            self.password = make_password(self.password, salt=None, hasher='default')

        return super().save(*args, **kwargs)

    def hash_password(self, *args, **kwargs):
        self.password = make_password(self.password, salt=None, hasher='default')
        return super().save(*args, **kwargs)

    def create_without_no_sql_db(self, *args, **kwargs):

        if not self.code:
            self.code = self.get_code(self.no_sql_user)

        if not self.password:
            self.password = f'ChangeItNow{self.code}'

        self.password = make_password(self.password, salt=None, hasher='default')

        return super().save(*args, **kwargs)

    def create_with_no_sql_db(self, *args, **kwargs):

        if not self.id:
            self.set_no_sql_user()

            no_sql_pass_length = 13
            self.no_sql_pass = secrets.token_urlsafe(no_sql_pass_length)

            if not self.code:
                self.code = self.get_code(self.no_sql_user)

            nsc = NoSQLClient()
            nsc.create_user(self.no_sql_user, self.no_sql_pass)
            facilitator_db = nsc.get_db(self.no_sql_db_name)
            nsc.add_member_to_database(facilitator_db, self.no_sql_user)

        if self.password and self.password != self.__current_password:
            self.password = make_password(self.password, salt=None, hasher='default')

        return super().save(*args, **kwargs)

    def create_with_manually_assign_database(self, *args, **kwargs):

        if not self.id:
            self.set_no_sql_user()

            if not self.code:
                self.code = self.get_code(self.no_sql_user)

            if not self.password:
                self.password = f'ChangeItNow{self.code}'
            self.password = make_password(self.password, salt=None, hasher='default')

            nsc = NoSQLClient()
            nsc.create_user(self.no_sql_user, self.no_sql_pass)
            facilitator_db = nsc.get_db(self.no_sql_db_name)
            nsc.add_member_to_database(facilitator_db, self.no_sql_user)

        if self.password and self.password != self.__current_password:
            self.password = make_password(self.password, salt=None, hasher='default')

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        no_sql_db = None
        if "no_sql_db" in kwargs:
            no_sql_db = kwargs.pop("no_sql_db")
        NoSQLClient().delete_user(self.no_sql_user, no_sql_db)
        # print(f'self.no_sql_user {self.no_sql_user}')
        # print(f'no_sql_db {no_sql_db}')
        super().delete(*args, **kwargs)

    @staticmethod
    def get_code(seed):
        import zlib
        return str(zlib.adler32(str(seed).encode('utf-8')))[:6]

    def get_name(self):
        try:
            nsc = NoSQLClient()
            facilitator_database = nsc.get_db(self.no_sql_db_name)
            return facilitator_database.get_query_result(
                {"type": "facilitator"}
            )[:][0]['name']
        except Exception as e:
            return None

    def get_name_with_sex(self):
        try:
            nsc = NoSQLClient()
            facilitator_doc = nsc.get_db(self.no_sql_db_name).get_query_result(
                {"type": "facilitator"}
            )[:][0]
            return f"{facilitator_doc['sex']} {facilitator_doc['name']}" if facilitator_doc.get('sex') else \
                facilitator_doc['name']
        except Exception as e:
            return None

    def get_email(self):
        try:
            nsc = NoSQLClient()
            facilitator_database = nsc.get_db(self.no_sql_db_name)
            return facilitator_database.get_query_result(
                {"type": "facilitator"}
            )[:][0]['email']
        except Exception as e:
            return None

    def get_type(self):
        if self.develop_mode and self.training_mode:
            return "develop-training"
        elif self.develop_mode:
            return "develop"
        elif self.training_mode:
            return "training"
        else:
            return "deploy"

    class Meta:
        verbose_name = _('Facilitator')
        verbose_name_plural = _('Facilitators')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    pass
    # instance.user_profile.save()
