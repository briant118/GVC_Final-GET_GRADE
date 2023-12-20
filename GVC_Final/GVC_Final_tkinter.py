import mysql.connector
import cv2
import face_recognition
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import ssl
import tkinter as tk
from PIL import Image, ImageTk


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GET GRADE")

        self.video_frame = tk.Label(root)
        self.video_frame.pack(padx=10, pady=10)

        # For capturing camera feed using OpenCV (cv2)
        self.camera = cv2.VideoCapture(0)
        self.update_camera()

        self.frame = tk.Frame(root)
        self.frame.pack()

        self.user_info_frame = tk.LabelFrame(self.frame, text="User Information", font=("Times New Roman", 20))
        self.user_info_frame.grid(row=0, column=0, padx=0, pady=0)

        self.Full_name = tk.Label(self.user_info_frame, text="Full Name:", font=("Times New Roman", 15))
        self.Full_name.grid(row=0, column=4, sticky='e')  

        self.ID = tk.Label(self.user_info_frame, text="Enter ID:", font=("Times New Roman", 15))
        self.ID.grid(row=1, column=4, sticky='e')  

        self.Full_name_entry = tk.Entry(self.user_info_frame, font=("Times New Roman", 15))
        self.Full_name_entry.grid(row=0, column=5, sticky='w')  

        self.ID_entry = tk.Entry(self.user_info_frame, font=("Times New Roman", 15))
        self.ID_entry.grid(row=1, column=5, sticky='w')  # Align left

        self.user_info_button = tk.LabelFrame(self.frame)
        self.user_info_button.grid(row=1, column=0, padx=25, pady=25)

        self.button = tk.Button(self.user_info_button, text="Enter Data", command=self.capture_image, font=("Times New Roman", 15))
        self.button.grid(row=0, column=0, sticky="news")

        for widget in self.user_info_frame.winfo_children():
            widget.grid(padx=10, pady=5)

    def update_camera(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = img
            self.video_frame.configure(image=img)
        self.root.after(10, self.update_camera)

    def capture_image(self):
        filenm = self.Full_name_entry.get()
        student_id = self.ID_entry.get()
        if filenm == "":
            tk.messagebox.showwarning(title="GVC", message="Enter Fullname")
        elif student_id == "":
            tk.messagebox.showwarning(title="GVC", message="Enter I'D ")
        else:
            ret, frame = self.camera.read()
            if ret:
                save_folder = "GVC_Final/Students_Picture"
                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)
                checking = os.path.join(save_folder, f"{filenm}.png")
                cv2.imwrite(checking, frame)
                test_image = face_recognition.load_image_file(checking)
                rgb_test_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_test_image)

                if len(face_locations) > 0:
                    self.send_email(filenm, student_id, save_folder)
                else:
                    tk.messagebox.showwarning(title="GVC", message="No student profile record!")



    def send_email(self, filenm, student_id, save_folder):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="202280287PSU",
            database="gvc"
        )
        mycursor = mydb.cursor()

        smtp_port = 587
        smtp_server = "smtp.gmail.com"
        email_from = "icsy200325@gmail.com"
        pswd = "ksgw zpqk easf uhhd"

        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['Subject'] = "Student Information"

        sql_query = """SELECT GVC, Elective1, Elective2, DSA, email, name 
                       FROM students WHERE students_ID = %s"""
        mycursor.execute(sql_query, (student_id,))
        student_result = mycursor.fetchone()

        if student_result:
            message = f"Name: {student_result[5]}\nID: {student_id}\n"
            message += f"GVC: {student_result[0]}, Elective1: {student_result[1]}, "
            message += f"Elective2: {student_result[2]}, DSA: {student_result[3]}"
            msg.attach(MIMEText(message, 'plain'))

            with open(os.path.join(save_folder, filenm + '.png'), 'rb') as attachment:
                attachment_package = MIMEBase('application', 'octet-stream')
                attachment_package.set_payload(attachment.read())
                encoders.encode_base64(attachment_package)
                attachment_package.add_header('Content-Disposition', f"attachment; filename= {filenm}.png")
                msg.attach(attachment_package)

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(email_from, pswd)
                server.sendmail(email_from, student_result[4], msg.as_string())
                tk.messagebox.showinfo(title="GVC", message=f"Student record sent to: {student_result[4]}")
        else:
            tk.messagebox.showwarning(title="GVC", message=f"No record found for Student ID {student_id}")
            

def main():
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
