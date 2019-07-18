#!/usr/bin/python
import os.path
import os
import datetime
import shutil
import cv2
import numpy as np
import tarfile

photo_root_dirs = ["/mnt/hdd/GatePhotos", "/mnt/hdd/StairsPhotos"]
video_root_dirs = ["/mnt/hdd/GateVideos", "/mnt/hdd/StairsVideos"]

def get_files(parent_dir, extension):
    return [x for x in os.listdir(parent_dir) if x.endswith(extension)]


def get_sub_dirs(root_dir):
    return [x for x in os.listdir(root_dir) if os.path.isdir(root_dir+"/"+x)]


def ensure_dir_exists(directory):
	if not os.path.exists(directory):
		os.mkdir(directory)


def replace_with_low_res(directory, files):
    for img in files:
        try:
            cv2_img = cv2.imread(os.path.join(directory,img))
            if str(cv2_img.shape) == "(360, 640, 3)":
                continue
            cv2_img = cv2.resize(cv2_img, (640, 360))
            cv2.imwrite(os.path.join(os.path.join(directory,"temp.jpg")), cv2_img)
            os.remove(os.path.join(directory,img))
            os.rename(os.path.join(os.path.join(directory,"temp.jpg")), os.path.join(directory,img))
        except:
            log_message("error reading:"+img)


def log_message(message):
    print(message.rstrip()+"\n")


def addMarkerLine():
    log_message("*"*180)

def check_hdd():
    try:
        os.listdir("/mnt/hdd")
        os.listdir("/mnt/hdd/GatePhotos")
        os.listdir("/mnt/hdd/StairsPhotos")
        os.listdir("/mnt/hdd/tmp/GateCamera")
        os.listdir("/mnt/hdd/tmp/StairsCamera")
        log_message("Hard disk is accessible")
        return True
    except Exception as error:
        log_message("Hard disk is not accessible: "+ str(error))
        log_message("Rebooting Raspberry PI now....")
        os.system("sudo reboot")
        return False

def save_space_image(date_dir):
    log_message("Running save_space_image on date:"+date_dir)
    for hour_dir in get_sub_dirs(date_dir):
        all_images = get_files(os.path.join(date_dir, hour_dir), "jpg")
        non_person_imgs = all_images
        person_dir = os.path.join(date_dir,hour_dir,"persons")
        if os.path.exists(person_dir):
            person_imgs = get_files(person_dir,"jpg")
            non_person_imgs = [x for x in all_images if x not in person_imgs]

        replace_with_low_res(os.path.join(date_dir,hour_dir),non_person_imgs)

def save_space_video(date_dir):
    log_message("Running save_space_video on date:"+date_dir)
    for hour_dir in get_sub_dirs(date_dir):
        person_dir = os.path.join(date_dir,hour_dir,"persons")
        if not os.path.exists(person_dir):
            gate_video = os.path.join(date_dir.replace("Photos","Videos"),hour_dir)
            if os.path.exists(gate_video):
                shutil.rmtree(gate_video)

def save_video_space2(date_dir):
    log_message("Running save_video_space2 on date:"+date_dir)
    for hr_dir in get_sub_dirs(date_dir):
        for video in get_files(os.path.join(date_dir,hr_dir),"mp4"):
            exists = check_person_exists_in_video(date_dir, hr_dir, video)
            if exists==False:
                os.remove(os.path.join(date_dir,hr_dir,video))

def check_person_exists_in_video(date_dir, hour, video):
    date_dir = date_dir.replace("Videos","Photos")
    date = os.path.split(date_dir)[-1]
    temp = video.split('[M]')[0].split('-')
    start_time = datetime.datetime.strptime(date + " " + temp[0], '%Y-%m-%d %H.%M.%S')
    end_time = datetime.datetime.strptime(date + " " + temp[1], '%Y-%m-%d %H.%M.%S')

    person_dir = os.path.join(date_dir,hour,'persons')
    imgs = get_files(person_dir,"jpg")
    imgs.sort()
    for i in range(len(imgs)):
        time = imgs[i].split('[M]')[0]
        if "_" in time:
            img_time = datetime.datetime.strptime(date + " " + time, '%Y-%m-%d %H_%M_%S')
        else:
            img_time = datetime.datetime.strptime(date + " " + time, '%Y-%m-%d %H.%M.%S')
        if img_time > start_time:
            return img_time < end_time
    return False

def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def backup(root_dir):
    print("Backing up :"+root_dir)
    hours = get_sub_dirs(root_dir)
    for hour_dir in hours:
        target_dir = os.path.join(root_dir,hour_dir,hour_dir)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

        ensure_dir_exists(target_dir)
        print("Backing up :"+target_dir)

        person_list = os.path.join(root_dir,hour_dir,"person.txt")
        other_list = os.path.join(root_dir,hour_dir,"others.txt")

        if not os.path.exists(person_list) or not os.path.exists(other_list):
            continue

        files_to_copy = []
        files_to_copy.append(person_list)
        files_to_copy.append(other_list)

        # Add person images to list.
        f = open(person_list)
        while 1:
            line = f.readline().rstrip()
            if not line:
                break
            files_to_copy.append(os.path.join(root_dir,hour_dir,line))
        f.close()

        # Add other images to list.
        f = open(other_list)
        while 1:
            line = f.readline().rstrip()
            if not line:
                break
            files_to_copy.append(os.path.join(root_dir,hour_dir,"thumbnails",line))
        f.close()

        for file in files_to_copy:
            shutil.copy2(file,target_dir)

        make_tarfile(os.path.join(root_dir,hour_dir,hour_dir+".tar.gz"),target_dir)
        #shutil.rmtree(target_dir)

def delete_old_footage():
    expiry_date_dictionary = {
        "/mnt/hdd/GatePhotos": 5,
        "/mnt/hdd/StairsPhotos": 5,
        "/mnt/hdd/GateVideos": 3,
        "/mnt/hdd/StairsVideos": 3,
        "/mnt/hdd/tmp/GateCamera": 0,
        "/mnt/hdd/tmp/StairsCamera": 0
    }

    today = datetime.datetime.now().date()
    print("Deleting old footage...")
    for root_dir in expiry_date_dictionary:
        expiry_date = expiry_date_dictionary[root_dir]
        for dt_dir in get_sub_dirs(root_dir):
            if dt_dir == "train":
                continue
            dt = datetime.datetime.strptime(dt_dir, "%Y-%m-%d").date()
            elapsed_days = (today-dt).days
            if elapsed_days > expiry_date:
                try:
                    print("Deleting: "+root_dir+"/"+dt_dir)
                    shutil.rmtree(root_dir+"/"+dt_dir)
                except:
                    print("Error deleting directory:"+root_dir+"/"+dt_dir)


def save_backups():
    date = datetime.datetime.now() - datetime.timedelta(days=1)
    date = date.strftime("%Y-%m-%d")

    backup(os.path.join(photo_root_dirs[0],date))

def save_space_main():
    if not check_hdd():
        exit(0)

    past_time = datetime.datetime.now() - datetime.timedelta(days=1)
    past_date = past_time.strftime("%Y-%m-%d")

    for photo_root in photo_root_dirs:
        date_dir = os.path.join(photo_root, past_date)
        if os.path.exists(date_dir):
            save_space_video(date_dir)
            #save_space_image(date_dir)

    for video_root in video_root_dirs:
        date_dir = os.path.join(video_root,past_date)
        if os.path.exists(date_dir):
            save_video_space2(date_dir)