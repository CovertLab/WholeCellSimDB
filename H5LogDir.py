import argparse
import H5Logger 

def main():
    parser = argparse.ArgumentParser(description='Stuff')
    parser.add_argument('-d', '--directory',
                        help='Directory of WCS output files.',
                        required=True)
    parser.add_argument('-o', '--output',
                        help='HDF5 output filename.',
                        required=True)
    args = parser.parse_args()

    print H5Logger.log_dir(args.directory, args.output)

if __name__=="__main__":
    main()
