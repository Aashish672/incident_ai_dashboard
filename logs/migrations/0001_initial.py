# Generated by Django 5.1.3 on 2025-07-17 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('log_level', models.CharField(choices=[('INFO', 'Info'), ('WARNING', 'Warning'), ('ERROR', 'Error'), ('DEBUG', 'Debug'), ('CRITICAL', 'Critical')], max_length=10)),
                ('message', models.TextField()),
                ('source', models.CharField(blank=True, max_length=255, null=True)),
                ('is_anomaly', models.BooleanField(default=False)),
            ],
        ),
    ]
