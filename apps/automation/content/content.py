import json
from pathlib import Path


def content_status():
    return "Content module is ready."


def load_research():
    data_file = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "research"
        / "latest.json"
    )

    with open(data_file, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_content(data):
    return {
        "title": "Research Result",
        "summary": (
            f"The researched page returned status {data['status_code']} "
            f"from {data['url']}."
        ),
        "source": data["url"]
    }


def save_content(content):
    output_dir = Path(__file__).resolve().parent.parent / "data" / "content"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "latest.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(content, file, indent=2, ensure_ascii=False)

    return output_file


if __name__ == "__main__":
    research_data = load_research()
    content = generate_content(research_data)
    file_path = save_content(content)

    print("Content generated successfully.")
    print("Saved to:", file_path)
