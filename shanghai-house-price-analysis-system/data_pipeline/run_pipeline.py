from collect_lianjia_listings import main as collect_lianjia
from collect_price_indices import main as collect_price_indices
from clean_data import main as clean_data


def main() -> None:
    collect_price_indices()
    collect_lianjia()
    clean_data()


if __name__ == "__main__":
    main()
