# Generated by Django 4.1 on 2022-11-02 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('welcome', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userclasses',
            name='professor',
            field=models.TextField(max_length=200),
        ),
    ]
