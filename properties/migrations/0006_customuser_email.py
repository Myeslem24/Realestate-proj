# Generated by Django 5.2 on 2025-05-09 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_customuser_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ]
