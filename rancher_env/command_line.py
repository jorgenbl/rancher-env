import rancher_env
import argparse

def main(args):

    rancher_env.make_confdir()

    if args.list_all_env:
        rancher_env.list_all_environments()
    if args.list_all_conf:
        rancher_env.list_configs()
    if args.new_config:
        rancher_env.create_config(new_config)
    elif args.new_config == "":
        rancher_env.create_config(new_config)
    if args.switch_config:
        rancher_env.switch_config(switch_config)
    elif args.switch_config == "":
        print("Please enter the config to switch to")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-nc', '--new_config', help='Save current config', default="")
    parser.add_argument('-lc', '--list-all-conf',
                        help='List all configs',
                        action='store_true', default=False)
    parser.add_argument('-le', '--list-all-env',
                        help='List all environments from all configs',
                        action='store_true', default=False)
    parser.add_argument('-sc', '--switch-config',
                        help='Specify the config to switch to')
    args = parser.parse_args()

    main(args)