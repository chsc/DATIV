//
// RPi Test
// Author: Christoph Schunk
//

#include <iostream>
#include <fstream>
#include <opencv2/imgproc.hpp>
#include <opencv2/calib3d.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/core.hpp>

void writeParameters(int minWidth, int maxWidth, int minHeight, int maxHeight)
{
    cv::FileStorage fs("config.json", cv::FileStorage::FORMAT_JSON | cv::FileStorage::WRITE);

    fs << "config";
    fs << "{";
    fs << "minWidth" << minWidth;
    fs << "maxWidth" << maxWidth;
    fs << "minHeight" << minHeight;
    fs << "maxHeight" << maxHeight;
    fs << "}";

    fs.release();
}

bool readParameters(int &minWidth, int &maxWidth, int &minHeight, int &maxHeight,
                    float &boardSquareWidth, float &boardSquareHeight)
{
    cv::FileStorage fs("config.json", cv::FileStorage::FORMAT_JSON | cv::FileStorage::READ);

    cv::FileNode cfg = fs["config"];
    if(cfg.type() != cv::FileNode::MAP) {
        return false;
    }
    cfg["minWidth"] >> minWidth;
    cfg["maxWidth"] >> maxWidth;
    cfg["minHeight"] >> minHeight;
    cfg["maxHeight"] >> maxHeight;

    cfg["boardSquareWidth"] >> boardSquareWidth;
    cfg["boardSquareHeight"] >> boardSquareHeight;

    fs.release();

    return true;
}

int main()
{
    std::cout << "Reading ...\n";

    cv::Mat image = cv::imread("test.png");
    cv::imshow("Test", image);

    cv::waitKey(-1);

    return 0;
}


