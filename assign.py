#!/usr/bin/env python3

import os
import sys
from math import ceil, floor
from random import choice, shuffle

import click

here = os.path.abspath(os.path.dirname(__file__))


class Assign:
    def __init__(self):
        self._name_list = self.loadNameList()

    def loadNameList(self):
        try:
            with open(os.path.join(here, 'Name_List.txt'), encoding='utf-8') as f:
                name_list = [i.rstrip('\n').strip() for i in f.readlines()]
                name_list = [i for i in name_list if i != '']
                name_list = [i for i in name_list if i[0] != '#']
            if len(name_list) == 0:
                raise ValueError('Empty list.')
        except FileNotFoundError:
            print('Name_List.txt is missing. Already create it for you.')
            with open(os.path.join(here, 'Name_List.txt'), 'w', encoding='utf-8') as f:
                f.write('\n'.join(['Name1', 'Name2', '#Name3', 'Name4']))
            click.pause()
            sys.exit()
        except ValueError:
            click.echo('name_list.txt has no valid content.')
            click.pause()
            sys.exit()
        return name_list


class AssignByName(Assign):
    def __init__(self, total, mode):
        super().__init__()
        self.total = total
        self.mode = mode
        shuffle(self._name_list)
        if total % len(self._name_list):
            click.echo('Total:{}, People:{}, Assign:{}-{}'.format(
                total, len(self._name_list), total//len(self._name_list), total//len(self._name_list)+1))
        else:
            click.echo('Total:{}, People:{}, Assign:{}'.format(
                total, len(self._name_list), total//len(self._name_list)))

    @staticmethod
    def get_num(num):
        return eval('{}({})'.format(choice(['ceil', 'floor']), num))

    def run(self):
        total = self.total
        result = []
        print_result = []
        while True:
            try:
                num = self.get_num(total/len(self._name_list))
                name = self._name_list.pop()
                result += [name] * num
                print_result += ['%s: %s' % (name, num)]
                total -= num
            except ZeroDivisionError:
                break
        if self.mode == 'random':
            shuffle(result)
        with open(os.path.join(here, 'Result.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(result))
        click.echo('\n'.join(print_result))
        click.pause()


@click.command(help='Assign by name.')
@click.argument('total', required=False, default=0, type=click.IntRange(0))
@click.option('--mode', '-m', default='normal', type=click.Choice(['normal', 'random']), show_default=True, help='Assign mode.')
def run(total, mode):
    if not total:
        total = click.prompt('Please input total number',
                             type=click.IntRange(1))
    AssignByName(total, mode).run()


if __name__ == '__main__':
    run()
