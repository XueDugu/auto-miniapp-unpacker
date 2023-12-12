import os
import re
import shlex
import time
import tkinter as tk
import subprocess

button_style = {"width": 15, "height": 2, "padx": 50, "pady": 10, "bd": 4, "relief": "raised", "bg": "lightblue", "fg": "black", "font": ('Helvetica', 12, 'bold')}
# 运行按钮

root = tk.Tk()
root.title("微信自动解包")
root.geometry("370x700")
# 设置窗口大小

text_label = tk.Label(root, text="记录栏", font=('Helvetica', 12, 'bold'))
text_label.grid(row=0, column=0, columnspan=2, pady=10)

text_box = tk.Text(root, height=15, width=50)
text_box.grid(row=1, column=0, rowspan=3, columnspan=2, padx=10, pady=10)

def clear_text_box():
    text_box.delete("1.0", tk.END)

clear_btn = tk.Button(root, text="Clear", command=clear_text_box, **button_style)
clear_btn.grid(row=9, column=0, pady=10)
# 清除记录栏
def clear_text_box():
    text_box.delete("1.0", tk.END)

file_entry = tk.Entry(root)
file_entry.grid(row=5, column=0, pady=10)
file_entry.insert(0, "请输入文件夹完整路径")


def get_file(event=None):
    flag=0
    file = file_entry.get()
    if(file!="请输入文件夹完整路径"):
        subfolders = [f for f in os.listdir(file) if os.path.isdir(os.path.join(file, f))]
        if subfolders is not None:
            if flag==0:
                flag=1
                text_box.insert(tk.END, file+"中的小程序包有:\n")
            text_box.insert(tk.END, "已解包的小程序包有:\n")
            for subfolder in subfolders:
                text_box.insert(tk.END, subfolder+"\n")
        wxapkg_files = [f for f in os.listdir(file) if f.endswith(".wxapkg")]
        if wxapkg_files is not None:
            if flag==0:
                flag=1
                text_box.insert(tk.END, file+"中的小程序包有:\n")
            text_box.insert(tk.END, "未解包的小程序包有:\n")
            for wxapkg_file in wxapkg_files:
                text_box.insert(tk.END, wxapkg_file+"\n")
        if flag==0:
            text_box.insert(tk.END, file+"中无小程序文件\n")
file_entry.bind("<Return>", get_file)
getfile_btn = tk.Button(root, text="更新已有文件", command=get_file, **button_style)
getfile_btn.grid(row=6, column=0, pady=10)
listening=False
count=0
def wechat_num():
    adb_command = 'adb shell su -c "ls /data/data/com.eg.android.AlipayGphone/files/nebulaInstallApps | wc -l"'
    process = subprocess.Popen(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result=process.stdout.readline().strip()
    return int(result)

def start_listen():
    global listening
    listening=True
    text_box.insert(tk.END, "Start listening...\n")
    raw=wechat_num()
    pkg_stack=[]
    print(raw)
    adb_command = 'adb shell su -c "ls /data/data/com.eg.android.AlipayGphone/files/nebulaInstallApps"'
    process = subprocess.Popen(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for _ in range(raw):    
        pkg=process.stdout.readline().strip()
        pkg_stack.append(pkg)
    while listening:
        result=wechat_num()
        if result > raw:
            text_box.insert(tk.END, "有新的"+str(result-raw)+"个小程序包\n")
            process = subprocess.Popen(adb_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            newpkg_stack=[]
            for _ in range(raw):    
                pkg=process.stdout.readline().strip()
                newpkg_stack.append(pkg)
            extra_objects = set(newpkg_stack) - set(pkg_stack)
            pkg_list=list(extra_objects)
            for i in range(len(pkg_list)):
                text_box.insert(tk.END, pkg_list[i] + "\n")
                file = file_entry.get()
                command = 'adb pull /data/data/com.eg.android.AlipayGphone/files/nebulaInstallApps/{pkg} {dest}'.format(pkg=pkg_list[i], dest=file)
                subprocess.run(command, shell=True)
                time.sleep(0.05)
            raw=result
            pkg_stack=newpkg_stack.copy()
        if result < raw:
            text_box.insert(tk.END, "小程序包消失，监听结束\n")
            end_listen()
        time.sleep(0.2)
def end_listen():
    global listening
    listening = False
    text_box.insert(tk.END, "End listening...\n")
    print("End listen!")
def listen():
    global count
    if count==0:
        count=1
        start_listen()
    else:
        count=0
        end_listen()

def Auto():
    file=file_entry.get()
    files = [f for f in os.listdir(file) if os.path.isfile(os.path.join(file, f))]
    matching_files = [f for f in files if f.endswith(".wxapkg")]
    for f in matching_files:
        unpacker_path = r"D:\wechatunpacker\bingo.bat"
        address=os.path.join(file, f)
        command = f'{unpacker_path} {shlex.quote(address)}'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"文件 {file} 解包成功")
            print(result.stdout)
        else:
            print(f"文件 {file} 解包失败")
            print(result.stderr)
listen_btn = tk.Button(root, text="监听", command=listen, **button_style)
listen_btn.grid(row=7, column=0, pady=10)
# 解包方法
# D:\wechatunpacker\bingo.bat .wxapkg
auto_btn= tk.Button(root, text="自动获取解包", command=clear_text_box, **button_style)
auto_btn.grid(row=8, column=0, pady=10)

root.mainloop()
