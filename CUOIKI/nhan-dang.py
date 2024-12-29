
import cv2
import face_recognition

imgElon = face_recognition.load_image_file("elon musk.jpg")
imgElon =cv2.cvtColor(imgElon,cv2.COLOR_BGR2RGB)
imgCheck = face_recognition.load_image_file("elon check.jpg")
imgCheck =cv2.cvtColor(imgCheck,cv2.COLOR_BGR2RGB)


faceloc = face_recognition.face_locations(imgElon)[0]
print(faceloc)
encodeElon = face_recognition.face_encodings(imgElon)[0] # tạo mã hóa khuôn mặt từ vị trí xác định
cv2.rectangle(imgElon,(faceloc[3],faceloc[0]),(faceloc[1],faceloc[2]),(255,0,255),2)

faceCheck = face_recognition.face_locations(imgCheck)[0]
encodeCheck = face_recognition.face_encodings(imgCheck)[0]
cv2.rectangle(imgCheck,(faceCheck[3],faceCheck[0]),(faceCheck[1],faceCheck[2]),(255,0,255),2)


results = face_recognition.compare_faces([encodeElon],encodeCheck) #mã hóa 2 khuon mat
print(results)


faceDis = face_recognition.face_distance([encodeElon],encodeCheck) #tính khoảng cách giữa các khuôn mặt
print(results,faceDis)

cv2.putText(imgCheck,f"{results}{(round(faceDis[0],2))}",(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)

cv2.imshow("Elon",imgElon)
cv2.imshow("Check",imgCheck)
cv2.waitKey()
cv2.destroyAllWindows()
