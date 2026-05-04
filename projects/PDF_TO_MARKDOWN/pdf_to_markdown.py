import asyncio
import re
from pathlib import Path

try:
    from kreuzberg import extract_file, ExtractionConfig, OutputFormat, ImageExtractionConfig
except ImportError as exc:
    raise ImportError(
        "Knihovna kreuzberg není nainstalovaná. Nainstalujte ji pomocí `pip install kreuzberg`."
    ) from exc

async def main() -> None:
    pdf_path = Path(r"H:\_BIM_MANAGMENT_STUFF\NORMY\EN_ISO_19650-2.pdf")
    output_path = pdf_path.with_suffix(".md")

    config = ExtractionConfig(
        output_format=OutputFormat.MARKDOWN,
        include_document_structure=True,
        images=ImageExtractionConfig(extract_images=True),
    )
    result = await extract_file(pdf_path, config=config)
    output_text = save_extracted_images(output_path, result.content or "", result)

    output_path.write_text(output_text, encoding="utf-8")
    print(f"Saved markdown to: {output_path}")


def save_extracted_images(output_path: Path, markdown_text: str, result):
    if result is None or not getattr(result, "images", None):
        return markdown_text

    image_folder = output_path.parent / output_path.stem
    image_folder.mkdir(parents=True, exist_ok=True)
    saved_names = set()

    for image in result.images:
        if not isinstance(image, dict):
            continue
        fmt = image.get("format", "png")
        idx = image.get("image_index")
        if idx is None:
            idx = len(saved_names)
        file_name = f"image_{idx}.{fmt}"
        file_path = image_folder / file_name
        data = image.get("data") or b""
        file_path.write_bytes(data)
        saved_names.add(file_name)

    def replace_link(match):
        alt_text = match.group(1)
        url = match.group(2).strip()
        base = Path(url).name
        if base in saved_names:
            return f"![{alt_text}]({output_path.stem}/{base})"
        return match.group(0)

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_link, markdown_text)

if __name__ == "__main__":
    asyncio.run(main())