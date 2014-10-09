import os
import mimetypes
from django import forms
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.views.generic.base import View
from django.utils.translation import ugettext as _

from ..conf import settings
from ..storages import private_storage

import logging
logger = logging.getLogger(__name__)


#==============================================================================
class GenericFileServeView(View):
    def handle_request(self, request, file_object):
        # available space
        #freespace = request.user.constraint_value('max_diskspace') - a.get_documents_disksize()
        #max_size = min(freespace, settings.FILE_UPLOAD_MAX_MEMORY_SIZE) / (1024 * 1024)

        data = { 'files': [], 'status': False, 'msg': '' }

        if 'path' in request.GET:
            path = request.GET.get('path')
            dirnames, filenames = file_object.repository_listdir(path)
            if dirnames is not None and filenames is not None:
                if path != '':
                    data['files'].append({
                        'folder': True,
                        'name': '..',
                        'link': os.path.split(path)[0],
                    })
                for fs in dirnames:
                    if not fs.startswith('.'):
                        data['files'].append({
                            'folder': True,
                            'name': fs,
                            'link': os.path.join(path, fs),
                        })
                for fs in filenames:
                    if not fs.startswith('.'):
                        data['files'].append({
                            'folder': False,
                            'name': fs,
                            'link': os.path.join(path, fs),
                        })
                data['status'] = True

        elif 'new' in request.GET:
            src = request.POST.get('src')
            path = os.path.join(request.POST.get('path'), src)
            if request.POST.get('type') == "folder":
                data['status'] = file_object.repository_create_folder(path)
                if data["status"]:
                    data['msg'] = _("Folder <strong>%(filename)s</strong> created successfully !") % { 'filename': src }
                else:
                    data['msg'] = _("Unable to create folder <strong>%(filename)s</strong>") % { 'filename': src }
            else:
                data['status'] = file_object.repository_create_file(path)
                if data["status"]:
                    data['msg'] = _("File <strong>%(filename)s</strong> created successfully !") % { 'filename': src }
                else:
                    data['msg'] = _("Unable to create file <strong>%(filename)s</strong>") % { 'filename': src }

        elif 'move' in request.GET:
            src = request.POST.get('src')
            dst = request.POST.get('dst')
            pathsrc = os.path.join(request.POST.get('path'), src)
            pathdst = os.path.join(request.POST.get('path'), dst)
            data['status'] = file_object.repository_move_file(pathsrc, pathdst)
            if data["status"]:
                data['msg'] = _("File <strong>%(filename)s</strong> moved successfully !") % { 'filename': src }
            else:
                data['msg'] = _("Unable to move file <strong>%(filename)s</strong>") % { 'filename': src }

        elif 'remove' in request.GET:
            src = request.POST.get('src')
            data['status'] = file_object.repository_delete_path(src)
            if data["status"]:
                data['msg'] = _("File <strong>%(filename)s</strong> deleted successfully !") % { 'filename': src }
            else:
                data['msg'] = _("Unable to delete file <strong>%(filename)s</strong>") % { 'filename': src }

        elif 'edit' in request.GET:
            src = request.GET.get('edit')
            f = file_object.repository_open_file(src)
            if f is not None:
                response = HttpResponse(f.read(), content_type=mimetypes.guess_type(src))
                return response

        elif 'download' in request.GET:
            src = request.GET.get('download')
            f = file_object.repository_open_file(src)
            if f is not None:
                response = HttpResponse(f.read(), content_type=mimetypes.guess_type(src))
                #response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.split(src)[-1]
                return response

        elif 'upload' in request.GET:
            if request.method == "POST":
                src = request.POST.get('path')
                file_list = request.FILES.getlist('files[]')
                for f in file_list:
                    file_object.repository_write_file(os.path.join(src, f.name), f)
                data["status"] = True
                data['msg'] = _("Files uploaded successfully !")

        return JsonResponse(data)
