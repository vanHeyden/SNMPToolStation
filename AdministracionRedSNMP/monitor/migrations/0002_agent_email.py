# Generated by Django 2.1.7 on 2019-03-10 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='email',
            field=models.EmailField(default='samplemail@hotmail.com', max_length=254),
        ),
    ]
