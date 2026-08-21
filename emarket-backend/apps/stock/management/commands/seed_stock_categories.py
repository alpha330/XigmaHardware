from apps.stock.management.commands._sample_seed import BaseSampleSeedCommand
from apps.stock.sample_data.seeder import seed_categories


class Command(BaseSampleSeedCommand):
    help = "Create or update the Xigma sample product taxonomy."
    seed_function = staticmethod(seed_categories)
    result_label = "categories"
