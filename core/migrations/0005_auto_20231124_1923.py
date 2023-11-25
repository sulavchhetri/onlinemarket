# Generated by Django 2.2.14 on 2023-11-24 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20190630_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='slug',
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('C', 'Clothes'), ('M', 'Mobiles & Tablets'), ('H', 'Home Appliances'), ('W', 'Wearables')], max_length=2),
        ),
    ]