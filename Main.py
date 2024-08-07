import cv2 
import os 
import sys 
import signal 
import time 
from edge_impulse_linux.image import ImageImpulseRunner 
 
import requests 
import json 
from requests.structures import CaseInsensitiveDict 
 
runner = None 
show_camera = True 
 
global id_product 
id_product = 1 
list_label = [] 
count = 0 
taken = 0 
 
a = ‘Pouch’ 
b = ‘Bottle’ 
c = ‘Pen’ 
 
 
def now(): 
    return round(time.time() * 1000) 
 
def sigint_handler(sig, frame): 
    print('Interrupted') 
    if (runner): 
        runner.stop() 
    sys.exit(0) 
 
signal.signal(signal.SIGINT, sigint_handler) 
 
def help(): 
    print('python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera 
is present>') 
 
def post(label, price, final_rate, taken): 
    global id_product 
    url = "https://automaticbilling.herokuapp.com/product" 
    headers = CaseInsensitiveDict() 
    headers["Content-Type"] = "application/json" 
    data_dict = {"id": id_product, "name": label, "price": price, "units": "units", "taken": taken, 
"payable": final_rate} 
    data = json.dumps(data_dict) 
    resp = requests.post(url, headers=headers, data=data) 
    print(resp.status_code) 
    id_product += 1 
    time.sleep(1) 
 
def list_com(label): 
    global count 
    global taken 
    count += 1 
    print('count is', count) 
    time.sleep(1) 
    if count > 1: 
        if list_label[-1] != label: 
            print("New Item detected") 
            print("Final weight is", list_weight[-1]) 
            rate(list_label[-2], taken) 
 
def rate(label, taken): 
    print("Calculating rate") 
    if label == a: 
        print("Calculating rate of", label) 
        price = 200 
        post(label, price, 1, taken) 
    elif label == b: 
        print("Calculating rate of", label) 
        price = 1000 
        post(label, price, 1000, taken) 
    else: 
        print("Calculating rate of", label) 
        price = 10 
        post(label, price, 10, taken) 
 
def main(argv): 
    try: 
        opts, args = getopt.getopt(argv, "h", ["--help"]) 
    except getopt.GetoptError: 
        help() 
        sys.exit(2) 
    for opt, arg in opts: 
        if opt in ('-h', '--help'): 
            help() 
            sys.exit() 
 
    if len(args) == 0: 
        help() 
        sys.exit(2) 
 
    model = args[0] 
 
    dir_path = os.path.dirname(os.path.realpath(__file__)) 
    modelfile = os.path.join(dir_path, model) 
 
    print('MODEL: ' + modelfile) 
 
    with ImageImpulseRunner(modelfile) as runner: 
        try: 
            model_info = runner.init() 
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + 
model_info['project']['name'] + '"') 
            labels = model_info['model_parameters']['labels'] 
            if len(args) >= 2: 
                videoCaptureDeviceId = int(args[1]) 
            else: 
                port_ids = get_webcams() 
                if len(port_ids) == 0: 
                    raise Exception('Cannot find any webcams') 
                if len(args) <= 1 and len(port_ids) > 1: 
                    raise Exception("Multiple cameras found. Add the camera port ID as a second argument 
to use to this script") 
                videoCaptureDeviceId = int(port_ids[0]) 
 
            camera = cv2.VideoCapture(videoCaptureDeviceId) 
            ret = camera.read()[0] 
            if ret: 
                backendName = camera.getBackendName() 
                w = camera.get(3) 
                h = camera.get(4) 
                print("Camera %s (%s x %s) in port %s selected." % (backendName, h, w, 
videoCaptureDeviceId)) 
                camera.release() 
            else: 
                raise Exception("Couldn't initialize selected camera.") 
 
            next_frame = 0  # limit to ~10 fps here 
 
            for res, img in runner.classifier(videoCaptureDeviceId): 
                if (next_frame > now()): 
                    time.sleep((next_frame - now()) / 1000) 
 
                # print('classification runner response', res) 
 
                if "classification" in res["result"].keys(): 
                    print('Result (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), 
end='') 
                    for label in labels: 
                        score = res['result']['classification'][label] 
                        if score > 0.9: 
                            list_com(label) 
                            if label == a: 
                                print('Apple detected') 
                            elif label == b: 
                                print('Banana detected') 
                            elif label == l: 
                                print('Lays detected') 
                            else: 
                                print('Coke detected') 
                    print('', flush=True) 
                next_frame = now() + 100 
        finally: 
            if (runner): 
                runner.stop() 
 
if __name__ == "__main__": 
    main(sys.argv[1:]) 
