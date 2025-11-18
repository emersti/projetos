# Generated migration to add indexes for performance optimization
# Date: 2025-01-XX

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consulta_risco', '0018_add_coordenadas_cidade'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='avaliacaoseguranca',
            index=models.Index(fields=['estado', 'cidade', 'data_avaliacao'], name='aval_est_cid_data_idx'),
        ),
        migrations.AddIndex(
            model_name='avaliacaoseguranca',
            index=models.Index(fields=['data_avaliacao'], name='aval_data_idx'),
        ),
    ]

