# Generated by Django 3.2.7 on 2022-04-29 11:57

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('molecule_handler', '0002_proteinsite'),
    ]

    operations = [
        migrations.CreateModel(
            name='SienaInfo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('statistic', models.JSONField()),
                ('alignment', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SienaJob',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('p', 'pending'), ('r', 'running'), ('s', 'success'), ('f', 'failure')], default='p', max_length=1)),
                ('error', models.TextField(null=True)),
                ('error_detailed', models.TextField(null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('date_last_accessed', models.DateField(auto_now=True)),
                ('hash_value', models.CharField(default=None, max_length=256, null=True, unique=True)),
                ('input_ligand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_siena_job_set', to='molecule_handler.ligand')),
                ('input_protein', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child_siena_job_set', to='molecule_handler.protein')),
                ('input_site', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_siena_job_set', to='molecule_handler.proteinsite')),
                ('output_info', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='siena.sienainfo')),
                ('output_proteins', models.ManyToManyField(related_name='parent_siena_job', to='molecule_handler.Protein')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='sienainfo',
            name='parent_siena_job',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='siena.sienajob'),
        ),
    ]
