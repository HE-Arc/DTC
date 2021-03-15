# Generated by Django 3.1.5 on 2021-03-15 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtcapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]