from apps.stock.management.commands._sample_seed import BaseSampleSeedCommand
from apps.stock.sample_data.seeder import seed_brands


class Command(BaseSampleSeedCommand):
    help = "Create or update the curated Xigma sample hardware brands."
    seed_function = staticmethod(seed_brands)
    result_label = "brands"
