# Generated by Django 2.2.12 on 2021-02-26 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainFrame', '0009_auto_20210205_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensordata',
            name='batterylevel',
            field=models.IntegerField(null=True),
        ),
    ]
