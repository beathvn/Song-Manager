# This script checks for duplicates in your rekordbox xml file.
# Pass the path to your rekordbox.xml file as a program argument with the -p flag.


# system imports
from argparse import ArgumentParser

# user imports
import helpers.dataloading as dataloading
import helpers.utils as utils


def main(args):
    filepath = args.path_to_xml

    if filepath is None:
        raise ValueError(
            'Please provide a valid .xml filepath to your rekordbox database as a program argument!')

    data = dataloading.load_dataframe_from_rekordbox_xml(filepath)

    # searching for duplicates
    results = data['@Location'].duplicated()

    # printing the names of the duplicated songs
    duplicate_songnames = []
    for index, result in enumerate(results):
        if result:
            duplicate_songnames.append(data.iloc[index]['@Name'])

    if len(duplicate_songnames) != 0:
        print(
            f'🚨 {len(duplicate_songnames)} TRACKS WHERE FOUND pointing to the same file on your harddisk:')
        utils.print_divider()
        for currsong in duplicate_songnames:
            print('- ' + currsong)
        utils.print_divider()
    else:
        print('✅ No songs appearing more than once were found.')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-p', '--path_to_xml')
    args = parser.parse_args()

    main(args)
