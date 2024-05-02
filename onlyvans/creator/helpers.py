def get_upload_to(instance, filename):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        return 'images/{}'.format(filename)
    elif filename.endswith('.mp4') or filename.endswith('.avi'):
        return 'videos/{}'.format(filename)