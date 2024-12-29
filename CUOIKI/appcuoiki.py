import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMainWindow, QStackedWidget, QFileDialog
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtGui import QPixmap, QImage
import cv2
import face_recognition
from datetime import datetime, timedelta
from sympy import symbols, integrate, limit, sympify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Ảnh đầu vào để nhận diện
user_image = face_recognition.load_image_file("person1.jpg")  # Thay đổi thành đường dẫn hình ảnh của bạn
user_face_encoding = face_recognition.face_encodings(user_image)[0]

class StartScreen(QWidget):
    def __init__(self, unlock_function, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        # Hiển thị thời gian ngày tháng
        self.time_label = QLabel(self)
        self.update_time()
        layout.addWidget(self.time_label)
        self.setLayout(layout)
        # Timer để cập nhật thời gian mỗi giây
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
    def update_time(self):
        current_time = QDateTime.currentDateTime()
        formatted_time = current_time.toString("hh:mm:ss - dddd, MMMM d, yyyy")
        self.time_label.setText(formatted_time)

class FaceUnlockApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Mở khóa màn hình"
        self.code = "1234"
        self.entered_code = ""
        self.face_unlock_enabled = False
        self.recognized_person = "Không xác định"
        self.failed_attempts = 0
        self.lockout_time = None
        self.face_unlock_delay = 5  # Đợi 5 giây trước khi quay lại giao diện mặc định
        self.face_unlock_timer = QTimer(self)
        self.is_unlocked = False  # Thêm biến theo dõi trạng thái mở khóa
        self.start_screen = StartScreen(self.show_unlock_interface)
        self.initUI()
        
    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.start_screen)

        # Sử dụng CSS để thay đổi màu sắc cho các thành phần giao diện
        self.message_label = QLabel("Nhập mã hoặc dùng mở khóa bằng khuôn mặt", self)
        self.message_label.setStyleSheet("color: blue; font-size: 16px;")
        layout.addWidget(self.message_label)

        self.code_input = QLineEdit(self)
        self.code_input.setPlaceholderText("Nhập mật khẩu")
        self.code_input.setStyleSheet("background-color: white; font-size: 16px;")
        layout.addWidget(self.code_input)

        code_button = QPushButton("Nhập mật khẩu", self)
        code_button.setStyleSheet("background-color: white; color: black; font-size: 16px;")
        code_button.clicked.connect(self.unlock_with_code)
        layout.addWidget(code_button)

        face_unlock_button = QPushButton("Chuyển đổi mở khóa khuôn mặt", self)
        face_unlock_button.setStyleSheet("background-color: white; color: black; font-size: 16px;")
        face_unlock_button.clicked.connect(self.toggle_face_unlock)
        layout.addWidget(face_unlock_button)

        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        self.info_label = QLabel(self)
        self.info_label.setStyleSheet("color: red; font-size: 16px;")
        layout.addWidget(self.info_label)

        self.central_widget.setLayout(layout)

        self.cap = cv2.VideoCapture(0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera_image)
        self.timer.start(33)  # Đặt thời gian quét ảnh thành 33ms (tương đương với khoảng 30 khung hình mỗi giây)

        self.face_unlock_timer.timeout.connect(self.return_to_default_interface)

        # Tạo một stacked widget để chứa các giao diện
        self.stacked_widget = QStackedWidget()
        self.central_widget.layout().addWidget(self.stacked_widget)

        self.central_widget.setLayout(layout)
        # Thêm giao diện mặc định (giao diện mở khóa)
        self.add_unlock_interface()

        # Thêm giao diện tính toán (giao diện thứ 2)
        self.add_calculation_interface()
    def show_unlock_interface(self):
        self.stacked_widget.setCurrentIndex(0)
        
    def add_unlock_interface(self):
        unlock_widget = QWidget()
        unlock_layout = QVBoxLayout()

        unlock_layout.addWidget(self.message_label)
        unlock_layout.addWidget(self.code_input)
        unlock_layout.addWidget(self.image_label)
        unlock_layout.addWidget(self.info_label)

        unlock_widget.setLayout(unlock_layout)
        self.stacked_widget.addWidget(unlock_widget)

    def add_calculation_interface(self):
        calculation_widget = QWidget()
        calculation_layout = QVBoxLayout()

        self.math_function_input = QLineEdit(self)
        self.math_function_input.setPlaceholderText("Nhập hàm cần tính toán")
        self.math_function_input.setStyleSheet("background-color: white; font-size: 16px;")
        calculation_layout.addWidget(self.math_function_input)

        integrate_button = QPushButton("Tính nguyên hàm", self)
        integrate_button.setStyleSheet("background-color: white; color: black; font-size: 16px;")
        integrate_button.clicked.connect(self.calculate_integral)
        calculation_layout.addWidget(integrate_button)

        definite_integral_button = QPushButton("Tính tích phân", self)
        definite_integral_button.setStyleSheet("background-color: white; color: black; font-size: 16px;")
        definite_integral_button.clicked.connect(self.calculate_definite_integral)
        calculation_layout.addWidget(definite_integral_button)

        self.lower_bound_input = QLineEdit(self)
        self.lower_bound_input.setPlaceholderText("Nhập giá trị biên dưới")
        self.lower_bound_input.setStyleSheet("background-color: white; font-size: 16px;")
        calculation_layout.addWidget(self.lower_bound_input)

        self.upper_bound_input = QLineEdit(self)
        self.upper_bound_input.setPlaceholderText("Nhập giá trị biên trên")
        self.upper_bound_input.setStyleSheet("background-color: white; font-size: 16px;")
        calculation_layout.addWidget(self.upper_bound_input)

        limit_button = QPushButton("Tính giới hạn", self)
        limit_button.setStyleSheet("background-color: white; color: black; font-size: 16px;")
        limit_button.clicked.connect(self.calculate_limit)
        calculation_layout.addWidget(limit_button)

        self.limit_value_input = QLineEdit(self)
        self.limit_value_input.setPlaceholderText("Nhập giá trị tiến tới")
        self.limit_value_input.setStyleSheet("background-color: white; font-size: 16px;")
        calculation_layout.addWidget(self.limit_value_input)
        
        calculation_layout.addWidget(self.math_function_input)

        plot_button = QPushButton("Vẽ đồ thị", self)
        plot_button.setStyleSheet("background-color: white; color: black; font-size: 16px;")
        plot_button.clicked.connect(self.plot_math_function_on_ui)
        calculation_layout.addWidget(plot_button)

        save_graph_button = QPushButton("Lưu Đồ Thị", self)
        save_graph_button.setStyleSheet("background-color: white; color: black; font-size: 16px;")
        save_graph_button.clicked.connect(self.save_current_plot)
        calculation_layout.addWidget(save_graph_button)


        self.result_label = QLabel("", self)
        self.result_label.setStyleSheet("color: green; font-size: 16px;")
        calculation_layout.addWidget(self.result_label)

        calculation_widget.setLayout(calculation_layout)
        self.stacked_widget.addWidget(calculation_widget)

        self.calculation_history = []  # Lưu trữ lịch sử tính toán

        # Vô hiệu hóa nút 'Nhập mật khẩu' khi đang ở trong giao diện tính toán
        unlock_widget = self.stacked_widget.widget(0)  # Lấy giao diện mở khóa từ stacked widget
        code_button = unlock_widget.findChild(QPushButton, "Nhập mật khẩu")
        face_unlock_button = unlock_widget.findChild(QPushButton, "Chuyển đổi mở khóa khuôn mặt")
        
        calculation_widget = self.stacked_widget.widget(1)  # Lấy giao diện tính toán từ stacked widget
        if code_button and calculation_widget: 
            code_button.setDisabled(True)  # Vô hiệu hóa nút 'Nhập mật khẩu'
            face_unlock_button.setDisabled(True) # Vô hiệu hóa nút mở bằng face

    def unlock_with_code(self):
        if self.face_unlock_enabled:
            self.message_label.setText(
                "Mở khóa khuôn mặt đang được bật. Vui lòng dùng khuôn mặt để mở khóa.")
        else:
            if self.lockout_time is not None and datetime.now() < self.lockout_time:
                remaining_time = self.lockout_time - datetime.now()
                self.message_label.setText(f"Thử lại sau {remaining_time.seconds} giây.")
            else:
                if self.code_input.text() == self.code:
                    self.is_unlocked = True  # Đặt trạng thái mở khóa thành True
                    self.message_label.setText("Mở khóa thành công!")

                    # Chuyển đến giao diện tính toán
                    QTimer.singleShot(3000, self.show_unlock_success_message)     
                else:
                    self.failed_attempts += 1
                    if self.failed_attempts >= 5:
                        self.lockout_time = datetime.now() + timedelta(minutes=1)  # Khóa trong 1 phút
                    self.message_label.setText("Mở khóa thất bại! Vui lòng thử lại.")
                self.code_input.clear()
    def show_unlock_success_message(self):
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss - dddd, MMMM d, yyyy")
        success_message = f"Đã Truy nhập thành công vào lúc {current_time}"
        self.stacked_widget.setCurrentIndex(1)  # Move to the calculation interface
        self.result_label.setText(success_message)  

    def toggle_face_unlock(self):
        if self.face_unlock_timer.isActive():
            self.face_unlock_timer.stop()
        if self.face_unlock_enabled:
            self.message_label.setText("Nhập mã hoặc mở bằng khuôn mặt")
        else:
            self.message_label.setText("Mở khóa bằng khuôn mặt đang được bật.")
            self.is_unlocked = True

            self.face_unlock_timer.start(self.face_unlock_delay * 1000)

        self.face_unlock_enabled = not self.face_unlock_enabled

    def update_camera_image(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                if self.face_unlock_enabled:
                    face_locations = face_recognition.face_locations(frame)
                    face_encodings = face_recognition.face_encodings(frame, face_locations)
                    self.recognized_person = "Không xác định được"
                    for face_encoding in face_encodings:
                        matches = face_recognition.compare_faces([user_face_encoding], face_encoding)
                        if True in matches:
                            self.recognized_person = "User: Quang Dũng "
                            self.message_label.setText("Mở khóa thành công!")
                        
                            self.face_unlock_success_time = QDateTime.currentDateTime().toString("hh:mm:ss - dddd, MMMM d, yyyy")
                            

                            

                            # Chuyển đến giao diện tính toán
                            QTimer.singleShot(3000, lambda: self.stacked_widget.setCurrentIndex(1))

                            if self.face_unlock_timer.isActive():
                                self.face_unlock_timer.stop()
                            break

                height, width, channel = frame.shape
                bytesPerLine = 3 * width
                qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

                pixmap = QPixmap.fromImage(qImg)
                self.image_label.setPixmap(pixmap)

                # Cập nhật thông tin người được công nhận
                self.info_label.setText(self.recognized_person)

        if not self.is_unlocked:  # Kiểm tra nếu chưa mở khóa
            self.math_function_input.clear()  # Xóa nội dung nhập liệu
            self.math_function_input.setDisabled(True)  # Vô hiệu hóa ô nhập liệu
        else:
            self.math_function_input.setEnabled(True)

    def return_to_default_interface(self):
        self.is_unlocked = False
        self.face_unlock_enabled = False
        self.message_label.setText("Nhập mã hoặc dùng mở bằng khuôn mặt")
        self.face_unlock_timer.stop()
        self.face_unlock_success_time = None
        # Chuyển về giao diện mặc định
        self.stacked_widget.setCurrentIndex(0)

    def closeEvent(self, event):
        self.cap.release()
        super(FaceUnlockApp, self).closeEvent(event)

    def calculate_integral(self):
        if not self.is_unlocked:
            self.result_label.setText("Vui lòng mở khóa trước khi tính toán.")
            return
        math_function = self.math_function_input.text()
    # Kiểm tra nếu không có biểu thức để tính toán
        if not math_function:
            self.result_label.setText("Vui lòng nhập biểu thức để tính nguyên hàm.")
            return
        x = symbols('x')
        try:
            integral_result = integrate(eval(math_function), x)
            self.result_label.setText(f"Nguyên hàm của {math_function} là: {integral_result}")
            self.calculation_history.append(f"Nguyên hàm của {math_function} là: {integral_result}")
        except Exception as e:
            self.result_label.setText(f"Lỗi khi tính nguyên hàm: {e}")

    def calculate_definite_integral(self):
        if not self.is_unlocked:
            self.result_label.setText("Vui lòng mở khóa trước khi tính toán.")
            return
        math_function = self.math_function_input.text()
        lower_bound_input = self.lower_bound_input.text()
        upper_bound_input = self.upper_bound_input.text()
    # Kiểm tra nếu không có giá trị đủ để tính toán
        if not lower_bound_input or not upper_bound_input:
            self.result_label.setText("Vui lòng nhập giá trị biên trước khi tính toán.")
            return
        lower_bound_input = float(lower_bound_input)  # Chuyển đổi giá trị thành số
        upper_bound_input = float(upper_bound_input)  # Chuyển đổi giá trị thành số
        
        x = symbols('x')
        try:
            expr = sympify(math_function)  # Phân tích cú pháp biểu thức toán học
            integral_result = integrate(expr, (x, lower_bound_input, upper_bound_input))
            self.result_label.setText(f"Tích phân của {math_function} từ {lower_bound_input} đến {upper_bound_input} là: {integral_result}")
            self.calculation_history.append(f"Tích phân của {math_function} từ {lower_bound_input} đến {upper_bound_input} là: {integral_result}")
        except Exception as e:
            self.result_label.setText(f"Lỗi khi tính tích phân: {e}")

    def calculate_limit(self):
        if not self.is_unlocked:
            self.result_label.setText("Vui lòng mở khóa trước khi tính toán.")
            return
        math_function = self.math_function_input.text()
        limit_value_input = self.limit_value_input.text()
    # Kiểm tra nếu không có giá trị đủ để tính toán
        if not limit_value_input:
            self.result_label.setText("Vui lòng nhập giá trị tiến tới trước khi tính toán.")
            return
        try:
            limit_value_input = float(limit_value_input)  # Chuyển đổi giá trị thành số
        except ValueError:
            self.result_label.setText("Giá trị tiến tới không hợp lệ. Vui lòng nhập số.")
            return
        x = symbols('x')
        try:
            expr = sympify(math_function)  # Phân tích cú pháp biểu thức toán học
            limit_result = limit(expr, x, limit_value_input)
            self.result_label.setText(f"Giới hạn của {math_function} khi x tiến tới {limit_value_input} là: {limit_result}")
            self.calculation_history.append(f"Giới hạn của {math_function} khi x tiến tới {limit_value_input} là: {limit_result}")
        except Exception as e:
            self.result_label.setText(f"Lỗi khi tính giới hạn: {e}")

    def calculate_math_function(self):
        if not self.is_unlocked:
            self.result_label.setText("Vui lòng mở khóa trước khi tính toán.")
            return

        math_function = self.math_function_input.text()
        x = symbols('x')
        try:
            expr = sympify(math_function)  # Phân tích cú pháp biểu thức toán học
            result = expr.subs(x, 2)  # Thay x bằng 2 để tính toán kết quả
        except Exception as e:
            self.result_label.setText(f"Lỗi: {e}")
    def plot_math_function_on_ui(self):
        try:
            self.plot_math_function()
        except Exception as e:
            self.result_label.setText(f"Lỗi khi vẽ đồ thị: {e}")

    def plot_math_function(self, plot_filename=None):
        try:
            math_function = self.math_function_input.text()
            x = symbols('x')
            expr = sympify(math_function)
        
            x_vals = range(-10, 11)
            y_vals = [expr.subs(x, val) for val in x_vals]

            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals)
            ax.set_title('Đồ thị hàm số', self.math_function_input)
            ax.set_xlabel('x')
            ax.set_ylabel('y')

            if plot_filename:
                plt.savefig(plot_filename)  
                self.result_label.setText("Lưu đồ thị thành công!")
                return None
            else:
                self.result_label.setText("Không thể lưu đồ thị.")     
            plt.show()
            return fig
        except Exception as e:
            self.result_label.setText(f"Lỗi khi tạo đồ thị: {e}")
            return None

    def show_plot_window(self, plot):
        plot_window = QMainWindow()
        central_widget = QWidget()
        plot_window.setCentralWidget(central_widget)
    
        layout = QVBoxLayout()
        canvas = FigureCanvas(plot.figure)
        layout.addWidget(canvas)
        central_widget.setLayout(layout)
    
        plot_window.setWindowTitle("Đồ thị hàm số", )
        plot_window.show()

    def save_current_plot(self):
        try:
            figure = self.plot_math_function(plot_filename=None)
            if figure:
                file_name, _ = QFileDialog.getSaveFileName(
                    self, "Save Graph", "", "Images (*.png);;All Files (*)")
                if file_name:
                    figure.savefig(file_name)
                    self.result_label.setText("Lưu đồ thị thành công!")
                else:
                    self.result_label.setText("Không chọn file lưu.")
            else:
                self.result_label.setText("Không thể lưu đồ thị.")
        except Exception as e:
            self.result_label.setText(f"Lỗi khi lưu đồ thị: {e}")
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    unlock_app = FaceUnlockApp()
    unlock_app.setWindowTitle(unlock_app.title)
    unlock_app.show()
    sys.exit(app.exec_())
