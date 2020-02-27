import sys, os


is_frozen = getattr(sys, 'frozen', False)
frozen_temp_path = getattr(sys, '_MEIPASS', '')

if is_frozen:
    basedir = frozen_temp_path
else:
    basedir = os.path.dirname(os.path.abspath(__file__))

resource_dir = os.path.join(basedir, 'resources')