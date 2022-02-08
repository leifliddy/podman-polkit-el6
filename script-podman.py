#!/usr/bin/python3

import argparse
import dbus
import os
import rpm
import subprocess
import sys
from podman import PodmanClient
from termcolor import cprint


centos_release = '6'

image_name         = f'polkit_rpmbuild_env:{centos_release}'
container_name     = f'polkit_builder_{centos_release}'
container_hostname = 'polkit_builder'
container_script   = '/root/01.copy.rpms.to.output_rpm.sh'


def print_yes():
    cprint(' [YES]', 'green')


def print_no():
    cprint(' [NO]', 'red')


def print_soft_no():
    cprint(' [NO]', 'yellow', attrs=['bold','dark'])


def print_success():
    cprint(' [SUCCESS]', 'green')


def print_failure():
    cprint(' [FAILURE]', 'red')


def print_debug(msg, cmd):
    cprint(f'DEBUG: {msg}:', 'yellow')
    cprint('run:', 'magenta', attrs=['bold', 'dark'])
    cprint(f'{cmd}\n', 'yellow', attrs=['bold'])


def check_podman_installed():
    cprint('{0:.<70}'.format('PODMAN: is podman installed'), 'yellow', end='')
    podman_instprint_noalled = False
    ts = rpm.TransactionSet()
    rpm_listing = ts.dbMatch()

    for rpm_pkg in rpm_listing:
        if rpm_pkg['name'] == 'podman':
            podman_installed = True

    if podman_installed:
        print_yes()
    else:
        print_no()
        cprint('\npodman is not installed', 'magenta')
        cprint('Exiting...', 'red')
        sys.exit(1)


def ensure_podman_socket_running():
    if os.geteuid() == 0:
        bus = dbus.SystemBus()
    else:
        bus = dbus.SessionBus()

    systemd = bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
    manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')
    service = 'podman.socket'

    try:
       manager.RestartUnit(service, 'fail')
    except:
       cprint('Error: Failed to start {}.'.format(service), 'red')
       cprint('Exiting...', 'red')
       sys.exit(2)


def ensure_image_exists():
    cprint('{0:.<70}'.format('PODMAN: checking if image exists'), 'yellow', end='')
    podman_image = client.images.list(filters = { 'reference' : image_name})

    if podman_image:
        print_yes()
    else:
        print_soft_no()
        cprint('PODMAN: building image...', 'yellow')
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        podman_cmd_str = f'podman build --squash -t {image_name} .'
        podman_cmd = podman_cmd_str.split()

        if args.debug:
            print_debug('to manually build the image', podman_cmd_str)

        # using the api function will hide the build process which would make it difficult to identify any potential build-related issues
        #client.images.build(path=cur_dir, tag=podman_image, squash=True, rm=True)

        cmd_output = subprocess.run(podman_cmd, universal_newlines=True)

        cprint('{0:.<70}'.format('PODMAN: build image'), 'yellow', end='')

        if cmd_output.returncode != 0:
            print_failure()
            cprint('Exiting...', 'red')
            sys.exit(3)
        else:
            print_success()


def ensure_image_removed():
    cprint('{0:.<70}'.format('PODMAN: checking if image exists'), 'yellow', end='')
    podman_image_exists = client.images.list(filters = { 'reference' : image_name})

    if podman_image_exists:
        print_yes()
        cprint('PODMAN: removing image...', 'yellow')
        print_debug('to manually remove the image', f'podman rmi {image_name}')
        client.images.remove(image=image_name)
    else:
        print_soft_no()


def ensure_container_exists_and_running(interactive):
    cprint('{0:.<70}'.format('PODMAN: checking if container exists'), 'yellow', end='')
    container_exists = client.containers.list(all=True, filters = { "name" : container_name})

    if container_exists:
        print_yes()
        podman_container = client.containers.get(container_name)
        container_status = podman_container.status

        cprint('{0:.<70}'.format('PODMAN: checking if container is running'), 'yellow', end='')

        if container_status == 'running':
            print_yes()
        else:
            print_soft_no()
            cprint('PODMAN: starting container...', 'yellow')
            if args.debug:
                print_debug('to manually start the container', f'podman start {container_name}')
            podman_container.start()
            ensure_container_exists_and_running(interactive)
    else:
        print_soft_no()
        run_container(interactive)
        if interactive:
            ensure_container_exists_and_running(interactive)


def create_mounts_dict(host_mount, container_mount):
    mounts = {
               'type':   'bind',
               'source': host_mount,
               'target': container_mount,
             }

    return mounts


def ensure_container_stopped_removed(remove_container=True):
    cprint('{0:.<70}'.format('PODMAN: checking if container exists'), 'yellow', end='')
    container_exists = client.containers.list(all=True, filters = {'name' : container_name})

    if container_exists:
        print_yes()
        podman_container = client.containers.get(container_name)
        container_status = podman_container.status

        cprint('{0:.<70}'.format('PODMAN: checking if container is running'), 'yellow', end='')

        if container_status != 'exited':
            print_yes()
            cprint('PODMAN: stopping container...', 'yellow')
            if args.debug:
                print_debug('to manually stop the container', f'podman stop {container_name}')
            podman_container.stop()
        else:
            print_soft_no()

        if remove_container:
            cprint('PODMAN: removing container...', 'yellow')
            if args.debug:
                print_debug('to manually remove the container', f'podman rm {container_name}')
            podman_container.remove()

    else:
        print_soft_no()


def run_container(interactive):
    cprint('PODMAN: run container...', 'yellow')
    bind_volumes          = []
    cur_dir               = os.path.dirname(os.path.realpath(__file__))
    output_dir_host       = cur_dir + '/output_rpm'
    output_dir_container  = '/output_rpm'

    bind_volumes.append(create_mounts_dict(output_dir_host, output_dir_container))

    if interactive:
        if args.debug:
            podman_run_cmd_manual = f'podman run -d -it --privileged=true -v $(pwd)/output_rpm:/output_rpm -h {container_hostname} --name {container_name} {image_name}'
            print_debug('to manually run the container', podman_run_cmd_manual)

        client.containers.run(image=image_name, name=container_name, hostname=container_hostname, detach=True, tty=True, privileged=True, mounts=bind_volumes)

    else:
        if args.debug:
            podman_run_cmd_manual = f'podman run -d --rm --privileged=true -v $(pwd)/output_rpm:/output_rpm -h {container_hostname} --name {container_name} {image_name} {container_script}'
            print_debug('to manually run the container', podman_run_cmd_manual)

        client.containers.run(image=image_name, name=container_name, hostname=container_hostname, detach=True, auto_remove=True, privileged=True, mounts=bind_volumes, command=container_script)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('--auto',
                        action='store_true',
                        help='ensure image is built, start a non-interactive container, run script, exit',
                        default=False)
    parser.add_argument('--debug',
                        action='store_true',
                        help='display debug messages',
                        default=False)
    group.add_argument('--rebuild',
                        action='store_true',
                        help='remove podman image and container if they exist, '
                             'then build (new) podman image and run container',
                        default=False)
    group.add_argument('--rm_image',
                        action='store_true',
                        help='remove podman image and container if they exist',
                        default=False)
    group.add_argument('--rm_container',
                        action='store_true',
                        help='remove container if it exists',
                        default=False)
    group.add_argument('--stop_container',
                        action='store_true',
                        default=False)

    args = parser.parse_args()


    check_podman_installed()
    ensure_podman_socket_running()
    client = PodmanClient()

    if args.auto:
        interactive = False
    else:
        interactive = True

    if args.rm_image:
        ensure_container_stopped_removed()
        ensure_image_removed()
        sys.exit()

    if args.rm_container:
        ensure_container_stopped_removed()
        sys.exit()

    if args.stop_container:
        ensure_container_stopped_removed(remove_container=False)
        sys.exit()

    if args.rebuild:
        ensure_container_stopped_removed()
        ensure_image_removed()

    if not interactive and not args.rebuild:
        ensure_container_stopped_removed()


    cprint('{0:.<70}'.format('PODMAN: image name'), 'yellow', end='')
    cprint(f' {image_name}', 'cyan')

    ensure_image_exists()

    cprint('{0:.<70}'.format('PODMAN: container name'), 'yellow', end='')
    cprint(f' {container_name}', 'cyan')

    ensure_container_exists_and_running(interactive)

    if interactive:
        cprint('PODMAN: to login to the container run:', 'yellow')
        cprint(f'podman exec -it {container_name} /bin/bash\n', 'green')
    else:
        cprint(f'PODMAN: running command {container_script}', 'yellow')
