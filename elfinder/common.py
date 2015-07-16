import os
import urllib
import hashlib
import mimetypes
from datetime import datetime

from PIL import Image

OPTIONS = {
    'root': '',
    'URL': '',
    'rootAlias': 'Home',
    'dotFiles': False,
    'dirSize': True,
    'fileMode': 0o644,
    'dirMode': 0o755,
    'imgLib': 'auto',
    'tmbDir': '.tmb',
    'tmbAtOnce': 5,
    'tmbSize': 48,
    'fileURL': True,
    'uploadMaxSize': 256,
    'uploadWriteChunk': 8192,
    'uploadAllow': [],
    'uploadDeny': [],
    'uploadOrder': ['deny', 'allow'],
    # 'aclObj': None, # TODO
    # 'aclRole': 'user', # TODO
    'defaults': {
        'read': True,
        'write': True,
        'rm': True
    },
    'perms': {},
    'archiveMimes': {},
    'archivers': {
        'create': {},
        'extract': {}
    },
    'disabled': [],
    'debug': False
}

MIME_TYPE = {
    'txt': 'text/plain',
    'conf': 'text/plain',
    'ini': 'text/plain',
    'php': 'text/x-php',
    'html': 'text/html',
    'htm': 'text/html',
    'js': 'text/javascript',
    'css': 'text/css',
    'rtf': 'text/rtf',
    'rtfd': 'text/rtfd',
    'py': 'text/x-python',
    'java': 'text/x-java-source',
    'rb': 'text/x-ruby',
    'sh': 'text/x-shellscript',
    'pl': 'text/x-perl',
    'sql': 'text/x-sql',
    # apps
    'doc': 'application/msword',
    'ogg': 'application/ogg',
    '7z': 'application/x-7z-compressed',
    # video
    'ogm': 'appllication/ogm',
    'mkv': 'video/x-matroska'
}


class ElfinderException(Exception):
    pass


def merge_dict(*args):
    result = []
    for dict_obj in args:
        result = result + list(dict_obj.items())
    return dict(result)


class BaseCommands(object):

    def get_content(self, path, tree):
        """CWD + CDC + maybe(TREE)"""
        response = {}
        response['cwd'] = self.__cwd(path)
        response['cdc'] = self.__cdc(path)

        if tree:
            response['tree'] = self.__tree(self.options['root'])
        return response

    def __cwd(self, path):
        """
        Current Working Directory
        """
        root = self.options['root']
        rootAlias = self.options['rootAlias']
        if path == root:
            rm = False
            name = rootAlias
        else:
            rm = True
            name = os.path.basename(path)

        if rootAlias:
            basename = rootAlias
        else:
            basename = os.path.basename(root)

        rel = basename + path[len(root):]

        return {
            'hash': self.__hash(path),
            'name': name,
            'mime': 'directory',
            'rel': rel,
            'size': 0,
            'date': datetime.fromtimestamp(
                os.stat(path).st_mtime
            ).strftime("%d %b %Y %H:%M"),
            'read': True,
            'write': self._isAllowed(path, 'write'),
            'rm': rm and self._isAllowed(path, 'rm')
        }

    def __cdc(self, path):
        """
        Current Directory Content
        """
        files = []
        dirs = []

        for f in sorted(os.listdir(path)):
            if not self._isAccepted(f):
                continue
            pf = os.path.join(path, f)
            info = {}
            info = self.__info(pf)
            info['hash'] = self.__hash(pf)
            if info['mime'] == 'directory':
                dirs.append(info)
            else:
                files.append(info)

        dirs.extend(files)
        return dirs

    def __hash(self, path):
        """
        Hash of the path
        """
        if not path:
            return None
        m = hashlib.md5()
        try:
            path = path.encode('utf-8')
        except UnicodeDecodeError:
            pass
        m.update(path)
        return str(m.hexdigest())

    def _findDir(self, fhash, path):
        """Find directory by hash"""
        fhash = str(fhash)
        if not path:
            path = self.options['root']
            if fhash == self.__hash(path):
                return path

        if not os.path.isdir(path):
            return None

        for d in os.listdir(path):
            pd = os.path.join(path, d)
            if os.path.isdir(pd) and not os.path.islink(pd):
                if fhash == self.__hash(pd):
                    return pd
                else:
                    ret = self._findDir(fhash, pd)
                    if ret:
                        return ret
        return None

    def __mimetype(self, path):
        """Detect mimetype of file"""
        mime = mimetypes.guess_type(path)[0] or 'unknown'
        ext = path[path.rfind('.') + 1:]

        if mime == 'unknown' and ('.' + ext) in mimetypes.types_map:
            mime = mimetypes.types_map['.' + ext]

        if mime == 'text/plain' and ext == 'pl':
            mime = MIME_TYPE[ext]

        if mime == 'application/vnd.ms-office' and ext == 'doc':
            mime = MIME_TYPE[ext]

        if mime == 'unknown':
            if os.path.basename(path) in ['README', 'ChangeLog']:
                mime = 'text/plain'
            else:
                if ext in MIME_TYPE:
                    mime = MIME_TYPE[ext]
        return mime

    def __path2url(self, path):
        curDir = path
        length = len(self.options['root'])
        url = self.options['URL'] + curDir[length:]
        url = url.replace(os.sep, '/')
        return getattr(urllib, 'request', urllib).quote(url, '/:~')

    def __getImgSize(self, path):
        im = Image.open(path)
        return str(im.size[0]) + 'x' + str(im.size[1])

    def __dirSize(self, path):
        total_size = 0
        if self.options['dirSize']:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.stat(fp).st_size
        else:
            total_size = os.lstat(path).st_size
        return total_size

    def __tree(self, path):
        """
        Return directory tree starting from path
        """

        if not os.path.isdir(path):
            return ''
        if os.path.islink(path):
            return ''

        if path == self.options['root'] and self.options['rootAlias']:
            name = self.options['rootAlias']
        else:
            name = os.path.basename(path)
        tree = {
            'hash': self.__hash(path),
            'name': name,
            'read': self._isAllowed(path, 'read'),
            'write': self._isAllowed(path, 'write'),
            'dirs': []
        }

        if self._isAllowed(path, 'read'):
            for d in sorted(os.listdir(path)):
                pd = os.path.join(path, d)
                if (
                        os.path.isdir(pd) and
                        not os.path.islink(pd) and
                        self._isAccepted(d)
                ):
                    tree['dirs'].append(self.__tree(pd))

        return tree

    def __info(self, path):
        filetype = 'file'
        if os.path.isfile(path):
            filetype = 'file'
        elif os.path.isdir(path):
            filetype = 'dir'
        elif os.path.islink(path):
            filetype = 'link'

        stat = os.lstat(path)
        statDate = datetime.fromtimestamp(stat.st_mtime)

        fdate = ''
        if stat.st_mtime >= self._today:
            fdate = 'Today ' + statDate.strftime("%H:%M")
        elif stat.st_mtime >= self._yesterday and stat.st_mtime < self._today:
            fdate = 'Yesterday ' + statDate.strftime("%H:%M")
        else:
            fdate = statDate.strftime("%d %b %Y %H:%M")

        info = {
            'name': os.path.basename(path),
            'hash': self.__hash(path),
            'mime': 'directory' if filetype == 'dir'
            else self.__mimetype(path),
            'date': fdate,
            'size': self.__dirSize(path) if filetype == 'dir'
            else stat.st_size,
            'read': self._isAllowed(path, 'read'),
            'write': self._isAllowed(path, 'write'),
            'rm': self._isAllowed(path, 'rm')
        }

        if filetype == 'link':
            lpath = self.__readlink(path)
            if not lpath:
                info['mime'] = 'symlink-broken'
                return info

            if os.path.isdir(lpath):
                info['mime'] = 'directory'
            else:
                info['parent'] = self.__hash(os.path.dirname(lpath))
                info['mime'] = self.__mimetype(lpath)

            if self.options['rootAlias']:
                basename = self.options['rootAlias']
            else:
                basename = os.path.basename(self.options['root'])

            info['link'] = self.__hash(lpath)
            info['linkTo'] = basename + lpath[len(self.options['root']):]
            info['read'] = info['read'] and self._isAllowed(lpath, 'read')
            info['write'] = info['write'] and self._isAllowed(lpath, 'write')
            info['rm'] = self._isAllowed(lpath, 'rm')
        else:
            lpath = False

        if not info['mime'] == 'directory':
            if self.options['fileURL'] and info['read'] is True:
                if lpath:
                    info['url'] = self.__path2url(lpath)
                else:
                    info['url'] = self.__path2url(path)
            if info['mime'][0:5] == 'image':
                dim = self.__getImgSize(path)
                if dim:
                    info['dim'] = dim
                    info['resize'] = True

                # if we are in tmb dir, files are thumbs itself
                if os.path.dirname(path) == self.tmbDir:
                    info['tmb'] = self.__path2url(path)
                    return info

                tmb = os.path.join(
                    self.tmbDir,
                    info['hash'] + '.png'
                )

                if os.path.exists(tmb):
                    tmbUrl = self.__path2url(tmb)
                    info['tmb'] = tmbUrl
                else:
                    pass

        return info

    def _isAllowed(self, path, access):
        if not os.path.exists(path):
            return False

        if access == 'read':
            if not os.access(path, os.R_OK):
                return False
        elif access == 'write':
            if not os.access(path, os.W_OK):
                return False
        elif access == 'rm':
            if not os.access(os.path.dirname(path), os.W_OK):
                return False
        else:
            return False
        return True

    def _isAccepted(self, target):
        if target == '.' or target == '..':
            return False
        if target[0:1] == '.' and not self.options['dotFiles']:
            return False
        return True

    def check_path(self, path):
        if not os.path.exists(path) or path == '':
            raise ElfinderException(
                'Bad path {}'.format(path)
            )
        elif not self._isAllowed(path, 'read'):
            raise ElfinderException('Access denied to "root" path')


class Commands(BaseCommands):

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            raise ElfinderException('Unknown "{}" command!'.format(name))

    def open(self):
        """
        Returns information about requested directory and its content,
        optionally can return directory tree as files, and options for the
        current volume.
        """
        response = {}
        init = self.request.get('init', None)
        tree = self.request.get('tree', None)
        path = self.options.get('root', None)
        if init:
            response['api'] = '2.0'
        if 'target' in self.request and self.request['target']:
            path = self._findDir(self.request['target'], None)
        return merge_dict(response, self.get_content(path, tree))
