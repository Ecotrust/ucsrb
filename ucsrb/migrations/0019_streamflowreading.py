# Generated by Django 2.2.17 on 2021-03-03 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ucsrb', '0018_auto_20210303_1346'),
    ]

    operations = [
        migrations.CreateModel(
            name='StreamFlowReading',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.CharField(max_length=30, verbose_name='Reading Timestamp')),
                ('metric', models.CharField(choices=[('abs_rate', 'Absolute Flow Rate'), ('delta_abs_rate', 'Change in Flow Rate'), ('seven_low', 'Seven Day Low Flow'), ('seven_mean', 'Seven Day Mean Flow'), ('one_low', 'One Day Low Flow'), ('one_mean', 'One Day Mean Flow'), ('delta_seven_low', 'Change in 7 Day Low Flow'), ('delta_seven_mean', 'Change in 7 Day Mean Flow'), ('delta_one_low', 'Change in 1 Day Low Flow'), ('delta_one_mean', 'Change in 1 Day Mean Flow')], max_length=30, verbose_name='Measurement Metric')),
                ('value', models.FloatField(verbose_name='Reading in m^3/hr')),
                ('basin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ucsrb.PourPointBasin', verbose_name='Stream Segment Basin')),
                ('treatment', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='ucsrb.TreatmentScenario', verbose_name='Treatment Scenario')),
            ],
        ),
    ]
