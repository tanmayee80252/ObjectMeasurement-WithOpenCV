# utlis.py
import cv2
import numpy as np


def getContours(img, cThr=[100, 100], showCanny=False, minArea=1000, filter=0, draw=False):
    """
    Finds contours in a preprocessed image and returns the image and a list of
    filtered contours sorted by area. Each entry: [num_points, area, approx, bbox, contour]
    """
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgCanny = cv2.Canny(imgBlur, cThr[0], cThr[1])
    kernel = np.ones((5, 5), np.uint8)
    imgDial = cv2.dilate(imgCanny, kernel, iterations=3)
    imgThre = cv2.erode(imgDial, kernel, iterations=2)

    if showCanny:
        cv2.imshow('Canny', imgThre)

    contours, hierarchy = cv2.findContours(imgThre, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    finalContours = []

    for i in contours:
        area = cv2.contourArea(i)
        if area > minArea:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            bbox = cv2.boundingRect(approx)

            if filter > 0:
                if len(approx) == filter:
                    finalContours.append([len(approx), area, approx, bbox, i])
            else:
                finalContours.append([len(approx), area, approx, bbox, i])

    # sort by area descending
    finalContours = sorted(finalContours, key=lambda x: x[1], reverse=True)

    if draw:
        for con in finalContours:
            cv2.drawContours(img, con[4], -1, (0, 0, 255), 3)

    return img, finalContours


def reorder(myPoints):
    """
    Reorders a set of 4 points to [top-left, top-right, bottom-left, bottom-right].
    Input shapes accepted: (4,1,2) or (4,2).
    """
    myPointsNew = np.zeros_like(myPoints)
    pts = myPoints.reshape((4, 2))
    add = pts.sum(1)
    myPointsNew[0] = pts[np.argmin(add)]   # top-left (smallest sum)
    myPointsNew[3] = pts[np.argmax(add)]   # bottom-right (largest sum)
    diff = np.diff(pts, axis=1)
    myPointsNew[1] = pts[np.argmin(diff)]  # top-right (smallest diff)
    myPointsNew[2] = pts[np.argmax(diff)]  # bottom-left (largest diff)
    return myPointsNew


def warpImg(img, points, w, h, pad=20):
    """
    Applies a perspective transform to warp the region defined by `points`
    to a rectangle of size (w, h). Optionally crops `pad` pixels from edges.
    """
    points = reorder(points)
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWarp = cv2.warpPerspective(img, matrix, (w, h))
    if pad > 0:
        imgWarp = imgWarp[pad:imgWarp.shape[0] - pad, pad:imgWarp.shape[1] - pad]
    return imgWarp


def findDis(pts1, pts2):
    """
    Euclidean distance between two points (x,y). Accepts lists, tuples or numpy arrays.
    """
    x1, y1 = int(pts1[0]), int(pts1[1])
    x2, y2 = int(pts2[0]), int(pts2[1])
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
