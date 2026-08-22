import argparse
import logging
from pathlib import Path

import pandas as pd
import rekordbox_client.dataloading as dataloading
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, Spacer
from song_common.logging_config import setup_logging


def get_rekordbox_xml_path(database_folder: Path, which_version: str) -> Path:
    """Return the selected Rekordbox 7 XML export from a database folder."""
    if which_version != "latest":
        return database_folder / f"rekordbox7_{which_version}.xml"

    xml_files = sorted(database_folder.glob("rekordbox7_*.xml"))
    if not xml_files:
        raise FileNotFoundError(
            f"No Rekordbox 7 XML exports found in '{database_folder}'."
        )
    return xml_files[-1]


def export_track_list_pdf(track_list: pd.DataFrame, output_path: Path) -> None:
    """Write a sorted track list to a paginated PDF table."""
    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Rekordbox track list",
    )
    styles = getSampleStyleSheet()
    table_style = styles["BodyText"].clone("TrackListTable")
    table_style.fontName = "Helvetica"
    table_style.fontSize = 8
    table_style.leading = 10

    table_data = [["Song name", "Artist"]]
    table_data.extend(
        [
            Paragraph(str(track["@Name"]), table_style),
            Paragraph(str(track["@Artist"]), table_style),
        ]
        for _, track in track_list.iterrows()
    )
    table = LongTable(
        table_data,
        colWidths=[105 * mm, 75 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, 0), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9E2F3")),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#F7F9FC")],
            ),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
    )
    document.build([Spacer(1, 2 * mm), table])


def export_track_list(
    database_folder: Path,
    output_folder: Path,
    which_version: str,
    output_format: str,
) -> Path:
    """Export the selected Rekordbox XML track title and artist list."""
    logger = logging.getLogger("rekordbox_maintenance")
    xml_path = get_rekordbox_xml_path(database_folder, which_version)
    track_list = dataloading.load_dataframe_from_rekordbox_xml(str(xml_path))[
        ["@Name", "@Artist"]
    ].sort_values(by=["@Name", "@Artist"])
    output_filename = (
        f"{xml_path.stem.replace('rekordbox7_', 'rekordbox_simple_')}.{output_format}"
    )
    output_path = output_folder / output_filename

    output_folder.mkdir(parents=True, exist_ok=True)
    if output_format == "csv":
        track_list.to_csv(output_path, index=False)
    elif output_format == "xlsx":
        track_list.to_excel(output_path, index=False)
    else:
        export_track_list_pdf(track_list, output_path)

    logger.info("Exported '%s' to '%s'.", xml_path.name, output_path)
    return output_path


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Export a sorted Rekordbox track title and artist list"
    )
    parser.add_argument(
        "--database",
        type=str,
        required=True,
        help="Path to the database folder",
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        required=True,
        help="Path to the output folder",
    )
    parser.add_argument(
        "--version",
        default="latest",
        help="Rekordbox XML date (YYYY-MM-DD), or 'latest' (default)",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "pdf", "xlsx"],
        default="pdf",
        help="Output file format (default: pdf)",
    )
    args = parser.parse_args()

    export_track_list(
        Path(args.database),
        Path(args.output_folder),
        args.version,
        args.format,
    )
