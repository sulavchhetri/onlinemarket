# Generated by Django 2.2.14 on 2023-12-01 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_reviewcomment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewcomment',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
