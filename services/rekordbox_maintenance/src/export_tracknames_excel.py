# system imports
import argparse
import logging
import os

# private library imports
from song_common.logging_config import setup_logging
import rekordbox_client.dataloading as dataloading


def main(database_folder: str, output_folder: str, which_version: str) -> None:
    """this function assumes, that the rekordbox database has all the xml files in the following format:
    `rekordbox7_YYYY-MM-DD.xml`
    """
    logger = logging.getLogger("rekordbox_maintenance")
    logger.setLevel(logging.INFO)

    if which_version == "latest":
        file_of_interest = sorted(
            f
            for f in os.listdir(database_folder)
            if f.startswith("rekordbox7_") and f.endswith(".xml")
        )[-1]
    else:
        file_of_interest = f"rekordbox7_{which_version}.xml"

    df = dataloading.load_dataframe_from_rekordbox_xml(
        os.path.join(database_folder, file_of_interest)
    )

    # preparing the outfilename
    filenamesplit = file_of_interest.split(".")[0].split("_")
    outfilename = filenamesplit[0] + "_simple_" + filenamesplit[-1] + ".xlsx"

    # saving to excel
    df[["@Name", "@Artist"]].sort_values(
        by=[
            "@Name",
            "@Artist",
        ]
    ).to_excel(os.path.join(output_folder, outfilename), index=False)
    logger.info(f"Successfully exported '{file_of_interest}' to excel file")


if __name__ == "__main__":
    setup_logging()

    ################## step 0 ##################
    parser = argparse.ArgumentParser(
        description="Export Rekordbox track names to Excel"
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
    args = parser.parse_args()

    database_folder = args.database
    output_folder = args.output_folder

    main(database_folder, output_folder, args.version)
