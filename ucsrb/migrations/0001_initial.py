# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-08 01:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('scenarios', '0003_auto_20171207_1705'),
    ]

    operations = [
        migrations.CreateModel(
            name='VegPlanningUnit',
            fields=[
                ('planningunit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='scenarios.PlanningUnit')),
                ('has_roads', models.BooleanField(default=False)),
                ('has_endangered_habitat', models.BooleanField(default=False)),
                ('is_private', models.BooleanField(default=False)),
                ('has_high_fire_risk', models.BooleanField(default=False)),
                ('miles_from_road_access', models.IntegerField()),
                ('vegetation_type', models.CharField(blank=True, max_length=255, null=True)),
                ('forest_height', models.IntegerField()),
                ('forest_class', models.CharField(blank=True, max_length=255, null=True)),
                ('slope', models.IntegerField()),
                ('canopy_coverage', models.IntegerField()),
            ],
            bases=('scenarios.planningunit',),
        ),
    ]
