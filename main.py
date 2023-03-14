import datetime
import logging
import multiprocessing
import pathlib
import shutil
import time

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


def get_files(root_dir: str, log_file_path: pathlib.Path) -> dict:
    all_files = {}
    for path in pathlib.Path(root_dir).rglob('*'):
        if path.is_file():
            all_files[path] = path.stat().st_mtime
            with log_file_path.open('a', encoding='utf-8') as a:
                print(f"{path}|{all_files[path]:.6f}", file=a)
    return all_files


def compare_log(doc_name: str, setup_file_path: pathlib.Path) -> list:
    with setup_file_path.open('r', encoding='utf-8') as r:
        my_dir2 = dict(row.strip().split('|') for row in r)
    with pathlib.Path(f'./log/IO-{doc_name}.txt').open('r', encoding='utf-8') as r:
        my_dir = dict(row.strip().split('|') for row in r)
    diff = set(my_dir.keys()) ^ set(my_dir2.keys())
    return [k for k in diff if k not in my_dir or k not in my_dir2 or my_dir2[k] != my_dir[k]]


def ay_copy(args):
    from_path, to_path = args
    shutil.copy(from_path, to_path)
    logging.info(f"{from_path.name} copied")


def copy_files(to_path: str, from_path: str, update_dir: list, doc_name: str, pool_size: int = 5) -> None:
    pool = multiprocessing.Pool(processes=pool_size)
    for item in update_dir:
        dest_path = to_path + '/' + str(pathlib.Path(item).relative_to(from_path).parent)
        pathlib.Path(dest_path).mkdir(parents=True, exist_ok=True)
        pool.apply_async(ay_copy, ((item, dest_path),))
    pool.close()
    pool.join()
    log_file_path = pathlib.Path(f'./log/IO-{doc_name}.txt')
    if log_file_path.exists():
        log_file_path.unlink()
    shutil.copy(setup_file_path, setup_file_path.parent / f'IO-{doc_name}.txt')


if __name__ == "__main__":
    try:
        logging.info('Sync started!')
        pathlib.Path('./log').mkdir(exist_ok=True)
        disk_lst = {
            # 'Keyence': [pathlib.Path('//10.178.14.150/Documents'),
            #             pathlib.Path('//10.54.5.130/atmo3_project_customer$/7_PAO5/07_Lab_Data/Keyence')],
            'HFK': [pathlib.Path('//10.178.14.151/HFK_folder'),r'C:\Users\wqa7szh\Desktop\new_project\test']
                    # '//1pathlib.Path(0.54.5.130/atmo3_project_customer$/7_PAO5/07_Lab_Data/HFK'],
            # 'ATMO3-A': [pathlib.Path('//10.178.14.250/ApplicationData'),
            #             pathlib.Path('//10.54.5.130/atmo3_project_customer$/7_PAO5/03_Production/300_'
            #                          'Production_Files/50_trend_check/ATMO3-A/ApplicationData')],
            # 'ATMO3-B': [pathlib.Path('//10.178.14.249/ApplicationData'),
            #             pathlib.Path('//10.54.5.130/atmo3_project_customer$/7_PAO5/03_Production/300_'
            #                          'Production_Files/50_trend_check/ATMO3-B')],
            # 'ATMO3-C': [pathlib.Path('//10.178.14.245/ApplicationData'),
            #             pathlib.Path('//10.54.5.130/atmo3_project_customer$/7_PAO5/03_Production/300_'
            #                          'Production_Files/50_trend_check/ATMO3-C')]
        }  # 你需要根据实际情况修改
        for key, (from_path, to_path) in disk_lst.items():
            setup_filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            setup_file_path = pathlib.Path(f'./log/{setup_filename}.txt')
            setup_file_path.touch()
            logging.info(f"Start syncing {key}")
            all_files = get_files(from_path, setup_file_path)
            logging.info('Files scanned!')
            logging.info('Start comparing!')
            update_dir = compare_log(key, setup_file_path)
            logging.info('Comparison finished!')
            logging.info('Start copying!')
            copy_files(to_path, from_path, update_dir, key)
            logging.info('Sync finished!')
            time.sleep(5)
    except Exception as ex:
        logging.exception(f'{ex}')
        time.sleep(5)
