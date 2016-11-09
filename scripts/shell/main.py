import os
import click

@click.group()
def shell():
    pass


@shell.command()
@click.option('--abs', default=False, help='is absolute path or not,default in current path')
@click.argument('path')
def mkdir(abs, path):
    '''make a dirctory
    '''
    path = path.strip()
    # get rid of '\' in header
    path = path.rstrip("\\")
    #  get rid of '\' in footer
    if abs:
        # determin whether the path exists
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
    else:
        os.makedirs(os.getcwd() + '/' + path)

@shell.command()
@click.option('--abs', default=False, help='is absolute path or not,default in current path')
@click.option('--f/--force', default=False, help='remove dir even if it\'s not empty')
@click.argument('path')
def rmdir(abs, f, path):
    '''
    remove a dirctory, force optional
    '''
    if not os.path.isdir(path):
        click.echo(path + ' is not a directory')
    else:
        if not f:
            if os.listdir(path):  # path is not empty
                click.echo('directory ' +
                           path + ' is not empty, but you can force to remove by --f/--force=True')
                return
            else:
                os.rmdir(path)
        else:  # force to remove even if it's not empty
            import shutil
            shutil.rmtree(path)

'''
move a file or directory to another place
'''


@shell.command()
@click.argument('src')
@click.argument('dest')
def mv(src, dest):
    import shutil
    shutil.move(src, dest)

'''
get resources in current directory
'''


@shell.command()
@click.option('--a/--all', default=False, help='how to show resources in current directory')
def ls(a):
    click.echo(os.listdir(os.getcwd()))

'''
make a file by name
'''


@shell.command()
@click.argument('file')
def touch(file):
    from pathlib import Path
    try:
        Path(file).touch()
    except FileNotFoundError as e:
        click.echo('directory doesn\'t exist')
        return

'''
rename a file or directory
'''


@shell.command()
@click.argument('target')
@click.argument('newname')
def rename(target, newname):
    if not os.path.exists(target):
        raise FileNotFoundError(target+' dosen\'t exist')

    os.rename(target, os.path.dirname(target)+os.sep+newname)

'''
cat a file content 
'''


@shell.command()
@click.argument('file')
def cat():
    return

'''
rm a file
'''


@shell.command()
@click.argument('file')
def rm(file):
    if not os.path.exists(file):
        click.echo(file + ' doesn\'t exsit')
        return
    elif os.path.isdir(file):
        click.echo(file + ' is a directory,use "rmdir" instead please')
        return
    else:
        os.remove(file)

'''
copy a file or directory to another place
'''


@shell.command()
@click.argument('src')
@click.argument('dest')
def cp(src, dest):
    # get rid of '\' in header
    src = src.strip()
    #  get rid of '\' in footer
    src = src.rstrip(os.sep)
    dest = dest.rstrip(os.sep)
    if not os.path.exists(src):
        raise FileNotFoundError(src + ' doesn\'t exist')
        return

    srcname = os.path.basename(src)
    if os.path.exists(dest):
        if os.path.isdir(dest):
            destname = dest + os.sep + srcname

            if os.path.exists(destname):
                click.echo('dest directory ' + dest +
                           ' has a file or directory named ' + srcname)
                return
            else:
                dest = destname

            doCopy(src, dest)
        else:
            click.echo(dest + ' exsits')
            return
    else:
        doCopy(src, dest)

def doCopy(src, dest):
    import shutil
    if os.path.isdir(src):
        shutil.copytree(src, dest)
    else:
        shutil.copyfile(src, dest)

'''get the size of a file 
in human friendly way'''


@shell.command()
@click.argument('file')
def size(file):
    click.echo(os.path.getsize(file))
