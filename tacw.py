#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

"""
Coleta informacoes do Tracksale e do chat Orbium para realizar o Tag Cloud no Kibana.
"""

import datetime
import json
import argparse
import configparser
import os
import sys
import logging
import pymysql
import requests

CONFIG_FILE = '.env.ini'

parser = argparse.ArgumentParser(description='Coleta informacoes do Tracksale e do Atende.')

if not os.path.exists(CONFIG_FILE):
    parser.add_argument('-c', '--config', metavar='<config file>', help='', required=True)
    args = parser.parse_args()
    CONFIG_FILE = args.config


def config_parser(section):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if config.has_section(section):
        items_dict = dict(config.items(section))
        return items_dict
    else:
        print(f'Section {section} doesnt exists')
        sys.exit(1)


def log_define(path_file, loglevel):
    logging.basicConfig(filename=path_file, format='%(asctime)s %(levelname)-8s %(message)s', level=loglevel)
    return logging


config_tracksale = config_parser('tracksale')
config_atende = config_parser('atende')
logger_config = config_parser('logging')
log = log_define(logger_config['file'], logger_config['level'])


def atende_get_comments(host, database, user, password, date):
    query = f"SELECT reclamacao_id, usr_id, origem_id, tipo_id, departamento_id, nome, email, telefone, " \
            f"mensagem, procede, status_id " \
            f"FROM reclamacao " \
            f"WHERE data_cadastro " \
            f"BETWEEN '{date} 00:00:00' AND '{date} 23:59:59'"
    with pymysql.connect(host=host, user=user, password=password, db=database).cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def tracksale_get_comments(url, date):
    url_comments = url + '?start={0}&end={0}'.format(date)
    result = requests.get(url_comments, timeout=10).json()
    return result


def tracksale_get_metrics(url, date):
    url_metrics = url + '?start={0}&end={0}'.format(date)
    result = requests.get(url_metrics, timeout=10).json()
    return result


def main():
    date = datetime.datetime.now()

    """Parser and add new comments with split"""
    date_yesterday_track = (date - datetime.timedelta(days=1)).strftime('%d/%m/%Y')

    try:
        comments_tracksale = tracksale_get_comments(config_tracksale['comments'], date_yesterday_track)
    except Exception as error:
        log.error("Error to get comments from Tracksale: {}".format(error))
        sys.exit(1)

    new_comments_tracksale = comments_tracksale
    for info_per_user in comments_tracksale:
        for tag in list(info_per_user.keys()):

            if tag == 'nps_comment' and info_per_user[tag] not in ['None', None]:
                index = comments_tracksale.index(info_per_user)
                comment = info_per_user[tag].replace(',', '').replace('.', '')
                new_comments_tracksale[index]['comment_split'] = comment.split()

    print(json.dumps(new_comments_tracksale))

    """Parser and split comments from chat orbium (Atende)"""
    date_yesterday_atende = (date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    try:
        comments_atende = atende_get_comments(config_atende['host'], config_atende['db'], config_atende['user'], config_atende['pass'], date_yesterday_atende)
    except Exception as error:
        log.error("Error to get comments from Atende: {}".format(error))
        sys.exit(1)

    new_comments_atende = list()
    for reclamacao_id, usr_id, origem_id, tipo_id, departamento_id, nome, email, telefone, mensagem, procede, status_id in comments_atende:
        comment_split = mensagem.decode('latin-1', 'ignore').replace(',', '').replace('.', '').split()

        new_comments_atende.append({'usr_id': usr_id, 'origem_id': origem_id, 'tipo_id': tipo_id,
                                    'departamento_id': departamento_id, 'nome': nome, 'email': email,
                                    'telefone': telefone, 'comment_split': comment_split,
                                    'procede': procede, 'status_id': status_id})

    print(json.dumps(new_comments_atende))


if __name__ == '__main__':
    main()
