def get_upload_to(instance, filename):
    """
    Determine the upload path for media files based on their file type.

    Parameters:
    - instance: The model instance this file is being attached to.
    - filename: The name of the file being uploaded.

    Returns:
    - A string representing the upload path for the file, categorized by its type (images or videos).
    """
    if filename.endswith('.jpg') or filename.endswith('.png'):
        return 'images/{}'.format(filename)
    elif filename.endswith('.mp4') or filename.endswith('.avi'):
        return 'videos/{}'.format(filename)
    else:
        raise ValueError("Unsupported file type")
