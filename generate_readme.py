import os
import csv
import argparse

ROOT = "papers"
FILE_NAME = "papers.csv"
TEMPLATE_FILE = "README.template"
UNCATEGORIZED_TEMPLATE_FILE = "README.uncategorized.template"

directory = [
    "phenomena-of-interest/in-context-learning",
    "phenomena-of-interest/chain-of-thought",
    "phenomena-of-interest/hallucination",
    "phenomena-of-interest/reversal-curse",
    "phenomena-of-interest/scaling-laws",
    "phenomena-of-interest/knowledge",
    "phenomena-of-interest/training-dynamics",
    "phenomena-of-interest/learning",
    "phenomena-of-interest/other-phenomena",
    "representational-capacity/what-can-transformer-do",
    "representational-capacity/what-can-transformer-not-do",
    "architectural-effectivity/layer-normalization",
    "architectural-effectivity/tokenization",
    "architectural-effectivity/linear-attention",
    "training-paradigms",
    "mechanistic-engineering",
    "miscellanea",
]


TEMPLATE = """
- **{}** [[paper link]]({}) {}  
{}
"""


def get_section_list(topic):
    p = os.path.join(ROOT, topic, FILE_NAME)

    # read as dict, the first line is the header

    with open(p, "r") as f:
        reader = csv.DictReader(f)
        # sort by date
        reader = sorted(reader, key=lambda x: x["Date"], reverse=True)
        # sanity check of each row
        for row in reader:
            assert len(row.keys()) == 4, f"topic: {topic}, row: {row}"
            for key in row.keys():
                assert key in [
                    "Title",
                    "Date",
                    "Url",
                    "Author",
                ], f"topic: {topic}, key: {key}, row: {row}"

        paper_list = []

        # add each row to the list and check for duplicates

        for row in reader:
            paper = TEMPLATE.format(
                row["Title"], row["Url"], row["Date"], row["Author"]
            )
            if paper not in paper_list:
                paper_list.append(paper)

    return paper_list, reader


def fill_readme_template(output_path, content_dict, template_file, dry_run=False):
    template_path = os.path.join(ROOT, template_file)
    with open(template_path, "r") as file:
        template_content = file.read()

    filled_content = template_content.format(**content_dict)

    if not dry_run:
        with open(output_path, "w") as file:
            file.write(filled_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    content_dict = {}

    all_papers = []
    all_paper_data = []
    for d in directory:
        paper_list, paper_data_reader = get_section_list(d)
        content_dict[d] = "\n\n".join(paper_list)
        all_papers.extend(paper_list)
        content_dict["n_" + d] = len(paper_list)

        all_paper_data.extend(paper_data_reader)

    # remove duplicates

    n_unique = len(set(all_papers))

    content_dict["n_papers"] = n_unique

    fill_readme_template("README.md", content_dict, TEMPLATE_FILE, dry_run=args.dry_run)

    # remove duplicate in all_paper_data by Title

    all_paper_data = [dict(t) for t in {tuple(d.items()) for d in all_paper_data}]

    all_paper_data = sorted(all_paper_data, key=lambda x: x["Date"], reverse=True)

    all_papers_data = [
        TEMPLATE.format(row["Title"], row["Url"], row["Date"], row["Author"])
        for row in all_paper_data
    ]

    uncategorized_all_papers = {
        "paper-list": "\n\n".join(all_papers_data),
        "n_papers": n_unique,
    }

    fill_readme_template(
        "README.uncategorized.md",
        uncategorized_all_papers,
        UNCATEGORIZED_TEMPLATE_FILE,
        dry_run=args.dry_run,
    )
