# Generated by Django 4.2.23 on 2025-06-29 01:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0003_vehicle_image_vehicle_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='الوصف'),
        ),
        migrations.CreateModel(
            name='VehicleMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='vehicles/extra_images/')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='vehicles.vehicle')),
            ],
        ),
    ]
