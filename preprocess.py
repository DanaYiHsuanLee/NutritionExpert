from pathlib import Path
import os
import splitfolders
import shutil

IMAGE_WIDTH = 448
IMAGE_HEIGHT = 336
# Select_class = [1, 6, 7, 12, 17, 18, 19, 26, 27, 31, 38, 43, 46, 55, 58, 60, 61, 68, 80, 81, 87, 97, 98, 130, 155, 168, 169, 173, 187]
Select_class = [2, 3]

def copy_images(src_directory, dest_directory):
    src_directory = Path(src_directory)
    dest_directory = Path(dest_directory)

    # Create the target folder 'image'
    dest_subdir = dest_directory / 'image'
    dest_subdir.mkdir(parents=True, exist_ok=True)
    image_formats = ['.jpg', '.png', '.jpeg', '.gif']

    # Copy all matching format image files
    for img_file in src_directory.iterdir():
        if img_file.is_file() and img_file.suffix.lower() in image_formats:  # 只複製圖片文件
            shutil.copy2(img_file, dest_subdir)

def copy_txt_files(src_directory, dest_directory):
    src_directory = Path(src_directory)
    dest_directory = Path(dest_directory)
    for txt_file in src_directory.glob('*.txt'):
        with open(txt_file, 'r') as f:
            lines = f.readlines()
        lines = lines[1:]
        for line in lines:
            # first set of numbers to be used as the filename
            original_first_number = line.split()[0]

            #  the name of the source folder
            line_parts = line.split()
            line_parts[0] = src_directory.name
            new_line = " ".join(line_parts)

            new_file_name = f"{original_first_number}.txt"
            dest_file = dest_directory / new_file_name

            i = 2
            while dest_file.exists():
                dest_file = dest_directory / f"{original_first_number}_{i}.txt"
                i += 1

            with open(dest_file, 'w') as new_file:
                new_file.write(new_line)

def convert_label(name, x1, y1, x2, y2):
    '''
    Normalized(Xmin) = (Xmin+w/2)/Image_Width

    Normalized(Ymin) = (Ymin+h/2)/Image_Height

    Normalized(w) = w/Image_Width

    Normalized(h) = h/Image_Height
    '''
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    w = x2 - x1
    h = y2 - y1
    normalizedXmin = (x1 + w/2) / IMAGE_WIDTH
    normalizedYmin = (y1 + h/2) / IMAGE_HEIGHT
    normalizedW = w / IMAGE_WIDTH
    normalizedH = h / IMAGE_HEIGHT
    return (name, str(normalizedXmin), str(normalizedYmin), str(normalizedW), str(normalizedH))


def write_to_txt(file, converted_labels):
    directory = '../datasets/256class/label'
    fileName = str(file).split("\\")[-1]
    f = open(directory + '/' + fileName, "w")
    for converted_label in converted_labels:
        line = ' '.join(converted_label)
        f.write(line + '\n')
    f.close()


def generate_yolo_labels():
    new_directory = '../datasets/256class/label' # Normalized numbers in label folder
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
    directory = '../datasets/256class/Annotations' # pre-normalized numbers in Annotation folder
    # iterate over files in that directory
    files = Path(directory).glob('*')
    for file in files:
        lines = file.read_text().split('\n')
        converted_labels = []
        for line in lines:
            if line == '':
                break
            line = line.strip()
            name = line.split(' ')[0]
            x1 = line.split(' ')[1]
            y1 = line.split(' ')[2]
            x2 = line.split(' ')[3]
            y2 = line.split(' ')[4]
            converted_label = convert_label(name, x1, y1, x2, y2)
            converted_labels.append(converted_label)
        write_to_txt(file, converted_labels)


def train_val_test_split(input_folder, output):
    # Split with a ratio.
    splitfolders.ratio(input_folder, output=output,
        seed=1337, ratio=(.8, .1, .1), group_prefix=None, move=False)


def copy_folder_contents(source_folders, destination_folders):
    for i in range(len(source_folders)):
        source_folder = source_folders[i]
        destination_folder = destination_folders[i]
        if os.path.exists(destination_folder):
            shutil.rmtree(destination_folder)
        os.makedirs(destination_folder)

        # Copy the contents of the source folder to the target folder
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                source_file = os.path.join(root, file)
                destination_file = os.path.join(destination_folder, file)
                shutil.copy(source_file, destination_file)


def delete_folders(folders):
    for folder in folders:
        shutil.rmtree(folder)


if __name__ == '__main__':
    for i in Select_class:
        copy_txt_files('../UECFOOD256'+'/'+str(i), '../datasets/256class/Annotations')
        copy_images('../UECFOOD256/' + str(i), '../datasets/256class')
    generate_yolo_labels()
    train_val_test_split('../datasets/256class', '../datasets/data')

    # organize the folders
    source_folders = ['../datasets/data/train/image', '../datasets/data/test/image', '../datasets/data/val/image', '../datasets/data/train/label', '../datasets/data/test/label', '../datasets/data/val/label']
    destination_folders = ['../datasets/data/images/train', '../datasets/data/images/test', '../datasets/data/images/val', '../datasets/data/labels/train', '../datasets/data/labels/test', '../datasets/data/labels/val']
    copy_folder_contents(source_folders, destination_folders)
    folders_to_delete = ['../datasets/data/train', '../datasets/data/test', '../datasets/data/val']
    delete_folders(folders_to_delete)