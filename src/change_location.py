# This script changes the location from an 
# "old location" (specified as a program argument with the -o flag) to a
# "new locaiton" (specified as a program argument with the -n flag) of the tracks in the 
# rekordbox.xml file (filepath specified as a program argument with the -r flag) and saves it to a 
# new location (out filepath specified as a program argument with the -p flag). 

# system imports
from argparse import ArgumentParser

# user imports
from RB_handler import RB_handler


def main(args):
    # instantiating the RB Handler and giving him the name benny ;)
    benny = RB_handler(args.path_to_rb)

    if args.old_location == '' or args.new_location == '':
        raise ValueError(
            'Please provide a location where the tracks are stored and where you want them to be stored.')

    # changing the tracks location
    benny.change_tracks_source_path(old_location=args.old_location,
                                    new_location=args.new_location)

    # saving the changed xml
    benny.export_data_to_xml(out_path=args.save_location)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-r', '--path_to_rb', default='')
    parser.add_argument('-o', '--old_location', default='')
    parser.add_argument('-n', '--new_location', default='')
    parser.add_argument('-p', '--save_location', default='')

    args = parser.parse_args()
    main()
