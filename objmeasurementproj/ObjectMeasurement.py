import cv2
import utlis

###################################
webcam = True
path = '1.jpg'  # used when webcam=False
cap = cv2.VideoCapture(0)
cap.set(10, 160)    # brightness
cap.set(3, 1920)    # width
cap.set(4, 1080)    # height
scale = 3
wP = 210 * scale    # A4 paper width in mm * scale (used as reference)
hP = 297 * scale    # A4 paper height in mm * scale
###################################

if not cap.isOpened() and webcam:
    print('Warning: webcam not available, switching to image mode')
    webcam = False

try:
    while True:
        if webcam:
            success, img = cap.read()
            if not success:
                print('Failed to grab frame from webcam')
                break
        else:
            img = cv2.imread(path)
            if img is None:
                print(f'Image at {path} not found')
                break

        imgContours, conts = utlis.getContours(img, minArea=50000, filter=4)
        if len(conts) != 0:
            biggest = conts[0][2]
            imgWarp = utlis.warpImg(img, biggest, wP, hP)

            imgContours2, conts2 = utlis.getContours(
                imgWarp, minArea=2000, filter=4, cThr=[50, 50], draw=False
            )
            if len(conts2) != 0:
                for obj in conts2:
                    cv2.polylines(imgContours2, [obj[2]], True, (0, 255, 0), 2)
                    nPoints = utlis.reorder(obj[2])

                    # compute width and height in px
                    pxW = utlis.findDis(nPoints[0][0], nPoints[1][0])
                    pxH = utlis.findDis(nPoints[0][0], nPoints[2][0])

                    # convert to cm (approx): divide by scale (since warp used mm*scale) then /10
                    nW = round((pxW / scale) / 10, 1)
                    nH = round((pxH / scale) / 10, 1)

                    # draw arrows and text
                    cv2.arrowedLine(
                        imgContours2,
                        (nPoints[0][0][0], nPoints[0][0][1]),
                        (nPoints[1][0][0], nPoints[1][0][1]),
                        (255, 0, 255),
                        3,
                        8,
                        0,
                        0.05,
                    )
                    cv2.arrowedLine(
                        imgContours2,
                        (nPoints[0][0][0], nPoints[0][0][1]),
                        (nPoints[2][0][0], nPoints[2][0][1]),
                        (255, 0, 255),
                        3,
                        8,
                        0,
                        0.05,
                    )

                    x, y, w, h = obj[3]
                    cv2.putText(
                        imgContours2,
                        f'{nW}cm',
                        (x + 30, y - 10),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        1.5,
                        (255, 0, 255),
                        2,
                    )
                    cv2.putText(
                        imgContours2,
                        f'{nH}cm',
                        (x - 70, y + h // 2),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL,
                        1.5,
                        (255, 0, 255),
                        2,
                    )

            cv2.imshow('A4', imgContours2)

        imgSmall = cv2.resize(img, (0, 0), None, 0.5, 0.5)
        cv2.imshow('Original', imgSmall)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

finally:
    # cleanup
    if webcam and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
