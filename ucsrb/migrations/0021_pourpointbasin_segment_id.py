# Generated by Django 2.2.17 on 2021-03-04 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ucsrb', '0020_streamflowreading_is_baseline'),
    ]

    operations = [
        migrations.AddField(
            model_name='pourpointbasin',
            name='segment_ID',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Stream Segment ID'),
        ),
    ]
