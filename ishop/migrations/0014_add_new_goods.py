from django.db import migrations


def add_new_goods(apps, schema_editor):
    Good = apps.get_model('ishop', 'Good')
    Good.objects.create(title='Beer Rogan 0.5l',
                        description='7%',
                        price=6,
                        in_stock=24)
    Good.objects.create(title='Beer Leffe 0.44l',
                        description='5%',
                        price=8,
                        in_stock=24)

def backward_action(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ishop', '0013_alter_shopuser_wallet'),
    ]

    operations = [
        migrations.RunPython(add_new_goods, backward_action)
    ]
