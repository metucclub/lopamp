# coding: utf-8
from django.core.management.base import BaseCommand

from django.core.mail import EmailMessage

from django.template import Context, Template
from django.template.loader import render_to_string
import json

mail_template = """
ODTÜ Bilgisayar Topluluğu 21. Programlama Yarışması başlıyor! 

Yarışmamıza kaydınızı yaptırdığınızı unutmamışsınızdır ama biz yine de hatırlatalım ve biraz da sizi bilgilendirelim istedik. 

Yarışmamız 23 Mart akşamı saat 20:00’de başlayacak ve 26 Mart Pazartesi saat 08:00’e kadar sürecek. Toplam 6 soruyu çözmek için 60 saatiniz olacak ve süreniz sistem açıldığında başlayacak. Sisteme istediğiniz zaman girip çıkıp daha sonra tekrar girebileceksiniz. Yarışmanın ilk 52 saatinde takımların sıralamaları herkese açık olacak, sıralama ekranı son 8 saatte kapatılacak. 

Final etabına katılmaya hak kazanan 17 takım için yarışmayı takip eden hafta içinde asiller ve yedekler olmak üzere 2 liste yayınlanacak ve asil listeden önlisans ya da lisans öğrencisi olduklarına dair öğrenci belgeleri istenecek. Asil listede olup öğrenci belgesi yollamayan takımlar yerine yedek listedeki takımlarla iletişime geçilecek ve finale kalan 17 takım böylece belirlenecek.

Yarışma sistemine mailin sonunda bulabileceğiniz giriş bilgileriyle saat 20:00’den itibaren yarisma.cclub.metu.edu.tr üzerinden giriş yapabileceksiniz. Herhangi bir sorunuz için bu maili yanıtlamak yerine cclub@metu.edu.tr adresine mail atarak bize ulaşabilirsiniz.

ODTÜ Bilgisayar Topluluğu olarak başarılar dileriz!

Takım adı: {{ team_name }}
Üyeler:
{{ name1 }}
{{ name2 }}
{{ name3 }}

Giriş bilgileri:
Giriş maili (takım kaptanının mail adresi): {{ mail1 }}
Şifre: {{ passwd }}
"""

class Command(BaseCommand):
	help = """
	reads email addresses, team names and passwords from a file
	and guns the stuff to the emails it found.
	"""
	def add_arguments(self, parser):
		parser.add_argument("file", help="where are stuff")

	def handle(self, *args, **options):
		teams = json.load(open(options["file"]))
		for team in teams:
			msg = Template(mail_template).render(Context(team))
			email = EmailMessage("ODTÜ Bilgisayar Topluluğu 21. Programlama Yarışması",
								msg,
								to=[team["mail1"], team["mail2"], team["mail3"]])
			email.send()
