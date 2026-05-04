import asyncio
from pathlib import Path

try:
    from kreuzberg import extract_file, ExtractionConfig
except ImportError as exc:
    raise ImportError(
        "Knihovna kreuzberg není nainstalovaná. Nainstalujte ji pomocí `pip install kreuzberg`."
    ) from exc

async def main() -> None:
    pdf_path = Path(r"H:\_BIM_MANAGMENT_STUFF\NORMY\EN_ISO_19650-2.pdf")
    output_path = pdf_path.with_suffix(".md")

    config = ExtractionConfig()
    result = await extract_file(pdf_path, config=config)
    output_text = result.content or ""

    output_path.write_text(output_text, encoding="utf-8")
    print(f"Saved markdown to: {output_path}")

if __name__ == "__main__":
    asyncio.run(main())