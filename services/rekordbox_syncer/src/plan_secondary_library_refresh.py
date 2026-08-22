# Produce a manual refresh plan for a secondary Rekordbox library by comparing
# its XML snapshot with the primary library XML. Newly added tracks are ignored
# because they are handled by the normal distribution workflow.


# system imports
from argparse import ArgumentParser
import logging
import os

# 3rd party imports
import pandas as pd

# user imports
from song_common.logging_config import setup_logging
import rekordbox_client.dataloading as dataloading


setup_logging()
logger = logging.getLogger(__name__)


def validate_file_path(path: str | None, description: str) -> bool:
    if path and os.path.isfile(path):
        return True

    logger.error(
        "Secondary-library refresh plan was not generated. %s does not exist: %s",
        description,
        path or "<not provided>",
    )
    return False


def plan_refresh_actions(
    primary_snapshot: pd.DataFrame,
    secondary_snapshot: pd.DataFrame,
    comparison_fields: list[str],
    delete_and_reimport_fields: list[str],
) -> None:
    reimport_actions = pd.concat(
        [primary_snapshot, secondary_snapshot], axis=0
    ).drop_duplicates(subset=comparison_fields, keep=False)
    replace_actions = pd.concat(
        [primary_snapshot, secondary_snapshot], axis=0
    ).drop_duplicates(subset=delete_and_reimport_fields, keep=False)

    reimport_actions.drop_duplicates(subset=["@Location"], keep="first", inplace=True)
    replace_actions.drop_duplicates(subset=["@Location"], keep="first", inplace=True)

    reimport_actions["action"] = "REIMPORT"
    replace_actions["action"] = "DELETE & REIMPORT"

    refresh_actions = pd.concat([reimport_actions, replace_actions], axis=0)
    refresh_actions.drop_duplicates(subset=["@Location"], keep="last", inplace=True)

    refresh_actions = refresh_actions.sort_values(
        by="action", inplace=False
    ).reset_index(drop=True)

    logger.info(
        "Found %s refresh actions (excluding new tracks and tracks outside the configured location).",
        len(refresh_actions),
    )
    files_to_remove = []
    for _, row in refresh_actions.iterrows():
        if row["snapshot"] == "secondary":
            files_to_remove.append(row)
        else:
            logger.info(f"Please {row['action']} {row['@Name']} - {row['@Artist']}")

    logger.info(
        f"Found {len(files_to_remove)} files that should be missing within rekordbox:"
    )
    for row in files_to_remove:
        logger.info(f"Please DELETE {row['@Name']} - {row['@Artist']}")


def validate_config(config: dict) -> bool:
    required_keys = {
        "primary_xml",
        "secondary_xml",
        "location_prefix",
        "ignore_new_tracks",
        "comparison_fields",
        "delete_and_reimport_fields",
    }
    missing_keys = sorted(required_keys.difference(config))
    if missing_keys:
        logger.error(
            "Secondary-library refresh plan was not generated. Missing configuration keys: %s",
            ", ".join(missing_keys),
        )
        return False

    fields_to_load = config["comparison_fields"] + config["delete_and_reimport_fields"]
    if "@Location" not in fields_to_load:
        logger.error(
            "Secondary-library refresh plan was not generated. '@Location' must be included in the configured fields."
        )
        return False

    if config["ignore_new_tracks"] and "@DateAdded" not in fields_to_load:
        logger.error(
            "Secondary-library refresh plan was not generated. '@DateAdded' is required when ignore_new_tracks is enabled."
        )
        return False

    return True


def validate_snapshot_fields(
    snapshot: pd.DataFrame, fields: list[str], description: str
) -> bool:
    missing_fields = sorted(set(fields).difference(snapshot.columns))
    if missing_fields:
        logger.error(
            "Secondary-library refresh plan was not generated. %s is missing fields: %s",
            description,
            ", ".join(missing_fields),
        )
        return False

    return True


def main(args) -> bool:
    if not validate_file_path(args.config, "Configuration file"):
        return False

    config = dataloading.load_yaml(args.config)
    if not validate_config(config):
        return False

    primary_xml_path = config["primary_xml"]
    secondary_xml_path = config["secondary_xml"]
    if not validate_file_path(primary_xml_path, "Primary XML file"):
        return False
    if not validate_file_path(secondary_xml_path, "Secondary XML file"):
        return False

    logger.info("Start of program: plan_secondary_library_refresh.py...")
    logger.info(
        "Comparing primary XML %s with secondary XML %s",
        primary_xml_path,
        secondary_xml_path,
    )
    primary_snapshot = dataloading.load_dataframe_from_rekordbox_xml(primary_xml_path)
    secondary_snapshot = dataloading.load_dataframe_from_rekordbox_xml(
        secondary_xml_path
    )

    fields_to_load = list(
        dict.fromkeys(
            config["comparison_fields"] + config["delete_and_reimport_fields"]
        )
    )
    if not validate_snapshot_fields(primary_snapshot, fields_to_load, "Primary XML"):
        return False
    if not validate_snapshot_fields(
        secondary_snapshot, fields_to_load, "Secondary XML"
    ):
        return False

    primary_snapshot = primary_snapshot[fields_to_load]
    secondary_snapshot = secondary_snapshot[fields_to_load]

    if config["ignore_new_tracks"]:
        newest_secondary_date = secondary_snapshot.sort_values(
            by="@DateAdded", ascending=False
        )["@DateAdded"].iloc[0]
        len_before = len(primary_snapshot)
        primary_snapshot = primary_snapshot[
            primary_snapshot["@DateAdded"] <= newest_secondary_date
        ]
        if len_before != len(primary_snapshot):
            logger.warning(
                "Excluded %s new primary tracks from the refresh plan.",
                len_before - len(primary_snapshot),
            )

    primary_snapshot = primary_snapshot[
        primary_snapshot["@Location"].str.startswith(config["location_prefix"])
    ]
    if primary_snapshot.empty:
        logger.error(
            "Secondary-library refresh plan was not generated. No primary tracks match the configured location prefix."
        )
        return False

    secondary_in_scope = secondary_snapshot[
        secondary_snapshot["@Location"].str.startswith(config["location_prefix"])
    ]
    if len(secondary_in_scope) != len(secondary_snapshot):
        logger.error(
            "Secondary-library refresh plan was not generated. All secondary tracks must use the configured location prefix."
        )
        return False

    primary_snapshot["snapshot"] = "primary"
    secondary_snapshot["snapshot"] = "secondary"

    plan_refresh_actions(
        primary_snapshot,
        secondary_snapshot,
        config["comparison_fields"],
        config["delete_and_reimport_fields"],
    )

    logger.info("End of program: plan_secondary_library_refresh.py\n")
    return True


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Plan a manual refresh of a secondary Rekordbox library"
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Path to the secondary-library refresh configuration YAML file",
    )

    args = parser.parse_args()
    if not main(args):
        raise SystemExit(1)
