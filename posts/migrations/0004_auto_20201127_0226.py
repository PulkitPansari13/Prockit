# Generated by Django 3.0.3 on 2020-11-26 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20201126_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(default='default_profile_pic6.svg', upload_to='profile_pics'),
        ),
    ]
