"""Bounded, deterministic archive writing for continuing research packets."""
import gzip
from hashlib import sha256
import os
from pathlib import Path
import stat
import tarfile
from uuid import uuid4


_DIRECTORY_FLAGS=os.O_RDONLY|getattr(os,'O_DIRECTORY',0)|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0)
_READ_FLAGS=os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0)|getattr(os,'O_CLOEXEC',0)
MAX_ARCHIVE_MEMBERS=12
MAX_ARCHIVE_UNCOMPRESSED_BYTES=512*1024**2
MAX_ARCHIVE_TAR_STREAM_BYTES=MAX_ARCHIVE_UNCOMPRESSED_BYTES+1024**2
MAX_COMPRESSED_ARCHIVE_BYTES=MAX_ARCHIVE_UNCOMPRESSED_BYTES+MAX_ARCHIVE_UNCOMPRESSED_BYTES//16383*5+1024**2
MAX_ARCHIVE_TREE_ENTRIES=4096
MAX_ARCHIVE_DIRECTORY_DEPTH=64
MAX_ARCHIVE_PATH_CHARS=100


def _absolute(path):
    return Path(os.path.abspath(path))


def _fdopen(descriptor,mode):
    try:return os.fdopen(descriptor,mode)
    except BaseException:
        os.close(descriptor)
        raise


class _BudgetWriter:
    def __init__(self,stream,maximum):self.stream=stream;self.maximum=maximum;self.written=0
    def write(self,data):
        if self.written+len(data)>self.maximum:
            raise ValueError('Compressed continuing archive exceeds its byte budget')
        written=self.stream.write(data);self.written+=written;return written
    def flush(self):return self.stream.flush()


class BoundedReader:
    """Inspect TAR headers before tarfile can materialize control extensions."""
    def __init__(self,stream,maximum,maximum_read=1024**2):
        self.stream=stream;self.maximum=maximum;self.maximum_read=maximum_read
        self.read_bytes=0;self.payload_remaining=0;self.member_bytes=0;self.ended=False
    def _read_up_to(self,size):
        blocks=[];remaining=size
        while remaining:
            block=self.stream.read(remaining)
            if not block:break
            blocks.append(block);remaining-=len(block)
        return b''.join(blocks)
    def _account(self,data):
        self.read_bytes+=len(data)
        if self.read_bytes>self.maximum:
            raise ValueError('TAR stream exceeds its decompressed byte budget')
        return data
    def _next_header(self):
        header=self._read_up_to(512)
        if len(header)!=512:
            raise ValueError('Truncated ordinary TAR header')
        self._account(header)
        if header==bytes(512):
            self.ended=True
            return header
        if header[156:157] not in (b'\0',b'0'):
            raise ValueError('TAR control or special member headers are not supported')
        size_field=header[124:136].strip(b'\0 ')
        if size_field and any(byte not in b'01234567' for byte in size_field):
            raise ValueError('Ordinary octal TAR member size required')
        size=int(size_field or b'0',8)
        self.member_bytes+=size
        if self.member_bytes>MAX_ARCHIVE_UNCOMPRESSED_BYTES:
            raise ValueError('TAR members exceed their uncompressed byte budget')
        self.payload_remaining=(size+511)//512*512
        return header
    def read(self,size=-1):
        if size is None or size<0:size=self.maximum_read
        if size>self.maximum_read:
            raise ValueError('TAR parser read exceeds its per-read byte budget')
        output=bytearray()
        while len(output)<size and not self.ended:
            if self.payload_remaining==0:
                block=self._next_header();output.extend(block)
                if self.ended:break
            else:
                requested=min(size-len(output),self.payload_remaining)
                block=self._read_up_to(requested)
                if not block:raise ValueError('Truncated ordinary TAR member data')
                self._account(block);output.extend(block);self.payload_remaining-=len(block)
        return bytes(output)


class BundleRollbackError(RuntimeError):
    """A failed bundle rollback with retained files for manual recovery."""
    def __init__(self,staging,errors):
        self.staging=Path(staging)
        super().__init__(f'Publication rollback incomplete; recovery files retained in {self.staging}: {errors}')


def _open_directory(path,*,create=False):
    """Open each directory component without following symlinks."""
    target=_absolute(path)
    descriptor=os.open(os.sep,_DIRECTORY_FLAGS)
    try:
        for component in target.parts[1:]:
            try:
                child=os.open(component,_DIRECTORY_FLAGS,dir_fd=descriptor)
            except FileNotFoundError:
                if not create:raise
                try:os.mkdir(component,0o777,dir_fd=descriptor)
                except FileExistsError:pass
                else:os.fsync(descriptor)
                child=os.open(component,_DIRECTORY_FLAGS,dir_fd=descriptor)
            os.close(descriptor);descriptor=child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def ensure_directory(path):
    """Create an output directory while refusing symlinks in its path."""
    target=_absolute(path)
    try:descriptor=_open_directory(target,create=True)
    except OSError as exc:raise ValueError('Symlinked or non-directory archive path refused') from exc
    os.close(descriptor)
    return target


def _ordinary_name(name):
    return (isinstance(name,str) and bool(name) and name not in ('.','..')
        and '/' not in name and '\\' not in name)


def _existing_regular(directory_fd,name):
    try:info=os.stat(name,dir_fd=directory_fd,follow_symlinks=False)
    except FileNotFoundError:return False
    if not stat.S_ISREG(info.st_mode):raise ValueError('Ordinary publication file required')
    return True


def validate_destinations(directory,names):
    """Reject symlinked or non-regular existing publication children."""
    descriptor=_open_directory(directory)
    try:
        for name in names:
            if not _ordinary_name(name):raise ValueError('Ordinary publication filenames required')
            _existing_regular(descriptor,name)
    finally:os.close(descriptor)


def sha256_file(directory,name,*,maximum_bytes=None):
    """Hash one publication member in bounded chunks without following links."""
    if not _ordinary_name(name):raise ValueError('Ordinary publication filename required')
    directory_fd=_open_directory(directory)
    try:descriptor=os.open(name,_READ_FLAGS,dir_fd=directory_fd)
    finally:os.close(directory_fd)
    try:
        with _fdopen(descriptor,'rb') as stream:
            before=os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):raise ValueError('Ordinary publication file required')
            if maximum_bytes is not None and before.st_size>maximum_bytes:
                raise ValueError('Publication file exceeds its byte budget')
            signature=lambda item:(item.st_dev,item.st_ino,item.st_size,item.st_mtime_ns,item.st_ctime_ns)
            digest=sha256()
            total=0
            while True:
                block=stream.read(1024*1024)
                if not block:break
                total+=len(block)
                if maximum_bytes is not None and total>maximum_bytes:
                    raise ValueError('Publication file exceeds its byte budget')
                digest.update(block)
            if total!=before.st_size:
                raise ValueError('Publication file changed during hashing')
            if signature(before)!=signature(os.fstat(stream.fileno())):
                raise ValueError('Publication file changed during hashing')
            return digest.hexdigest()
    except OSError as exc:raise ValueError('Ordinary publication file required') from exc


def open_lock_file(directory,name):
    """Open a singly linked regular lock file relative to a pinned directory."""
    if not _ordinary_name(name):raise ValueError('Ordinary lock filename required')
    directory_fd=_open_directory(directory)
    try:
        descriptor=os.open(name,os.O_CREAT|os.O_RDWR|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0)|getattr(os,'O_CLOEXEC',0),0o600,dir_fd=directory_fd)
        info=os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1:
            os.close(descriptor)
            raise ValueError('Lock file must be a singly linked ordinary file')
        return descriptor
    finally:os.close(directory_fd)


def write_atomic_bytes(directory,name,raw):
    """Atomically replace one ordinary file through a pinned directory handle."""
    if not _ordinary_name(name) or not isinstance(raw,bytes):
        raise ValueError('Ordinary filename and immutable bytes required')
    descriptor=_open_directory(directory);temporary=name+'.tmp-'+uuid4().hex;created=False
    try:
        _existing_regular(descriptor,name)
        output_fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0),0o644,dir_fd=descriptor)
        created=True
        with _fdopen(output_fd,'wb') as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        _existing_regular(descriptor,name)
        os.replace(temporary,name,src_dir_fd=descriptor,dst_dir_fd=descriptor)
        created=False;os.fsync(descriptor)
    except BaseException:
        if created:
            try:os.unlink(temporary,dir_fd=descriptor)
            except FileNotFoundError:pass
        raise
    finally:os.close(descriptor)


def replace_file_bundle(staging,directory,names):
    """Install a prepared file bundle and restore its previous generation on failure."""
    staging=_absolute(staging);directory=_absolute(directory)
    if staging.parent!=directory or not names or len(set(names))!=len(names):
        raise ValueError('Publication staging directory must be a direct child')
    target_fd=_open_directory(directory);staging_fd=None
    backups={};install_attempts=set();staged_identity={}
    try:
        staging_fd=_open_directory(staging)
        for name in names:
            if not _ordinary_name(name) or not _existing_regular(staging_fd,name):
                raise ValueError('Ordinary staged publication files required')
            staged_info=os.stat(name,dir_fd=staging_fd,follow_symlinks=False)
            staged_identity[name]=(staged_info.st_dev,staged_info.st_ino)
            _existing_regular(target_fd,name)
        try:
            # Persist the staging directory entry before it can become the sole
            # location of any previous publication member.
            os.fsync(target_fd)
            for name in names:
                if _existing_regular(target_fd,name):
                    backup='.old-'+uuid4().hex+'-'+name
                    backups[name]=backup
                    os.replace(name,backup,src_dir_fd=target_fd,dst_dir_fd=staging_fd)
            # Cross-directory renames must be durable on both sides before new
            # files replace the old publication.
            os.fsync(staging_fd)
            os.fsync(target_fd)
            for name in names:
                install_attempts.add(name)
                os.replace(name,name,src_dir_fd=staging_fd,dst_dir_fd=target_fd)
            os.fsync(target_fd)
            os.fsync(staging_fd)
        except BaseException as error:
            rollback_errors=[]
            for name in reversed(names):
                if name in install_attempts:
                    try:staged_still_present=_existing_regular(staging_fd,name)
                    except BaseException as rollback_error:
                        rollback_errors.append(rollback_error);staged_still_present=True
                    if not staged_still_present:
                        try:
                            installed_info=os.stat(name,dir_fd=target_fd,follow_symlinks=False)
                            if (installed_info.st_dev,installed_info.st_ino)!=staged_identity[name]:
                                raise ValueError(f'Installed publication file identity changed: {name}')
                            os.unlink(name,dir_fd=target_fd)
                        except FileNotFoundError:
                            rollback_errors.append(FileNotFoundError(f'Installed publication file disappeared: {name}'))
                        except BaseException as rollback_error:rollback_errors.append(rollback_error)
                backup=backups.get(name)
                if backup is not None:
                    try:backup_present=_existing_regular(staging_fd,backup)
                    except BaseException as rollback_error:
                        rollback_errors.append(rollback_error);backup_present=True
                    if backup_present:
                        try:os.replace(backup,name,src_dir_fd=staging_fd,dst_dir_fd=target_fd)
                        except BaseException as rollback_error:rollback_errors.append(rollback_error)
                    else:
                        try:os.stat(name,dir_fd=target_fd,follow_symlinks=False)
                        except FileNotFoundError:
                            rollback_errors.append(FileNotFoundError(f'Previous publication file is missing: {name}'))
                        except BaseException as rollback_error:rollback_errors.append(rollback_error)
            try:os.fsync(target_fd)
            except BaseException as rollback_error:rollback_errors.append(rollback_error)
            try:os.fsync(staging_fd)
            except BaseException as rollback_error:rollback_errors.append(rollback_error)
            if rollback_errors:
                raise BundleRollbackError(staging,', '.join(repr(item) for item in rollback_errors)) from error
            raise
    finally:
        if staging_fd is not None:os.close(staging_fd)
        os.close(target_fd)


def validate_tar_member_name(name):
    """Accept only portable, ordinary relative POSIX archive paths."""
    if (not isinstance(name,str) or not name or name.startswith('/')
            or not name.isascii() or len(name)>MAX_ARCHIVE_PATH_CHARS
            or '\\' in name or ':' in name or '\x00' in name):
        raise ValueError('Ordinary relative archive member required')
    parts=name.split('/')
    if len(parts)>MAX_ARCHIVE_DIRECTORY_DEPTH+1 or any(part in ('','.','..') for part in parts):
        raise ValueError('Ordinary relative archive member required')
    return name


def _open_member(root_fd,relative):
    validate_tar_member_name(relative)
    parts=relative.split('/')
    parent=os.dup(root_fd)
    try:
        for component in parts[:-1]:
            child=os.open(component,_DIRECTORY_FLAGS,dir_fd=parent)
            os.close(parent);parent=child
        return os.open(parts[-1],_READ_FLAGS,dir_fd=parent)
    finally:os.close(parent)


def _walk_member_files(root_fd):
    """Yield a deterministic, bounded tree without following directory links."""
    visited=0
    def visit(directory_fd,prefix,depth):
        nonlocal visited
        if depth>MAX_ARCHIVE_DIRECTORY_DEPTH:
            raise ValueError('Continuing artifact directory depth exceeds its budget')
        names=[]
        with os.scandir(directory_fd) as entries:
            for entry in entries:
                visited+=1
                if visited>MAX_ARCHIVE_TREE_ENTRIES:
                    raise ValueError('Continuing artifact tree exceeds its entry budget')
                names.append(entry.name)
        for name in sorted(names):
            relative=f'{prefix}/{name}' if prefix else name
            validate_tar_member_name(relative)
            info=os.stat(name,dir_fd=directory_fd,follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                raise ValueError('Linked continuing artifact refused during archive creation')
            if name=='.coordinator.lock' and stat.S_ISREG(info.st_mode):
                continue
            if stat.S_ISDIR(info.st_mode):
                child=os.open(name,_DIRECTORY_FLAGS,dir_fd=directory_fd)
                try:yield from visit(child,relative,depth+1)
                finally:os.close(child)
            elif stat.S_ISREG(info.st_mode):
                yield relative,info
            else:
                raise ValueError('Ordinary continuing artifact required during archive creation')
    yield from visit(root_fd,'',0)


def write_streaming_archive(folder,destination):
    """Write a deterministic gzip/TAR without holding the archive in memory."""
    folder=_absolute(folder);destination=_absolute(destination)
    if destination==folder or destination.is_relative_to(folder):
        raise ValueError('Archive destination must be outside its source directory')
    source_fd=None;destination_fd=None
    try:
        source_fd=_open_directory(folder)
        destination_fd=_open_directory(destination.parent)
    except OSError as exc:
        if source_fd is not None:os.close(source_fd)
        if destination_fd is not None:os.close(destination_fd)
        raise ValueError('Symlinked or non-directory archive path refused') from exc
    if not destination.name:
        os.close(source_fd);os.close(destination_fd)
        raise ValueError('Ordinary archive destination required')
    temporary=destination.name+'.tmp-'+uuid4().hex;created=False
    member_count=0;uncompressed_bytes=0
    try:
        _existing_regular(destination_fd,destination.name)
        output_fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_CLOEXEC',0),0o644,dir_fd=destination_fd)
        created=True
        with _fdopen(output_fd,'wb') as raw:
            bounded=_BudgetWriter(raw,MAX_COMPRESSED_ARCHIVE_BYTES)
            with gzip.GzipFile(filename='',fileobj=bounded,mode='wb',mtime=0) as compressed:
                with tarfile.open(fileobj=compressed,mode='w|',format=tarfile.USTAR_FORMAT) as archive:
                    for relative,entry in _walk_member_files(source_fd):
                        member_fd=_open_member(source_fd,relative)
                        with _fdopen(member_fd,'rb') as source:
                            before=os.fstat(source.fileno())
                            signature=lambda item:(item.st_dev,item.st_ino,item.st_size,item.st_mtime_ns,item.st_ctime_ns)
                            if not stat.S_ISREG(before.st_mode) or signature(before)!=signature(entry):
                                raise ValueError('Continuing artifact changed before archive read')
                            member_count+=1;uncompressed_bytes+=before.st_size
                            if member_count>MAX_ARCHIVE_MEMBERS or uncompressed_bytes>MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                                raise ValueError('Continuing archive exceeds its verified member or byte budget')
                            info=tarfile.TarInfo(relative);info.size=before.st_size
                            info.mode=0o644;info.mtime=0;info.uid=0;info.gid=0;info.uname='';info.gname=''
                            archive.addfile(info,source)
                            if signature(before)!=signature(os.fstat(source.fileno())):
                                raise ValueError('Continuing artifact changed during archive read')
            raw.flush();os.fsync(raw.fileno())
        _existing_regular(destination_fd,destination.name)
        os.replace(temporary,destination.name,src_dir_fd=destination_fd,dst_dir_fd=destination_fd)
        # A directory-fsync failure is reported; the replaced archive may remain,
        # but coordinator publication writes its manifest only after this returns.
        created=False;os.fsync(destination_fd)
    except BaseException:
        if created:
            try:os.unlink(temporary,dir_fd=destination_fd)
            except FileNotFoundError:pass
        raise
    finally:
        os.close(source_fd);os.close(destination_fd)
