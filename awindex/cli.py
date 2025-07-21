import json
from .awelist import parse_awesome_list


# Entrypoint
if __name__ == "__main__":
    with open('test/awesome-digital-preservation.md', 'r') as fin:
        for pf in parse_awesome_list(fin, source="Awesome Digital Preservation"):
            print(pf.model_dump_json())


