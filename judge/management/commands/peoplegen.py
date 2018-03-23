# coding: utf-8
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify

from judge.models import *
import os, sys, string
import unicodecsv as csv
import json

def mkstring(N):
	stringset = string.ascii_letters
	return ''.join([stringset[i % len(stringset)] for i in [ord(x) for x in os.urandom(N)]])

slugs = []
def mkslug(x):
	slug = slugify(x)
	if slug in slugs: slug += str(slugs.count(slug))
	slugs.append(slug)
	return slug

class Command(BaseCommand):
	help = """
	reads pile of data and generates people. assumes a ~/valid.csv exists.
	team names are slugified to create unique identifiers.
	usernames are the email address of the team captain.
	"""

	print "removing all users except whirlpool..."
	for u in User.objects.exclude(username="whirlpool"): u.delete()

	def handle(self, *args, **options):
		f = open("/home/whirlpool/valid.csv", "rb")
		out = []
		mails = []
		for row in list(csv.DictReader(f)):
			email = row["E-posta"]
			email2 = row["E-posta 2"]
			email3 = row["E-posta 3"]
			for mail in [email, email2, email3]:
				if mail == "": continue
				if mail in mails:
					print "wtf aq dupemail %s" % mail
					sys.exit(1)
				mails.append(mail)

			username = email
			passwd = mkstring(12)

			usr = User(username=username, email=email, is_active=True)
			usr.set_password(passwd)
			usr.is_superuser = False
			usr.save()
			print u"generated user with name=%s email=%s passwd=%s"% (username, email, passwd)

			profile = Profile(user=usr)
			profile.team_name = row["team_name"]
			profile.team_slug = mkslug(profile.team_name)[:16]
			profile.timezone = "Europe/Istanbul"
			profile.language = Language.objects.get(key="PY2")
			profile.save()
			print u"generated profile with team_name=%s team_slug=%s" % (profile.team_name, profile.team_slug)
			out.append({"mail1": row["E-posta"],
					"mail2": row["E-posta 2"],
					"mail3": row["E-posta 3"],
					"team_name": profile.team_name,
					"name1": row["ad1"].upper() + " " + row["soyad1"].upper(),
					"name2": row["ad2"].upper() + " " + row["soyad2"].upper(),
					"name3": row["ad3"].upper() + " " + row["soyad3"].upper(),
					"passwd": passwd})

		f.close()
		g = open("peoplegen.out", "w")
		json.dump(out, g)
		g.close()
