# Generated by Django 3.2.7 on 2021-09-25 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('name', models.CharField(max_length=15)),
                ('password', models.CharField(max_length=15)),
                ('mail_address', models.CharField(max_length=30)),
            ],
        ),
    ]