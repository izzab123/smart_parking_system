import qrcode

def generate_qr():
    car = "ABC-123"
    img = qrcode.make(car)
    img.save("car_qr.png")
    print("QR Created")

generate_qr()