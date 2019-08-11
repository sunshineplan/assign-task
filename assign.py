#!/usr/bin/env python3


import os
from math import ceil, floor
from random import choice, shuffle

import click

here = os.path.abspath(os.path.dirname(__file__))


def get_num(num):
    return eval('{}({})'.format(choice(['ceil', 'floor']), num))


def assign(task, mode):
    try:
        with open(os.path.join(here, 'People_List.txt'), encoding='utf-8') as f:
            people_list = [i.rstrip('\n').strip() for i in f.readlines()]
            people_list = [i for i in people_list if i != '']
            people_list = [i for i in people_list if i[0] != '#']
    except FileNotFoundError:
        print('People_List.txt is missing. Already create it for you.')
        with open(os.path.join(here, 'People_List.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(['Name1', 'Name2', '#Name3', 'Name4']))
        click.pause()
        return

    try:
        per = task//len(people_list)
    except ZeroDivisionError:
        print('People_List.txt has no valid content.')
        click.pause()
        return

    if task % len(people_list):
        print('Total:{}, People:{}, Assign:{}-{}'.format(
            task, len(people_list), per, per+1))
    else:
        print('Total:{}, People:{}, Assign:{}'.format(
            task, len(people_list), per))
    shuffle(people_list)
    result = []
    print_result = []
    while True:
        try:
            num = get_num(task/len(people_list))
            name = people_list.pop(0)
            result += [name] * num
            print_result += ['%s: %s' % (name, num)]
            task -= num
        except ZeroDivisionError:
            break
    if mode == 'random':
        shuffle(result)
    with open(os.path.join(here, 'Result.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))
    print('\n'.join(print_result))
    click.pause()


@click.command(help='Assign task according people list.')
@click.argument('task', required=False, default=0, type=click.IntRange(0))
@click.option('--mode', '-m', default='normal', type=click.Choice(['normal', 'random']), show_default=True, help='Assign task mode.')
def run(task, mode):
    if not task:
        task = click.prompt('Please input total task number',
                            type=click.IntRange(1))
    assign(task, mode)


if __name__ == '__main__':
    run()
