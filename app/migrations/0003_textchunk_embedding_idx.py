# Generated by Django 5.1.4 on 2024-12-30 06:52

import pgvector.django.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_textchunk_embedding'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='textchunk',
            index=pgvector.django.indexes.HnswIndex(
                ef_construction=64,
                fields=['embedding'],
                m=16,
                name='embedding_idx',
                opclasses=['vector_cosine_ops']
            ),
        ),
    ]

