from argparse import ArgumentParser

from democonverter.demo import Demo


def main():
    # sys.tracebacklimit = 0

    parser = ArgumentParser(
        prog='democonverter',
        description='Convert Aftershock demo to WolfcamQL friendly demo.',
        epilog='Created by ldrone (2024-04-21)',
    )

    parser.add_argument('demos', nargs='*', help='Input demo(s)')
    parser.add_argument(
        '-i', '--info', action='store_true', help='Show info without converting demo.'
    )
    parser.add_argument('-o', '--output', help='Output directory. Default is "out"')

    args = parser.parse_args()
    for demo in args.demos:
        Demo(demo).read(not args.info, args.output)


if __name__ == '__main__':
    main()
