import os
import sys
import json
import glob
import logging
import datetime
import zipfile

from antioch.core import config

logger = logging.getLogger('antioch.archiver')


def gen_archive_name(num):
    F = config.ARCHIVE_FILENAME

    now = datetime.datetime.utcnow()
    date_str = '%s_%d' % (now.month, now.year)
    arch_name = F % (str(num).zfill(4), date_str)

    logger.info('generated new archive name: ' + arch_name)
    return arch_name


def create_toc(source_folder):
    logger.info('..creating table of contents')
    files = glob.glob(os.path.join(source_folder, '*.json'))
    toc_filepath = os.path.join(source_folder, '_contents.jsonp')

    with open(toc_filepath, 'w') as out_file:
        for f in files:
            d = json.load(open(f, 'r'))
            out_file.write(json.dumps(d) + '\n')
            if config.REMOVE_AFTER_ARCHIVED:
                os.remove(f)
    return toc_filepath


def create_archive(name, source_folder):
    logger.info('creating archive: ' + name)

    arch_name = os.path.join(source_folder, name)
    toc_name = create_toc(source_folder)

    z = zipfile.ZipFile(arch_name, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True)
    z.write(toc_name, arcname=os.path.basename(toc_name))

    if config.REMOVE_AFTER_ARCHIVED:
        os.remove(toc_name)

    for file in glob.glob(os.path.join(source_folder, '*.movie')):
        f_path = os.path.join(source_folder, file)
        logger.info('..adding file ' + f_path)
        z.write(f_path, arcname=os.path.basename(f_path))

        if config.REMOVE_AFTER_ARCHIVED:
            os.remove(f_path)
    z.close()


if __name__ == '__main__':
    if len(sys.argv) == 3:
        archive_number = int(sys.argv[1])
        pickup_folder = sys.argv[2]

    else:
        archive_number = 0
        pickup_folder = config.PICKUP_FOLDER_LOCATION

    if not os.path.exists(pickup_folder):
        raise EnvironmentError(pickup_folder)

    logger.info('bundling movie+json data for archiving')

    create_archive(
        gen_archive_name(archive_number),
        pickup_folder)

    logger.info('done')
