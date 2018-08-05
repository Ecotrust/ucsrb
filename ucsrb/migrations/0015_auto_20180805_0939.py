# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-08-05 09:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ucsrb', '0014_treatmentscenario_aggregate_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScenarioNNLookup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ppt_id', models.IntegerField(verbose_name='Pour Point ID')),
                ('scenario_id', models.IntegerField(verbose_name='Harvest Scenario Identifier')),
                ('treatment_target', models.IntegerField()),
                ('fc_delta', models.FloatField(verbose_name='Percent Change in Fractional Coverage')),
            ],
        ),
        migrations.AddField(
            model_name='pourpoint',
            name='imputed_ppt',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='ucsrb.PourPoint', verbose_name='Nearest Neighbor Match'),
        ),
        migrations.AddField(
            model_name='pourpoint',
            name='streammap_id',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='pourpoint',
            name='watershed_id',
            field=models.CharField(blank=True, choices=[('ent', 'Upper Entiat'), ('met', 'Upper Methow'), ('wen', 'Chiwawa')], default=None, max_length=3, null=True, verbose_name='Modeled Watershed Identifier'),
        ),
    ]
