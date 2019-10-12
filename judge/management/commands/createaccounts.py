from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify

from judge.models import *

import os, sys, string

def mkstring(N):
	stringset = string.ascii_letters
	return ''.join([stringset[i % len(stringset)] for i in [ord(x) for x in os.urandom(N)]])

slugs = []

def mkslug(x):
	slug = slugify(x)

    if slug == '' or slug in slugs:
        slug += str(slugs.count(slug))

    slugs.append(slug)

    return slug

class Command(BaseCommand):
	for u in User.objects.exclude(is_staff=True): u.delete()

	def handle(self, *args, **options):
		number = int(input())

        for _ in range(number):
            items = input().split(',')

            name = items[0]
            email = items[1]

            username = email

            passwd = mkstring(12)

            usr = User(username=username, email=email, is_active=True)
            usr.set_password(passwd)
            usr.is_superuser = False
            usr.save()

            profile = Profile(user=usr)
            profile.team_name = username
            profile.team_slug = mkslug(profile.team_name)[:16]
            profile.timezone = "Europe/Istanbul"
            profile.language = Language.objects.get(key="PY2")
            profile.save()

            print(username, passwd)