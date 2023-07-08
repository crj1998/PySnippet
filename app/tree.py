"""
Usage:
    tree(Path.home())
ref: https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
"""

from pathlib import Path
from itertools import islice

SPACE =  '    '
BRANCH = '│   '
TEE =    '├── '
LAST =   '└── '

FILE_PREFIX = "📄 "
DIR_PREFIX = "📁 "

def tree(dir_path: Path, level: int=-1, limit_to_directories: bool=False, length_limit: int=1000, skip_hiden_file: bool = True):
    """Given a directory Path object print a visual tree structure"""
    dir_path = Path(dir_path) # accept string coerceable to Path
    files = 0
    directories = 0
    def inner(dir_path: Path, prefix: str='', level=-1):
        nonlocal files, directories
        if not level: 
            return # 0, stop iterating
        contents = [
            d for d in dir_path.iterdir() 
            if not (
                (skip_hiden_file and d.name.startswith(".")) or (limit_to_directories and not d.is_dir())
            )
        ]
        pointers = [TEE] * (len(contents) - 1) + [LAST]
        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                yield prefix + pointer + DIR_PREFIX + path.name
                directories += 1
                extension = BRANCH if pointer == TEE else SPACE 
                yield from inner(path, prefix=prefix+extension, level=level-1)
            elif not limit_to_directories:
                yield prefix + pointer + FILE_PREFIX + path.name
                files += 1
    print(DIR_PREFIX + dir_path.name)
    iterator = inner(dir_path, level=level)
    for line in islice(iterator, length_limit):
        print(line)
    if next(iterator, None):
        print(f'... length_limit, {length_limit}, reached, counted:')
    print(f'\n 🚀 {directories} directories' + (f', {files} files' if files else ''))

if __name__ == "__main__":
    p = Path(__file__).absolute().parent.parent
    tree(p)
    tree(p, limit_to_directories=True, skip_hiden_file=False)
    tree(p, limit_to_directories=True, skip_hiden_file=True)
