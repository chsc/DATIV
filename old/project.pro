CONFIG   += debug_and_release
CONFIG   += console
CONFIG   += c++17
CONFIG   -= qt
QT       -= core gui
TARGET   = rpi_camera
TEMPLATE = app

win32-msvc* {
    COMPILER = "win32-msvc"
}
win32-g++ {
    COMPILER = "win32-gcc"
}
linux-g++ {
    COMPILER = "linux-gcc"
}

CONFIG(debug, debug|release) {
    DESTDIR = ../build/$${COMPILER}/debug
} else {
    DESTDIR = ../build/$${COMPILER}/release
}

win32-g++ {
    LIBS += D:\thirdparty\OpenCV-MinGW-Build-OpenCV-4.1.1-x64\x64\mingw\lib\libopencv_videoio411.dll.a
    LIBS += D:\thirdparty\OpenCV-MinGW-Build-OpenCV-4.1.1-x64\x64\mingw\lib\libopencv_calib3d411.dll.a
    LIBS += D:\thirdparty\OpenCV-MinGW-Build-OpenCV-4.1.1-x64\x64\mingw\lib\libopencv_imgcodecs411.dll.a
    LIBS += D:\thirdparty\OpenCV-MinGW-Build-OpenCV-4.1.1-x64\x64\mingw\lib\libopencv_imgproc411.dll.a
    LIBS += D:\thirdparty\OpenCV-MinGW-Build-OpenCV-4.1.1-x64\x64\mingw\lib\libopencv_core411.dll.a
    LIBS += D:\thirdparty\OpenCV-MinGW-Build-OpenCV-4.1.1-x64\x64\mingw\lib\libopencv_highgui411.dll.a

    INCLUDEPATH += D:\thirdparty\OpenCV-MinGW-Build-OpenCV-4.1.1-x64\include
}

linux-g++ {
    LIBS += -lopencv_videoio
    LIBS += -lopencv_calib3d
    LIBS += -lopencv_imgcodecs
    LIBS += -lopencv_imgproc
    LIBS += -lopencv_core
    LIBS += -lopencv_highgui

    INCLUDEPATH += /usr/include/opencv4
}

INCLUDEPATH += ..

SOURCES += main.cpp

OTHER_FILES +=

HEADERS +=

